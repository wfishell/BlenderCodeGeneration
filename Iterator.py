
from Packages import *
# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

# Build the Google Drive service
drive_service = build('drive', 'v3', credentials=credentials)
def GetCode(folder_id):
    drive_service = authenticate_drive()
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/json'",
        spaces='drive',
        fields="nextPageToken, files(id, name)").execute()

    items = results.get('files', [])

    if not items:
        print('No JSON files found.')
        #trying to update iterator function
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

class Kinograph:
    def extractImages(self,video_stream, folder_id, N):
        count = 0
        video_stream.seek(0)  # Ensure we're at the beginning of the stream
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            video_stream.seek(0)  # Ensure we're at the beginning of the stream
            temp_file.write(video_stream.read())
            temp_file_path = temp_file.name  # Get the path to the temp file
        vidcap = cv2.VideoCapture(temp_file_path)
        success, image = vidcap.read()
        success = True
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000))  # added this line
        #Create Kinograph Folder
        SubFolder=MassUpload('Animation Kinograph',folder_id)
        SubFolderID=SubFolder.create_subfolder()
        ImagePathList = []
        while success:

            if count % N == 0:
                print('Read a new frame: ', success)
                _, buffer = cv2.imencode('.jpg', image)  # Convert to JPEG
                image_bytes = buffer.tobytes()  # Convert to bytes
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as img_file:
                    img_file.write(image_bytes)
                    img_file_path = img_file.name
                # Upload the image bytes directly to Google Drive
                image_name = f"frame_{count}.jpg"  # Name of the image file
                GoogleDriveFile=UploadFile(image_name)
                GoogleDriveFile.upload_file_to_drive(GoogleDriveFile.filename,img_file_path,"image/jpeg",SubFolderID)
            success, image = vidcap.read()
            count = count + 1
        return SubFolderID


    def get_file_stream(self,file_name, folder_id):
        # Query to find the file in the specified folder
        drive_service = authenticate_drive()
        query = f"name='{file_name}' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print("No files found.")
            return None

        # Get the file ID
        file_id = items[0]['id']

        # Download the file stream
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False

        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        fh.seek(0)  # Go back to the beginning of the BytesIO stream
        return fh
