import openai
import autopep8
import re
import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
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
    def chat_with_gpt4(self,text_prompt):
        try:
            # Send request to OpenAI's API
            response = openai.ChatCompletion.create(
                model="gpt-4",  # You can also use 'gpt-3.5-turbo' if you don't have access to GPT-4
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

            # Format the extracted code using autopep8
            formatted_code = autopep8.fix_code(extracted_code)

            return exec(formatted_code)

        except Exception as e:
            print(f"Error: {e}")

            # Modify the prompt to retry with additional guidance
            print(extracted_code)
            new_prompt = f"{extracted_code} this was returning an error {e} can you modify this code so that it addresses this error. Ensure all objects are in field of view when rendered."
            print("Retrying with modified prompt...")

            # Retry the function with the new prompt
            return self.chat_with_gpt4(new_prompt)




# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class UploadFile:
    def __init__(self,filename):
        self.filename=filename
    def authenticate_drive(self):
        """Shows basic usage of the Drive v3 API. Lists the user's Drive files."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('drive', 'v3', credentials=creds)


    def upload_file_to_drive(self,file_name, file_path, mime_type):
        drive_service = self.authenticate_drive()

        # File metadata to specify the file name and folder (optional)
        file_metadata = {'name': file_name,
                         'parents': ['1VYfJiunHJ8i8JPQIN5IIp8ISr9jp7ni8']}

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
    testinstance=animationgeneartion("Create me a python script for an animation blender file of the planets in orbit. Use different colors for each of the planets, and make sure to have movement",
                        '/Users/will/PycharmProjects/pythonProject8/PlanetaryOrbitAnimation.blend')
    code=testinstance.chat_with_gpt4(testinstance.prompt)
    fileupload=UploadFile('PlanetaryOrbitAnimation.blend')
    fileupload.upload_file_to_drive(fileupload.filename,fileupload.filename,"application/x-blender")
    prompt_file='/Users/will/PycharmProjects/pythonProject8/PlanetaryOrbitAnimation.txt'
    with open(prompt_file, "w") as file:
        # Write some text to the file
        file.write(testinstance.prompt)
    fileupload=UploadFile('PlanetaryOrbitAnimation.txt')
    fileupload.upload_file_to_drive(fileupload.filename,fileupload.filename,"text/plain")

