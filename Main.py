from Iteration import *
from Packages import *
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
    def __init__(self,prompt,filename,
                 TemplateCode='''
import bpy

# Clear existing mesh objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Create a new cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
cube = bpy.context.object

# Add a point light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 5))
light = bpy.context.object
light.data.energy = 1000  # Set the light strength

# Set the number of frames for the animation
start_frame = 1
end_frame = 200
bpy.context.scene.frame_start = start_frame
bpy.context.scene.frame_end = end_frame

# Insert keyframes for the cube's location
cube.location.x = -5  # Starting position
cube.keyframe_insert(data_path="location", frame=start_frame)

cube.location.x = 5  # Ending position
cube.keyframe_insert(data_path="location", frame=end_frame)

# Insert keyframes for the camera's location
camera = bpy.data.cameras.new("Camera")
camera_object = bpy.data.objects.new("Camera", camera)
bpy.context.scene.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object

# Set the camera's initial position
camera_object.location = (-5, -10, 5)
camera_object.rotation_euler = (1.1, 0, 0)  # Point down at the cube

# Insert keyframes for the camera's location
camera_object.keyframe_insert(data_path="location", frame=start_frame)
camera_object.location.x = 5  # Move camera with the cube
camera_object.keyframe_insert(data_path="location", frame=end_frame)

# Ensure all objects are baked for animation
bpy.context.view_layer.objects.active = cube
bpy.ops.nla.bake(frame_start=start_frame, frame_end=end_frame, 
                 visual_keying=True, clear_constraints=True, 
                 bake_types={'POSE', 'OBJECT'})

bpy.context.view_layer.objects.active = camera_object
bpy.ops.nla.bake(frame_start=start_frame, frame_end=end_frame, 
                 visual_keying=True, clear_constraints=True, 
                 bake_types={'POSE', 'OBJECT'})

# Set render output settings

bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'

'''):
        #in future iterations we should enable specifying specific chatgpt versions
        #I excluded that from this iteration as people might type in the wrong version and get an error
        #this is the original prompt
        self.prompt=prompt
        self.json_file={"Prompt":self.prompt}
        self.TemplateCode=TemplateCode
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
    def ErrorLog(self,ExtractedCode):
        FolderName=self.filename[:-5]
        SubFolder=MassUpload(FolderName,ParentID='19GkT7pQw6Nl0IAGqPfwOBy_N22RDDQIR')
        SubFolderID=SubFolder.create_subfolder()
        self.json_file['elapsed_time'] = 'Unknown'
        self.json_file['Code'] = ExtractedCode
        prompt_file = f"{FolderName}.json"
        with open(prompt_file, "w") as file:
            # Write some text to the file
            json.dump(AnimationInstance.json_file, file, indent=4)
        fileupload = UploadFile(prompt_file)
        fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
        print('Killing File')
    def chat_with_LLM(self, text_prompt,Kill_Function=0):
        if Kill_Function == 4:
            #At the 4th iteration the text prompt will be the code
            self.ErrorLog(text_prompt)
            print('Max Number of OpenAI Calls reached. Consider adjusting prompt or code')
            sys.exit(1)
        try:

            # Send request to OpenAI's API
            response = openai.ChatCompletion.create(
                model="o1-preview-2024-09-12",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{text_prompt}."
                            f"Use {self.TemplateCode} and APIs compatiable with blender 4.2.1 as a general template to improve the quality of the animation "
                            f"Return the code enclosed in triple backticks like ``` at both the start and end of the code section. "
                            f"Lastly, always save it as a blend file to this path {self.filename} and assume no objects or functions have been created."
                            f"Do not assign a rendering resolution and remove any assigned rendering resolution."
                            f"Do not use a main() class and avoid attribute errors"
                        ),
                    },
                ],
                max_completion_tokens=10000,

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
                        bpy.context.scene.frame_end = 200  # Adjust this to your frame range

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
            Kill_Function_Updated=Kill_Function+1
            return self.chat_with_LLM(new_prompt,Kill_Function_Updated)







# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

# Build the Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)
def GetParentFolder(subfolder_id):
    drive_service = authenticate_drive()
    # Fetch the metadata of the subfolder
    file = drive_service.files().get(fileId=subfolder_id, fields='id, name, parents').execute()

    # Check if the subfolder has a parent and print it
    if 'parents' in file:
        parent_id = file['parents'][0]
        print(f"Parent Folder ID: {parent_id}")
    else:
        print("This folder has no parent.")
    return parent_id
def GetCode(folder_id):
    drive_service = authenticate_drive()
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/json'",
        spaces='drive',
        fields="nextPageToken, files(id, name)").execute()

    items = results.get('files', [])

    if not items:
        print('No JSON files found.')
    else:
        # Assuming we are looking for the first JSON file in the folder
        json_file = items[0]
        print(f"Found JSON file: {json_file['name']} (ID: {json_file['id']})")

        # Download the JSON file content
        request = drive_service.files().get_media(fileId=json_file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        # Read the JSON content
        fh.seek(0)
        json_content = json.load(fh)
    return json_content['Code']
def authenticate_drive():
    """Authenticate using a Service Account and return the Drive service."""
    # Load the service account credentials
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=SCOPES
    )

    # Build the Google Drive service
    return build('drive', 'v3', credentials=credentials)
