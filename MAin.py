import openai
import autopep8
import re
import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import textwrap
openai.api_key = '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'
class animationgeneartion:
    def __init__(self,prompt,filename):
        #in future iterations we should enable specifying specific chatgpt versions
        #I excluded that from this iteration as people might type in the wrong version and get an error
        #this is the original prompt
        self.prompt=prompt
        #file name that the image will be rendered too
        #this will be saved in google drive
        self.filename=filename
        # Function to extract code inside backticks (``` code ```)
    def extract_backticks_code(self,text):
        # Use regex to find all content between triple backticks (``` code ```)
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    # Define the conversation with ChatGPT
    # Define the conversation with ChatGPT
    def chat_with_gpt4(self, text_prompt):
        try:
            # Send request to OpenAI's API
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # You can also use 'gpt-3.5-turbo' if you don't have access to GPT-4
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user",
                     "content": f"{text_prompt}. Ensure all objects and collections are visible in render and set camera=bpy.context.scene"
                                f" .return the code in with backticks like this ``` at the start and end of the program and format it like python. Lastly, always save it as a blend file to this path {self.filename} and assume no objects have been created and stop including the word 'python' in there unless it is part of a piece of code. "
                                f"Also always make sure bpy is defined"},
                ],
                max_tokens=1500,  # Adjust token usage depending on the length of the response
                temperature=0.7,  # Controls creativity. Lower values = more deterministic
            )

            # Extract the response content
            reply = response['choices'][0]['message']['content']

            # Extract code block between backticks
            code_blocks = self.extract_backticks_code(reply)

            # Check if any code block was found
            if not code_blocks:
                raise ValueError("No code block found in the response.")

            # Get the first code block
            extracted_code = code_blocks[0]
            #render image code
            #
            path = self.filename[:-5]+'mp4'
            rendercode = f"""
            #renders images in scene
            def set_camera_to_view_all_objects():
                # Get the active scene
                scene = bpy.context.scene
            
                # Get the camera object
                cam = scene.camera
            
                # Get the bounding box of all objects
                min_x, min_y, min_z = [float('inf')] * 3
                max_x, max_y, max_z = [float('-inf')] * 3
            
                for obj in bpy.data.objects:
                    if obj.type == 'MESH':  # Only consider mesh objects
                        for vert in obj.bound_box:
                            world_vert = obj.matrix_world @ bpy.mathutils.Vector(vert[:])
                            min_x = min(min_x, world_vert.x)
                            min_y = min(min_y, world_vert.y)
                            min_z = min(min_z, world_vert.z)
                            max_x = max(max_x, world_vert.x)
                            max_y = max(max_y, world_vert.y)
                            max_z = max(max_z, world_vert.z)
            
                # Calculate the center of the bounding box
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                center_z = (min_z + max_z) / 2
            
                # Calculate the size of the bounding box (diagonal distance)
                size_x = max_x - min_x
                size_y = max_y - min_y
                size_z = max_z - min_z
                max_size = max(size_x, size_y, size_z)
            
                # Position the camera
                cam.location = (center_x, center_y - max_size * 1.5, center_z + max_size * 0.5)
            
                # Point the camera at the center of the bounding box
                direction = bpy.mathutils.Vector((center_x, center_y, center_z)) - cam.location
                rot_quat = direction.to_track_quat('Z', 'Y')
                cam.rotation_euler = rot_quat.to_euler()
            
                # Set the camera to focus on the entire scene
                scene.view_layers.update()
            
            # Call the function
            set_camera_to_view_all_objects()

            bpy.context.scene.render.filepath = '{path}'

            # Set render resolution
            bpy.context.scene.render.resolution_x = 1920
            bpy.context.scene.render.resolution_y = 1080

            # Set frame range for the animation
            bpy.context.scene.frame_start = 1
            bpy.context.scene.frame_end = 250  # Adjust this to your frame range

            # Set the render engine (optional, 'CYCLES' or 'BLENDER_EEVEE')
            bpy.context.scene.render.engine = 'CYCLES'

            # Set the file format to FFMPEG for video
            bpy.context.scene.render.image_settings.file_format = 'FFMPEG'

            # Set the container to MPEG-4
            bpy.context.scene.render.ffmpeg.format = 'MPEG4'
            bpy.ops.render.render(animation=True)
            """

            # Format the extracted code using autopep8
            formatted_code_stage_1=textwrap.dedent(extracted_code)
            formatted_code_stage_2=textwrap.dedent(rendercode)
            formatted_code_stage_3=formatted_code_stage_1+formatted_code_stage_2
            formatted_code = autopep8.fix_code(formatted_code_stage_3)

            return exec(formatted_code)

        except Exception as e:
            print(f"Error: {e}")

            # Modify the prompt to retry with additional guidance
            print(formatted_code)
            new_prompt = (f"{formatted_code} this was returning an error {e} can you modify this code so that it addresses this error, and any indentation errors. Ensure all objects are in field of view when rendered. "
                          f"Avoid nonetype errors and to avoid bpy does not exist error.")
            print("Retrying with modified prompt...")

            # Retry the function with the new prompt
            return self.chat_with_gpt4(new_prompt)




# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

# Build the Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)
class UploadFile:
    def __init__(self,filename):
        self.filename=filename

    def authenticate_drive(self):
        """Authenticate using a Service Account and return the Drive service."""
        # Load the service account credentials
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES
        )

        # Build the Google Drive service
        return build('drive', 'v3', credentials=credentials)

    def upload_file_to_drive(self, file_name, file_path, mime_type):
        """Upload a file to Google Drive using the authenticated service."""
        drive_service = self.authenticate_drive()

        # File metadata to specify the file name and folder (optional)
        file_metadata = {
            'name': file_name,
            'parents': ['1VYfJiunHJ8i8JPQIN5IIp8ISr9jp7ni8']  # Optional: Folder ID
        }

        # MediaFileUpload handles the file to upload
        media = MediaFileUpload(file_path, mimetype=mime_type)

        # Upload the file to Google Drive
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"File uploaded successfully, File ID: {file.get('id')}")


if __name__=='__main__':
    #Name File Name +Animation or Image. for example PlanetaryOrbitAnimation.blend
    testinstance=animationgeneartion("Create me a python blender script which shows the planets orbitting around the sun",
                        'PlanetsOrbittingFixedCameraGPT4o.blend')
    print('test 4')
    print(testinstance.prompt)
    code=testinstance.chat_with_gpt4(testinstance.prompt)
    fileupload=UploadFile('PlanetsOrbittingFixedCameraGPT4o.blend')
    fileupload.upload_file_to_drive(fileupload.filename,fileupload.filename,"application/x-blender")
    fileupload = UploadFile('PlanetsOrbittingFixedCameraGPT4o.mp4')
    fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "video/mp4")
    prompt_file='PlanetsOrbittingFixedCameraGPT4o.txt'
    with open(prompt_file, "w") as file:
        # Write some text to the file
        file.write(testinstance.prompt)
    fileupload=UploadFile('PlanetsOrbittingFixedCameraGPT4o.txt')
    fileupload.upload_file_to_drive(fileupload.filename,fileupload.filename,"text/plain")