class LLMAnalysis:
    def __init__(self, FolderID_1,FolderID_2,prompt):
        self.FolderID_1 = FolderID_1
        self.FolderID_2 = FolderID_2
        self.set_1=self.DownloadKinograph(self.FolderID_1)
        self.set_2=self.DownloadKinograph(self.FolderID_2)
        self.prompt=prompt

    def encode_image_to_base64(self,image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        return base64_image

    def DownloadKinograph(self,folder_id):
        drive_service = authenticate_drive()
        query = f"'{folder_id}' in parents and mimeType contains 'image/'"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print("No files found.")
            return None
        file_path = []

        for item in items:

            # Get the file ID
            file_id = item['id']
            # Download the file stream
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
                fh.seek(0)  # Go back to the beginning of the BytesIO stream
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as temp_file:
                fh.seek(0)  # Ensure we're at the beginning of the stream
                temp_file.write(fh.read())
                temp_file_path = temp_file.name
                file_path.append(temp_file_path)
        base64_image_list = []
        for i in file_path:
            base64_image_list.append(self.encode_image_to_base64(i))
        return base64_image_list
    def extract_backticks_code(self,text):
        # Use regex to find all content between triple backticks (``` code ```)
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches ==[]:
            pattern = r"```(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)
        return matches
    def CompareKinographs(self):
        # Create the messages for the API call
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"I have two sets of images functioning as kineographs for this prompt: {self.prompt}."
                                    f"which one is performing better at representing the prompt and why. Consider the images"
                                    f"come in order in their respective sets (return name of the set, set 1 or set 2, which more closely aligns with the prompt surounded by 3 backticks  on each side``` ```"
                                    f"as well as your analysis"
                        }
                    ]
                }
            ]

            # Adding images from set_1
            for base64_image in [self.set_1[i] for i in [0, 2, 4]]:
                messages[0]['content'].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            # Adding images from set_2
            for base64_image in [self.set_2[i] for i in [0, 2, 4]]:
                messages[0]['content'].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            # Make the API call
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1000,
            )

            # Extract the response content
            response_content = response['choices'][0]['message']['content']
            print(response_content)
            analysis_file = 'Evaluation.txt'
            with open(analysis_file, "w") as file:
                # Write some text to the file
                file.write(response_content)
            fileupload = UploadFile('Evaluation.txt')
            prefered_set=str(self.extract_backticks_code(response_content)[0])
            if prefered_set.find('2') != -1 or prefered_set.find('second') != -1:
                fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_2)
            elif prefered_set.find('1') != -1 or prefered_set.find('first') != -1:
                fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_1)
            return self.extract_backticks_code(response_content)[0]
        except Exception as e:
            print(f"An error occurred: {e}")
            return 'Set 2'
    def ProvideFeedback(self,preferred_set):
        if preferred_set.find('2') != -1 or preferred_set.find('second') != -1:
            preferred_set_photos=self.set_2
        elif preferred_set.find('1') != -1 or preferred_set.find('first') != -1:
            preferred_set_photos=self.set_1
        else:
            self.CompareKinographs()
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"provide 1 sentences of feedback on this kinograph on what can be addressed to improve the animation to better fit the prompt: {self.prompt}."
                                    f"Do not provide any code just constructive feeback"
                        }
                    ]
                }
            ]

            # Adding images from set_1
            for base64_image in [preferred_set_photos[i] for i in [0, 2, 4]]:
                messages[0]['content'].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            # Make the API call
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=1000,
            )

            # Extract the response content
            response_content = response['choices'][0]['message']['content']
            print(response_content)
        
            analysis_file = 'ImprovementPlan.txt'
            with open(analysis_file, "w") as file:
                # Write some text to the file
                file.write(response_content)
            fileupload = UploadFile('ImprovementPlan.txt')
            if preferred_set.find('2') != -1 or preferred_set.find('second') != -1:
                fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_2)
            elif preferred_set.find('1') != -1 or preferred_set.find('first') != -1:
                fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_1)
            return response_content
        except Exception as e:
            print(f"An error occurred: {e}")
            analysis_file = 'ImprovementPlan.txt'
            with open(analysis_file, "w") as file:
                # Write some text to the file
                file.write("Provide greater detail with regards to spatial, temporal and visual aspects of the animation")
            fileupload = UploadFile('ImprovementPlan.txt')
            
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_2)
            response_content="Provide greater detail with regards to spatial, temporal and visual aspects of the animation"
            return response_content

    def GetParentFolder(self,preferred_set):

        if preferred_set.find('2') != -1 or preferred_set.find('second') != -1:
            print('Set 2 get parent')
            subfolder_id=self.FolderID_2
        elif preferred_set.find('1') != -1 or preferred_set.find('first') != -1:
            print('Set 1 get parent')
            subfolder_id=self.FolderID_1
        elif preferred_set=='Set 2':
            subfolder_id=self.FolderID_2
        else:
            preferred_set=self.CompareKinographs()
            return self.GetParentFolder(preferred_set)
        print(subfolder_id)
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
    def GetPreviousCodeGeneration(self,preffered_set):
        folder_id=self.GetParentFolder(preffered_set)
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
class FirstCycle:
    def __init__(self, FileName1, FolderID1, prompt):
        self.FileName1 = FileName1
        self.FolderID1 = FolderID1
        self.prompt=prompt
        self.Kinograph=Kinograph()
    def encode_image_to_base64(self,image_path):
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        return base64_image

    def DownloadKinograph(self,folder_id):
        drive_service = authenticate_drive()
        query = f"'{folder_id}' in parents and mimeType contains 'image/'"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print("No files found.")
            return None
        file_path = []

        for item in items:

            # Get the file ID
            file_id = item['id']
            # Download the file stream
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")
                fh.seek(0)  # Go back to the beginning of the BytesIO stream
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg') as temp_file:
                fh.seek(0)  # Ensure we're at the beginning of the stream
                temp_file.write(fh.read())
                temp_file_path = temp_file.name
                file_path.append(temp_file_path)
        base64_image_list = []
        for i in file_path:
            base64_image_list.append(self.encode_image_to_base64(i))
        return base64_image_list
    def FirstCycle(self):
        VideoStream=self.Kinograph.get_file_stream(self.FileName1, self.FolderID1)
        SubFolder=self.Kinograph.extractImages(VideoStream, self.FolderID1, 40)
        Image_Set=self.DownloadKinograph(SubFolder)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"provide 1 sentences of feedback on this kinograph on what can be addressed to improve the animation to better fit the prompt and make the animation more real: {self.prompt}."
                                f"Do not provide any code just constructive feeback"
                    }
                ]
            }
        ]

        # Adding images from set_1
        for base64_image in Image_Set:
            messages[0]['content'].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=1000,
        )

        # Extract the response content
        response_content = response['choices'][0]['message']['content']
        print(response_content)
        analysis_file = 'ImprovementPlan.txt'
        with open(analysis_file, "w") as file:
            # Write some text to the file
            file.write(response_content)
        fileupload = UploadFile('ImprovementPlan.txt')
        fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", SubFolder)
        return response_content
class FullCycle:
    def __init__(self, FileName1, FileName2, FolderID1, FolderID2, Prompt):
        self.FileName1 = FileName1
        self.FileName2 = FileName2
        self.FolderID1 = FolderID1
        self.FolderID2 = FolderID2
        self.Prompt=Prompt
    def Cylce(self):
        if self.CheckForKinograph(self.FolderID1)==False:

            kinograph1 = Kinograph()
            VideoStream1 = kinograph1.get_file_stream(self.FileName1, self.FolderID1)
            SubFolder1 = kinograph1.extractImages(VideoStream1, self.FolderID1, 40)
        else:
            SubFolder1=self.CheckForKinograph(self.FolderID1)
        if self.CheckForKinograph(self.FolderID2)==False:
            kinograph2 = Kinograph()
            VideoStream2 = kinograph2.get_file_stream(self.FileName2, self.FolderID2)
            SubFolder2 = kinograph2.extractImages(VideoStream2, self.FolderID2, 40)
        else:
            SubFolder2=self.CheckForKinograph(self.FolderID2)
        Analysis_Test = LLMAnalysis(SubFolder1, SubFolder2, self.Prompt)
        preferred_set = Analysis_Test.CompareKinographs()
        print(preferred_set)
        Code = Analysis_Test.GetPreviousCodeGeneration(preferred_set)
        print(Code)
        ImprovementPlan=Analysis_Test.ProvideFeedback(preferred_set)
        print(ImprovementPlan)
        return Code,ImprovementPlan
    def CheckForKinograph(self, folder_id, folder_name='Animation Kinograph'):
        drive_service = authenticate_drive()
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if items:
            return items[0]['id']  # Returns True and the folder ID if found
        return False    # Returns False and None if not found

if __name__ == '__main__':
    CycleInstance=FullCycle('BouncingBalls01.mp4','BouncingBalls00.mp4',
              '1p4BWjICXHX0L_o7eM5bFq2nb_Fa_q7pY','1yEYXk3bjPKX_VoBmYyQ1I7zTlQvlbl7u','Create me a python script for a blender animation of a Balls bouncing')
    Code=CycleInstance.Cylce()
    print(Code)
