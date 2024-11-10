
from Packages import *
from AnimationGeneration import *
from Iterator import *
from datetime import datetime
class Pipeline:
    def __init__(self):
        self.Prompt1=("BouncingBalls","Create me a python script for a blender animation of a ball bouncing")
        self.Prompt2=("PlanetsOrbiting","Create me a python script for a blender animation of a Planets orbitting around the Sun")
        self.Prompt3=("QuiltFalling","Create me a python script for a blender animation of a quilt falling onto a sphere")
        self.Prompt4=("DrivingThroughWall","Create me a python script for an object driving through a wall")
        self.PromptList=[self.Prompt1,self.Prompt2,self.Prompt3,self.Prompt4]
    def RunPipeline(self):

        MasterFolder=MassUpload(f'AnimationPipelineTestInstance {datetime.now().date()}')
        MasterFolderID=MasterFolder.create_subfolder()
        for PromptTuple in self.PromptList:
            Prompt=PromptTuple[0]
            # First Instance
            PromptFolder=MassUpload(Prompt, MasterFolderID)
            PromptFolderID=PromptFolder.create_subfolder()
            for i in range(0,3):
                ParentFolder=MassUpload(F"{Prompt}{i}", PromptFolderID)
                ParentFolderID=ParentFolder.create_subfolder()
                SubFolderID_LST=[]
                for i in range (0,3):
                    start_time = time.time()
                    if i==0:
                        AnimationInstance = animationgeneartion(Prompt,
                                                                F"{ParentFolder.FolderName}{i}.blend")
                        print(AnimationInstance.prompt)
                        code, ExtractedCode = AnimationInstance.chat_with_LLM(AnimationInstance.prompt)                        
                        SubFolder = MassUpload(F"{ParentFolder.FolderName}{i}",ParentFolderID)
                        SubFolderID = SubFolder.create_subfolder()
                        if ExtractedCode is None:
                            end_time = time.time()
                            elasped_time = end_time - start_time

                            # Upload JSON File
                            AnimationInstance.json_file['elapsed_time'] = elasped_time
                            AnimationInstance.json_file['Failed']='True'
                            AnimationInstance.json_file['Code'] = ExtractedCode
                            prompt_file = F"{ParentFolder.FolderName}{i}.json"
                            with open(prompt_file, "w") as file:
                                # Write some text to the file
                                json.dump(AnimationInstance.json_file, file, indent=4)
                            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
                            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
                            break
                        fileupload = UploadFile(AnimationInstance.filename)
                        fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/x-blender",
                                                        SubFolderID)
                        fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.mp4")
                        fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "video/mp4", SubFolderID)
                        end_time = time.time()
                        elasped_time = end_time - start_time

                        # Upload JSON File
                        AnimationInstance.json_file['elapsed_time'] = elasped_time
                        AnimationInstance.json_file['Failed']='False'
                        AnimationInstance.json_file['Code'] = ExtractedCode
                        prompt_file = F"{ParentFolder.FolderName}{i}.json"
                        with open(prompt_file, "w") as file:
                            # Write some text to the file
                            json.dump(AnimationInstance.json_file, file, indent=4)
                        fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
                        fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
                        SubFolderID_LST.append(SubFolderID)
                    elif i==1:
                        FirstCycleInstance=FirstCycle(F"{ParentFolder.FolderName}{i-1}.mp4",SubFolderID_LST[0],Prompt)
                        ImprovementPlan=FirstCycleInstance.FirstCycle()
                        FirstInstanceCode=GetCode(SubFolderID_LST[0])
                        AnimationInstance = animationgeneartion(F"Here is the original Prompt {AnimationInstance.prompt}"
                                                                            F" and these are the critques {ImprovementPlan}",
                                                                F"{ParentFolder.FolderName}{i}.blend",
                                                                FirstInstanceCode)
                        print(AnimationInstance.prompt)
                        code, ExtractedCode = AnimationInstance.chat_with_LLM(AnimationInstance.prompt)
                        SubFolder = MassUpload(F"{ParentFolder.FolderName}{i}",ParentFolderID)
                        SubFolderID = SubFolder.create_subfolder()
                        if ExtractedCode is None:
                            end_time = time.time()
                            elasped_time = end_time - start_time

                            # Upload JSON File
                            AnimationInstance.json_file['elapsed_time'] = elasped_time
                            AnimationInstance.json_file['Failed']='True'
                            AnimationInstance.json_file['Code'] = ExtractedCode
                            prompt_file = F"{ParentFolder.FolderName}{i}.json"
                            with open(prompt_file, "w") as file:
                                # Write some text to the file
                                json.dump(AnimationInstance.json_file, file, indent=4)
                            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
                            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
                            break
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
                        InstanceOfCycle=FullCycle(F"{ParentFolder.FolderName}{i-2}.mp4",F"{ParentFolder.FolderName}{i-1}.mp4",
                                SubFolderID_LST[i-2],SubFolderID_LST[i-1],Prompt)
                        PreferredCode,ImprovementPlan=InstanceOfCycle.Cylce()
                        AnimationInstance = animationgeneartion(Prompt,
                                                                F"{ParentFolder.FolderName}{i}.blend",
                                                                FirstInstanceCode)
                        print(AnimationInstance.prompt)
                        code, ExtractedCode = AnimationInstance.chat_with_LLM(F"Here is the original Prompt {AnimationInstance.prompt}"
                                                                            F" and these are the critques {ImprovementPlan}")
                        SubFolder = MassUpload(F"{ParentFolder.FolderName}{i}",ParentFolderID)
                        SubFolderID = SubFolder.create_subfolder()
                        if ExtractedCode is None:
                            end_time = time.time()
                            elasped_time = end_time - start_time

                            # Upload JSON File
                            AnimationInstance.json_file['elapsed_time'] = elasped_time
                            AnimationInstance.json_file['Failed']='True'
                            AnimationInstance.json_file['Code'] = ExtractedCode
                            prompt_file = F"{ParentFolder.FolderName}{i}.json"
                            with open(prompt_file, "w") as file:
                                # Write some text to the file
                                json.dump(AnimationInstance.json_file, file, indent=4)
                            fileupload = UploadFile(F"{ParentFolder.FolderName}{i}.json")
                            fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
                            break
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

if __name__=='__main__':
    PipelineInstance=Pipeline()
    PipelineInstance.RunPipeline()