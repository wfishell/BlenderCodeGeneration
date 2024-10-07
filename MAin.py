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
import json
import textwrap
import time
openai.api_key = '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'

import sys
import traceback


class InterpreterError(Exception): pass

class InterpreterError(Exception): pass

def my_exec(cmd, globals=None, locals=None, description='source string'):
    try:
        exec(cmd, globals, locals)
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0]
        cl, exc, tb = sys.exc_info()
        line_number = traceback.extract_tb(tb)[-1][1]
    else:
        return
    return line_number

class animationgeneartion:
    def __init__(self,prompt,filename):
        #in future iterations we should enable specifying specific chatgpt versions
        #I excluded that from this iteration as people might type in the wrong version and get an error
        #this is the original prompt
        self.prompt=prompt
        self.json_file={"Prompt":self.prompt}
        #file name that the image will be rendered too
        #this will be saved in google drive
        self.filename=filename
        # Function to extract code inside backticks (``` code ```)
    def extract_backticks_code(self,text):
        # Use regex to find all content between triple backticks (``` code ```)
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches ==[]:
            pattern = r"```(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)
        return matches

    # Define the conversation with ChatGPT
    # Define the conversation with ChatGPT
    def chat_with_gpt4(self, text_prompt):
        try:
            Camera_Object_Tracking='''
                    sc = context.space_data
                    clip = sc.clip
                    tracking = clip.tracking
        
                    camob = CLIP_OT_setup_tracking_scene._findOrCreateCamera(context)
                    cam = camob.data
        
                    # Remove all constraints to be sure motion is fine.
                    camob.constraints.clear()
        
                    # Append camera solver constraint.
                    con = camob.constraints.new(type='CAMERA_SOLVER')
                    con.use_active_clip = True
                    con.influence = 1.0
        
                    cam.sensor_width = tracking.camera.sensor_width
                    cam.lens = tracking.camera.focal_length'''

            Follow_Object_Path='''
                    camera = bpy.data.objects['Camera']
                    path = bpy.data.objects['BezierCircle']
                
                    camera.select = True
                    path.select = True
                
                    bpy.context.scene.objects.active = camera #select camera
                
                    '''


            # Send request to OpenAI's API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{text_prompt}."
                            f"Use {Camera_Object_Tracking}  to improve the quality of the animation "
                            f"Return the code enclosed in triple backticks like ``` at both the start and end of the code section. "
                            f"Lastly, always save it as a blend file to this path {self.filename} and assume no objects or functions have been created."
                            f"Do not use a main() class"
                        ),
                    },
                ],
                max_completion_tokens=1500,

            )

            # Extract the response content
            reply = response['choices'][0]['message']['content']
            code_blocks = self.extract_backticks_code(reply)

            # Check if any code block was found
            if not code_blocks:
                raise ValueError("No code block found in the response.")

            # Get the first code block
            extracted_code = code_blocks[0]
            #render image code
            #
            #path = self.filename[:-5]+'mp4'
            path=self.filename[:-5]+'mp4'
            rendercode = f"""
                        #renders images in scene
                        bpy.context.scene.render.filepath = '{path}'

                        # Set render resolution
                        bpy.context.scene.render.resolution_x = 256
                        bpy.context.scene.render.resolution_y = 256

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

            formatted_code_stage_1=textwrap.dedent(extracted_code)
            formatted_code_stage_2=textwrap.dedent(rendercode)
            formatted_code_stage_3=formatted_code_stage_1+formatted_code_stage_2
            formatted_code = autopep8.fix_code(formatted_code_stage_3)
            print(formatted_code)
            return exec(formatted_code),formatted_code

        except Exception as e:
            print(f"Error: {e}")
            Error=InterpreterError(e)
            error=str(e)
            line_number=my_exec(formatted_code)
            if error in self.json_file:
                self.json_file[error].append((formatted_code,line_number))
            else:
                self.json_file[error]=[(formatted_code,line_number)]
            print(line_number)
            # Modify the prompt to retry with additional guidance
            new_prompt = (f"{extracted_code} this was returning an error {e} at line number {line_number} can you modify this code so that it addresses this error. Ensure bpy is defined ")
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
    start_time=time.time()
    #Name File Name +Animation or Image. for example PlanetaryOrbitAnimation.blend
    testinstance=animationgeneartion("Create me a python blender script of a full scene of bunch of shapes bouncing up and down randomly",
                        'Test_GPT4.blend')
    print(testinstance.prompt)
    code,ExtractedCode=testinstance.chat_with_gpt4(testinstance.prompt)
    fileupload=UploadFile('Test_GPT4.blend')
    fileupload.upload_file_to_drive(fileupload.filename,fileupload.filename,"application/x-blender")
    fileupload = UploadFile('Test_GPT4.mp4')
    fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "video/mp4")
    end_time=time.time()
    elasped_time=end_time-start_time
    testinstance.json_file['elapsed_time']=elasped_time
    testinstance.json_file['Code']=ExtractedCode
    prompt_file='Test_GPT4.json'
    with open(prompt_file, "w") as file:
        # Write some text to the file
        json.dump(testinstance.json_file, file, indent=4)
    fileupload=UploadFile('Test_GPT4.json')
    fileupload.upload_file_to_drive(fileupload.filename,fileupload.filename,"application/json")

