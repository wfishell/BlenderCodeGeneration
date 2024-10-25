from Packages import *
from Main import *
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
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"I have two sets of images functioning as kineographs for this prompt: {self.prompt}."
                                f"which one is performing better at representing the prompt and why. Consider the images"
                                f"come in order in their respective sets (return name of better set surounded by ``` ``` as well as your analysis"
                    }
                ]
            }
        ]

        # Adding images from set_1
        for base64_image in self.set_1:
            messages[0]['content'].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        # Adding images from set_2
        for base64_image in self.set_2:
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
    def ProvideFeedback(self,preferred_set):
        if preferred_set.find('2') != -1 or preferred_set.find('second') != -1:
            preferred_set_photos=self.FolderID_2
        elif preferred_set.find('1') != -1 or preferred_set.find('first') != -1:
            preferred_set_photos=self.FolderID_1
        else:
            self.CompareKinographs()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"provide 3 sentences of feedback on this kinograph on what can be addressed to improve the animation to better fit the prompt: {self.prompt}."
                                f"Do not provide any code just constructive feeback"
                    }
                ]
            }
        ]

        # Adding images from set_1
        for base64_image in preferred_set_photos:
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
        fileupload = UploadFile('ImrpovementPlan.txt')
        if preferred_set.find('2') != -1 or preferred_set.find('second') != -1:
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_2)
        elif preferred_set.find('1') != -1 or preferred_set.find('first') != -1:
            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "text/plain", self.FolderID_1)
        return analysis_file

    def GetParentFolder(self,preferred_set):


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
class FullCycle:
    def __init__(self, FileName1, FileName2, FolderID1, FolderID2):
        self.FileName1 = FileName1
        self.FileName2 = FileName2
        self.FolderID1 = FolderID1
        self.FolderID2 = FolderID2
    def fullCycle(self):
        kinograph1 = Kinograph()
        VideoStream1 = kinograph1.get_file_stream(self.FileName1, self.FolderID1)
        kinograph2 = Kinograph()
        VideoStream2 = kinograph2.get_file_stream(self.FileName2, self.FolderID2)
        SubFolder1 = kinograph1.extractImages(VideoStream1, self.FolderID1, 20)
        SubFolder2 = kinograph2.extractImages(VideoStream2, self.FolderID2, 20)
        Analysis_Test = LLMAnalysis(SubFolder1, SubFolder2, 'Create an animation of balls bouncing')
        preferred_set = Analysis_Test.CompareKinographs()
        print(preferred_set)
        Code = Analysis_Test.GetPreviousCodeGeneration(preferred_set)
        print(Code)
        ImprovementPlan=Analysis_Test.GetParentFolder(preferred_set)
        return Code,ImprovementPlan

if __name__ == '__main__':
    CycleInstance=FullCycle('BouncingBalls2.mp4','MultipleBallsBouncing_o1.mp4',
              '19DpaJNOCZYj6hqv-TB171EqfgPt9hUUA','1-dTeKObHrL_EuHkkdXIV7jeK6swwjHMl')
    Code=CycleInstance.fullCycle()