class UploadFile:
    def __init__(self,filename):
        self.filename=filename

    def upload_file_to_drive(self, file_name, file_path, mime_type, ParentID):
        """Upload a file to Google Drive using the authenticated service."""
        drive_service = authenticate_drive()

        # File metadata to specify the file name and folder (optional)
        file_metadata = {
            'name': file_name,
            'parents': [ParentID]  # Optional: Folder ID
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
class MassUpload:
    def __init__(self,FolderName,ParentID='1VYfJiunHJ8i8JPQIN5IIp8ISr9jp7ni8'):
        self.FolderName = FolderName
        self.ParentID = ParentID
    def create_subfolder(self):
        drive_service = authenticate_drive()
        """Create a subfolder inside a parent folder on Google Drive."""
        folder_metadata = {
            'name': self.FolderName,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.ParentID]  # The ID of the parent folder
        }

        # Create the subfolder
        subfolder = drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()

        print(f"Subfolder created successfully, Subfolder ID: {subfolder.get('id')}")
        return subfolder.get('id')

if __name__=='__main__':

    Prompt=("Create me a python script for a blender animation of and object driving through a wall and shattering it. Use color.")
    # First Instance
    ParentFolder=MassUpload('Shatter Glass')
    ParentFolderID=ParentFolder.create_subfolder()
    SubFolderID_LST=[]
    for i in range (0,5):
        start_time = time.time()
        if i==0:
            AnimationInstance = animationgeneartion(Prompt,
                                                    F"{ParentFolder.FolderName}{i}.blend")
            print(AnimationInstance.prompt)
            code, ExtractedCode = AnimationInstance.chat_with_LLM(AnimationInstance.prompt)
            SubFolder = MassUpload(F"{ParentFolder.FolderName}{i}",ParentFolderID)
            SubFolderID = SubFolder.create_subfolder()
            fileupload = UploadFile(AnimationInstance.filename)
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/x-blender",
                                            SubFolderID)
            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.mp4")
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "video/mp4", SubFolderID)
            end_time = time.time()
            elasped_time = end_time - start_time

            # Upload JSON File
            AnimationInstance.json_file['elapsed_time'] = elasped_time
            AnimationInstance.json_file['Code'] = ExtractedCode
            prompt_file = F"{ParentFolder.FolderName}{i}.json"
            with open(prompt_file, "w") as file:
                # Write some text to the file
                json.dump(AnimationInstance.json_file, file, indent=4)
            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
            SubFolderID_LST.append(SubFolderID)
        elif i==1:
            FirstInstanceCode=GetCode(SubFolderID_LST[0])
            AnimationInstance = animationgeneartion(Prompt,
                                                    F"{ParentFolder.FolderName}{i}.blend",
                                                    FirstInstanceCode)
            print(AnimationInstance.prompt)
            code, ExtractedCode = AnimationInstance.chat_with_LLM(AnimationInstance.prompt)
            SubFolder = MassUpload(F"{ParentFolder.FolderName}{i}",ParentFolderID)
            SubFolderID = SubFolder.create_subfolder()
            fileupload = UploadFile(AnimationInstance.filename)
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/x-blender",
                                            SubFolderID)
            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.mp4")
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "video/mp4", SubFolderID)
            end_time = time.time()
            elasped_time = end_time - start_time

            # Upload JSON File
            AnimationInstance.json_file['elapsed_time'] = elasped_time
            AnimationInstance.json_file['Code'] = ExtractedCode
            prompt_file = F"{ParentFolder.FolderName}{i}.json"
            with open(prompt_file, "w") as file:
                # Write some text to the file
                json.dump(AnimationInstance.json_file, file, indent=4)
            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
            SubFolderID_LST.append(SubFolderID)
        else:
            InstanceOfCycle,ImprovementPlan=FullCycle(F"{ParentFolder.FolderName}{i-2}.mp4",F"{ParentFolder.FolderName}{i-1}.mp4",
                      SubFolderID_LST[i-2],SubFolderID_LST[i-1])
            PreferredCode=InstanceOfCycle.fullCycle()
            AnimationInstance = animationgeneartion(Prompt,
                                                    F"{ParentFolder.FolderName}{i}.blend",
                                                    FirstInstanceCode)
            print(AnimationInstance.prompt)
            code, ExtractedCode = AnimationInstance.chat_with_LLM(F"Here is the original Prompt {AnimationInstance.prompt}"
                                                                  F" and these are the critques {ImprovementPlan}")
            SubFolder = MassUpload(F"{ParentFolder.FolderName}{i}",ParentFolderID)
            SubFolderID = SubFolder.create_subfolder()
            fileupload = UploadFile(AnimationInstance.filename)
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/x-blender",
                                            SubFolderID)
            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.mp4")
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "video/mp4", SubFolderID)
            end_time = time.time()
            elasped_time = end_time - start_time

            # Upload JSON File
            AnimationInstance.json_file['elapsed_time'] = elasped_time
            AnimationInstance.json_file['Code'] = ExtractedCode
            prompt_file = F"{ParentFolder.FolderName}{i}.json"
            with open(prompt_file, "w") as file:
                # Write some text to the file
                json.dump(AnimationInstance.json_file, file, indent=4)
            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
            SubFolderID_LST.append(SubFolderID)
