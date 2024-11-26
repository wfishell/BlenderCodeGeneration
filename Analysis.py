
from Iterator import *
from Packages import *
from collections import defaultdict
import numpy as np
import matplotlib.image as mpimg
import pandas as pd
import traceback
import warnings
import contextlib
import io
def clean_messages(message_dict):
    return {
        key: [msg.split(': ', 1)[-1] for msg in messages]
        for key, messages in message_dict.items()
    }
def DictAvgs(list_dict):
    sums = defaultdict(int)
    counts = defaultdict(int)

    # Calculate cumulative sum and count for each key
    for d in list_dict:
        for key, values in d.items():
            sums[key] += sum(values)
            counts[key] += len(values)
def categorize_error(message):
    if "has no attribute" in message:
        return "AttributeError"
    elif "not found" in message:
        return "NotFoundError"
    elif "index out of range" in message:
        return "IndexError"
    elif "Context missing active object" in message:
        return "ContextError"
    elif "name" in message and "is not defined" in message:
        return "NameError"
    else:
        return "OtherError"

    # Calculate averages
    averages = {key: sums[key] / counts[key] for key in sums}
    return averages

class Folder_Analysis:
    def __init__(self, FolderID):
        self.FolderID=FolderID
        self.subfolder_ids=self.get_subfolder_ids()
    def get_subfolder_ids(self):
        drive_service = authenticate_drive()
        query = f"'{self.FolderID}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        # Extract subfolder IDs into a list
        subfolder_ids = [folder['id'] for folder in results.get('files', [])]
        return subfolder_ids
    def Avg_Query_Time(self, Prompt):
        return None
    def FileAnalysis(self):
        
        Error_DF_List=[]
        Warning_DF_List=[]
        for i in range(0,len(self.subfolder_ids)):
            if i==0:
                file=individual_file_analysis(self.subfolder_ids[i])
                Warning_DF, Error_DF=file.Get_Error_Frequencies_DataFrame()
                Error_DF_List.append(Error_DF)
            else:
                file=individual_file_analysis(self.subfolder_ids[i])
                Temp_Warning_DF, Temp_Error_DF=file.Get_Error_Frequencies_DataFrame()
                Error_DF_List.append(Temp_Error_DF)
        Error_DF_Final=pd.concat(Error_DF_List,ignore_index=True)
        Error_DF_Final = Error_DF_Final.groupby('ErrorMessage', as_index=False)['Frequency'].sum()
        Error_DF_Final['ErrorMessage'] = Error_DF_Final['ErrorMessage'].apply(categorize_error)

        Error_DF_Summary = Error_DF_Final.groupby('ErrorMessage')['Frequency'].sum().reset_index()
        return Error_DF_Summary
    def Get_Error_Rate_By_Instance(self):
        DF_List=[]
        for ele in self.subfolder_ids:
            File=individual_file_analysis(ele)
            Temp_DF_Error_Rate=File.Get_Error_Frequencies_By_Instance_DataFrame()
            DF_List.append(Temp_DF_Error_Rate)
        Error_DF_Final_By_Instance=pd.concat(DF_List)
        Error_DF_Final_By_Instance['ErrorMessage'] = Error_DF_Final_By_Instance['ErrorMessage'].apply(categorize_error)
        Error_DF_Final_By_Instance = Error_DF_Final_By_Instance.groupby(['ErrorMessage','Instance'], as_index=False)['Frequency'].sum()

        return Error_DF_Final_By_Instance

    def Get_RunTime_Data(self):
        DataFrameList=[]
        for ele in self.subfolder_ids:
            GenerationFailure=False
            Temp_Analysis=individual_file_analysis(ele)
            Temp_Run_Time_DF=Temp_Analysis.Get_RunTime_DataFrame_Detailed()
            for ele in Temp_Analysis.JSON_Files:
                if ele['Code']==None:
                    GenerationFailure=True 
                    break
            if GenerationFailure==False:
                DataFrameList.append(Temp_Run_Time_DF)
        ConcatDF=pd.concat(DataFrameList)
        ConcatDF.fillna(0,inplace=True)
        RunTimeAverages = ConcatDF.groupby(ConcatDF.index).mean()
        return RunTimeAverages
    
    def Plot_RunTime_Date(self, Prompt):
        # Assuming query_df is obtained from self.Get_RunTime_Data()
        query_df = self.Get_RunTime_Data()
        melted_df = query_df.reset_index().melt(id_vars='index', var_name='Metric', value_name='Time')
        melted_df.rename(columns={'index': 'Instance'}, inplace=True)

        # Pivot the melted DataFrame to get the values for stacking
        pivot_df = melted_df.pivot(index='Instance', columns='Metric', values='Time').fillna(0)

        # Plot using Matplotlib
        plt.figure(figsize=(10, 6))

        # Create a stacked bar plot
        bottoms = np.zeros(len(pivot_df))  # Initialize the bottom positions for stacking
        for metric in pivot_df.columns:
            plt.bar(pivot_df.index, pivot_df[metric], bottom=bottoms, label=metric)
            bottoms += pivot_df[metric].values  # Update the bottom positions

        # Customizing the chart
        plt.xlabel('Instances')
        plt.ylabel('Time (seconds)')
        plt.title(f'Average Query and Render Times for {Prompt}')

        # Add more Y-axis ticks
        plt.yticks(np.arange(0, bottoms.max() + 10, 10))  # Adjust the range and step as needed

        # Draw a rectangle around the Render Times and add labels
        render_time_index = pivot_df.columns.get_loc('Render_Time')  # Get the index of the Render_Time column
        for i, instance in enumerate(pivot_df.index):
            render_time_value = pivot_df.iloc[i, render_time_index]
            plt.gca().add_patch(plt.Rectangle((i - 0.4, bottoms[i] - render_time_value), 0.8, render_time_value, 
                                                edgecolor='red', facecolor='none', linewidth=2))
            
            # Add label for the total render time
            plt.text(i, bottoms[i] - render_time_value / 2, f'{render_time_value:.2f}', 
                    ha='center', va='center', color='black', fontsize=10)

        plt.legend(title='Metric', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'./docs/{Prompt}_{datetime.today().date()}_RenderAndQueryTime.png', format="png", dpi=300, bbox_inches="tight")
        path=f'./docs/{Prompt}_{datetime.today().date()}_RenderAndQueryTime.png'
        plt.close()
        return path


class individual_file_analysis:
    def __init__(self,FolderID):
        self.JsonFileTypes=['Code','Prompt','elapsed_time','gpt_query_time_0','gpt_query_time_1',
                            'gpt_query_time_2','gpt_query_time_3','render_time_0','render_time_1',
                            'render_time_2','render_time_3', 'Failed']
        self.FolderID=FolderID
        self.JSON_Files=self.Analyze_JSON()
        
    def Analyze_JSON(self):
        drive_service = authenticate_drive()
        query = f"'{self.FolderID}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            orderBy='name asc'  
        ).execute()
        
        subfolders = results.get('files', [])
        all_json_files = []

        for folder in subfolders:
            json_query = f"'{folder['id']}' in parents and mimeType='application/json'"
            json_results = drive_service.files().list(
                q=json_query,
                spaces='drive',
                fields='files(id, name, parents, createdTime)'
            ).execute()
            
            json_files = json_results.get('files', [])
            for json_file in json_files:
                json_file['folder_name'] = folder['name']
                json_file['folder_id'] = folder['id']
                all_json_files.append(json_file)
        
        all_json_files.sort(key=lambda x: x['name'])

        all_json_contents = []
        for json_file in all_json_files:
            file_id = json_file['id']
            request = drive_service.files().get_media(fileId=file_id)
            file_content = request.execute()
            json_content = json.loads(file_content)
            all_json_contents.append(json_content)

        return all_json_contents

    def Analyze_MP4_Files(self):
        drive_service = authenticate_drive()
        query = f"'{self.FolderID}' in parents and mimeType='application/vnd.google-apps.folder'"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            orderBy='name asc'  
        ).execute()
        
        subfolders = results.get('files', [])
        all_mp4_files = []

        for folder in subfolders:
            mp4_query = f"'{folder['id']}' in parents and mimeType='video/mp4'"
            mp4_results = drive_service.files().list(
                q=mp4_query,
                spaces='drive',
                fields='files(id, name, parents, createdTime)'
            ).execute()
            
            mp4_files = mp4_results.get('files', [])
            for mp4_file in mp4_files:
                mp4_file['folder_name'] = folder['name']
                mp4_file['folder_id'] = folder['id']
                all_mp4_files.append(mp4_file)

        all_mp4_files.sort(key=lambda x: x['name'])

        all_mp4_contents = []
        for mp4_file in all_mp4_files:
            file_id = mp4_file['id']
            request = drive_service.files().get_media(fileId=file_id)
            file_content = request.execute()  # This retrieves the binary content of the MP4 file.
            all_mp4_contents.append({
                'file_content': file_content,
                'file_name': mp4_file['name'],
                'folder_name': mp4_file['folder_name'],
                'created_time': mp4_file['createdTime']
            })

        return all_mp4_contents

    def Get_Query_Runtimes(self):
        # returns dict of run time 
        RunTimeHistory={}
        j=1
        for ele in self.JSON_Files:
            for key,val in ele.items():
                if 'gpt_query_time' in key:
                    if j not in RunTimeHistory:
                        RunTimeHistory[j]=[ele[key]]
                    else:
                        RunTimeHistory[j].append(ele[key])
            j+=1
        return RunTimeHistory
    def ElapsedTime(self):
        ElaspedTime={}
        instance=1
        for ele in self.JSON_Files:
            ElaspedTime[instance]=ele['elapsed_time']
            instance+=1
        return ElaspedTime
    
    def Get_Render_Time(self):
        #Needs to be updated once we get more tokens
        ElapsedTime=self.ElapsedTime()
        QueryRunTime=self.Get_Query_Runtimes()
        RenderTime={}
        for key in ElapsedTime:
            RenderTime[key]=ElapsedTime[key]-sum(QueryRunTime[key])
        return RenderTime
    def Get_RunTime_DataFrame_Detailed(self):
        data=self.Get_Query_Runtimes()
        result = {}
            
            # Iterate through the input dictionary
        for key, values in data.items():
            # Assign the first and second elements to the new keys
            for index in range(len(values)):
                if f'Query_Time_{index + 1}' in result:
                    result[f'Query_Time_{index + 1}'].append(values[index])
                else:
                    result[f'Query_Time_{index + 1}'] = [values[index]]

        max_length = max(len(result) for result in result.values())

        # Initialize a new dictionary to hold the padded results
        padded_result = {}

        # Iterate through the input dictionary
        for key, values in result.items():
            # Pad the list with zeros to match the maximum length
            padded_values = values + [0] * (max_length - len(values))
            padded_result[key] = padded_values

        Runtime=self.Get_Render_Time()
        Runtime
        query_df = pd.DataFrame(padded_result)
        query_df.index = [f"Instance_{i+1}" for i in range(len(query_df))]

        query_df['Render_Time'] = list(Runtime.values())
        return query_df
    def Get_Error_Frequencys(self):
        
        Error_History=[]
        for ele in self.JSON_Files:
            for key,val in ele.items():
                if key not in self.JsonFileTypes: 
                    ErrorCode=val[0] 
                    BlenderCode=BlenderCodeAnalyzer(ErrorCode[0])
                    Analysis=BlenderCode.analyze()
                    Analysis=clean_messages(Analysis)
                    Error_History.append(Analysis)
        return Error_History

    def Get_Error_Frequencies_DataFrame(self):
        Error_History = self.Get_Error_Frequencys()
        Error_Frequency = {'errors': [], 'warnings': []}

        # Populate Error_Frequency with errors and warnings
        for ele in Error_History:
            for key, val in ele.items():
                if key in Error_Frequency:  # Check if the key exists
                    Error_Frequency[key].extend(val)

        # Create DataFrames for errors and warnings
        Error_DF = pd.DataFrame(Error_Frequency['errors'], columns=['ErrorMessage'])
        Warning_DF = pd.DataFrame(Error_Frequency['warnings'], columns=['WarningMessage'])

        # Group by error and warning messages
        error_summary = Error_DF.groupby('ErrorMessage').size().reset_index(name='Frequency') if not Error_DF.empty else pd.DataFrame(columns=['ErrorMessage', 'Frequency'])
        warning_summary = Warning_DF.groupby('WarningMessage').size().reset_index(name='Frequency') if not Warning_DF.empty else pd.DataFrame(columns=['WarningMessage', 'Frequency'])

        return warning_summary, error_summary  
    def Get_Error_History_By_Instance(self):
        Error_History=[]
        i=1
        for ele in self.JSON_Files:
            instance_error_list=[]
            Instance_Analysis={'errors':[]}
            for key,val in ele.items():
                if key not in self.JsonFileTypes: 
                    ErrorCode=val[0] 
                    BlenderCode=BlenderCodeAnalyzer(ErrorCode[0])
                    Analysis=BlenderCode.analyze()
                    Analysis=clean_messages(Analysis)
                    Instance_Analysis['errors'].append(Analysis['errors'][0])
            Error_History.append((i,Instance_Analysis))
            
            i+=1
        return Error_History 
    def Get_Error_Frequencies_By_Instance_DataFrame(self):
        Error_History=self.Get_Error_History_By_Instance()
        DF_Error_List=[]
        for ele in Error_History:
            Temp_Instance_Error_History=pd.DataFrame(ele[1])
            Temp_Instance_Error_History['Instance']=f'Instance_{ele[0]}'
            DF_Error_List.append(Temp_Instance_Error_History)
        Error_DF=pd.concat(DF_Error_List)
        Error_DF.rename(columns={'errors':'ErrorMessage'}, inplace=True)


        error_summary = (Error_DF.groupby(['ErrorMessage', 'Instance']).size().reset_index(name='Frequency')) if not Error_DF.empty else pd.DataFrame(columns=['ErrorMessage', 'Frequency'])        
        return error_summary

class BlenderCodeAnalyzer:
    def __init__(self, code_string):
        self.code = code_string.strip()
        self.errors = []
        self.warnings = []
        self.outputs = []

    def execute_code(self):
        """Execute the Blender code and capture runtime errors, warnings, and outputs."""
        # Capture warnings in the context
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Capture all warnings

            # Redirect stdout and stderr to capture print statements and error messages
            with io.StringIO() as buf_stdout, io.StringIO() as buf_stderr:
                with contextlib.redirect_stdout(buf_stdout), contextlib.redirect_stderr(buf_stderr):
                    try:
                        exec(self.code)  # Execute the code
                    except Exception as e:
                        # Capture the exception type and message
                        error_type = type(e).__name__
                        error_message = str(e)
                        self.errors.append(f"{error_type}: {error_message}")

                # Get the outputs from stdout and stderr
                output = buf_stdout.getvalue()
                error_output = buf_stderr.getvalue()

            # Process captured warnings
            for warning in w:
                warning_type = warning.category.__name__
                warning_msg = str(warning.message)
                warning_line = warning.lineno
                self.warnings.append(f"{warning_type} (line {warning_line}): {warning_msg}")

            # Capture any output messages
            if output:
                self.outputs.extend(output.strip().split('\n'))
            if error_output:
                self.outputs.extend(error_output.strip().split('\n'))

    def analyze(self):
        """Run all checks and return results."""
        self.execute_code()  # Execute the code and capture runtime errors, warnings, and outputs
        return {
            'errors': self.errors,
        }



def PlotErrorRates(File_List):
    Error_DF_List=[]
    for Prompt,FileID in File_List.items():
        File=Folder_Analysis(FileID)
        Temp_Error_DF = File.FileAnalysis()  
        Temp_Error_DF['Prompt']=Prompt
        Error_DF_List.append(Temp_Error_DF)
    
    Error_DF=pd.concat(Error_DF_List)
    Error_DF.fillna(0, inplace=True)
    pivot_df = Error_DF.pivot_table(index='Prompt', columns='ErrorMessage', values='Frequency', fill_value=0)
    pivot_df = pivot_df.infer_objects()
    pivot_df.plot(kind='bar', figsize=(12, 8))
    plt.title('Error Frequencies Across DataFrames')
    plt.xlabel('Error Messages')
    plt.ylabel('Frequency')
    plt.legend(title='DataFrame')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'./docs/ErrorBarGraph_{datetime.today().date()}.png', format="png", dpi=300, bbox_inches="tight")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def PlotErrorEvolution(FolderList):
    DF_List = []

    for key, file in FolderList.items():
        Folder = Folder_Analysis(file)  # Assume Folder_Analysis is defined
        Temp_DF = Folder.Get_Error_Rate_By_Instance()  # Each DF contains ['Instance', 'ErrorMessage', 'Frequency']
        DF_List.append(Temp_DF)

    combined_df = pd.concat(DF_List, ignore_index=True)

    grouped_df = combined_df.groupby(['Instance', 'ErrorMessage']).sum().reset_index()

    pivot_df = grouped_df.pivot(index='Instance', columns='ErrorMessage', values='Frequency').fillna(0)

    expected_errors = ['AttributeError', 'NotFoundError', 'IndexError', 'ContextError', 'NameError', 'OtherError']
    for error in expected_errors:
        if error not in pivot_df.columns:
            pivot_df[error] = 0

    pivot_df = pivot_df[expected_errors]

    fig, ax = plt.subplots(figsize=(10, 6))

    indices = np.arange(len(pivot_df.index)) 

    bottom = np.zeros(len(pivot_df.index))

    for error in expected_errors:
        ax.bar(
            indices,
            pivot_df[error],
            bottom=bottom,
            label=error
        )
        bottom += pivot_df[error]  

    ax.set_title('Error Evolution Over Instances', fontsize=16)
    ax.set_xlabel('Instance', fontsize=12)
    ax.set_ylabel('Frequency of Errors', fontsize=12)
    ax.set_xticks(indices)
    ax.set_xticklabels(pivot_df.index, rotation=45, ha='right')
    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(f'./docs/ErrorEvolution_{datetime.today().date()}.png', format="png", dpi=300, bbox_inches="tight")

import cv2
import numpy as np
from datetime import datetime
import os

def lucas_kanade_optical_flow(file_content, Prompt):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        # Write the file content to the temporary file
        temp_file.write(file_content)
        temp_file_path = temp_file.name  
    cap = cv2.VideoCapture(temp_file_path)
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
    lk_params = dict(winSize=(15, 15),
                     maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    ret, first_frame = cap.read()
    if not ret:
        print("Error: Unable to read video file")
        return

    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    prev_points = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
    mask = np.zeros_like(first_frame)
    height, width, _ = first_frame.shape

    output_dir = './docs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = f'./docs/Lucas_Kanade_Flow_{Prompt}_{datetime.today().date()}.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))  # 30 FPS

    if not out.isOpened():
        print("Error: Could not open the output video file for writing.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        curr_points, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_points, None, **lk_params)

        if curr_points is None:
            print("No points detected in this frame.")
            break

        good_new = curr_points[status == 1]
        good_prev = prev_points[status == 1]

        if good_new.size == 0 or good_prev.size == 0:
            continue

        for i, (new, old) in enumerate(zip(good_new, good_prev)):
            a, b = map(int, new.ravel())
            c, d = map(int, old.ravel())
            mask = cv2.line(mask, (a, b), (c, d), (0, 255, 0), 2)
            frame = cv2.circle(frame, (a, b), 5, (0, 0, 255), -1)

        output = cv2.add(frame, mask)

        out.write(output)  # Write the frame to the output video

        # Removed cv2.imshow("Optical Flow - Lucas Kanade", output) to prevent video playback

        prev_gray = curr_gray.copy()
        prev_points = good_new.reshape(-1, 1, 2)

    cap.release()
    out.release()  # Release the VideoWriter
    cv2.destroyAllWindows()

def calculate_magnitude(prev_points, curr_points):
    return np.linalg.norm(curr_points - prev_points, axis=1)
def quantify_optical_flow(file_content, Title):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        # Write the file content to the temporary file
        temp_file.write(file_content)
        temp_file_path = temp_file.name  
    cap = cv2.VideoCapture(temp_file_path)
    # Parameters for Shi-Tomasi corner detection and Lucas-Kanade
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
    lk_params = dict(winSize=(15, 15), maxLevel=2,
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    ret, first_frame = cap.read()
    if not ret:
        print("Error: Unable to read video file")
        return
    
    prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    prev_points = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
    
    frame_metrics = []  # To store motion metrics for each N to N+10
    accumulated_metrics = {
        "mean_motion": 0,
        "total_motion": 0,
        "motion_variance": 0,
        "num_points": 0,
    }
    
    frame_count = 0  # Counter for frames processed
    skip_frames = 10  # Number of frames to skip

    while True:
        # Read the next frame
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert the current frame to grayscale
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Only process every 10th frame after the first frame
        if frame_count % skip_frames == 0 and frame_count != 0:
            # Calculate optical flow from prev_gray to curr_gray
            curr_points, status, error = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_points, None, **lk_params)
            
            if curr_points is None or status is None:
                break
            
            good_new = curr_points[status == 1]
            good_prev = prev_points[status == 1]
            
            if len(good_new) == 0 or len(good_prev) == 0:
                continue
            
            # Compute motion magnitudes
            magnitudes = calculate_magnitude(good_prev, good_new)
            
            # Update accumulated metrics
            accumulated_metrics["mean_motion"] += np.mean(magnitudes)
            accumulated_metrics["total_motion"] += np.sum(magnitudes)
            accumulated_metrics["motion_variance"] += np.var(magnitudes)
            accumulated_metrics["num_points"] += len(magnitudes)
        
        # Update previous frame and points every 10 frames
        if frame_count % skip_frames == 0 and frame_count != 0:
            prev_gray = curr_gray.copy()
            prev_points = good_new.reshape(-1, 1, 2) if len(good_new) > 0 else prev_points
            
            # Calculate average metrics after processing 10 frames
            if accumulated_metrics["num_points"] > 0:
                frame_metrics.append({
                    "mean_motion": [accumulated_metrics["mean_motion"] / (frame_count // skip_frames)],
                    "total_motion": [accumulated_metrics["total_motion"]],
                    "motion_variance": [accumulated_metrics["motion_variance"] / (frame_count // skip_frames)],
                    "num_points": [accumulated_metrics["num_points"]],
                })
                
                # Reset accumulated metrics for the next set of frames
                accumulated_metrics = {key: 0 for key in accumulated_metrics}
        
        frame_count += 1
    cap.release()
    i=10
    DF_List=[]
    
    for ele in frame_metrics:
        Frames=i
        Temp_DF=pd.DataFrame(ele)
        Temp_DF=Temp_DF[['mean_motion','total_motion','motion_variance']]
        Temp_DF['Frames']=Frames
        DF_List.append(Temp_DF)
        i+=10
    DF_Motion=pd.concat(DF_List)
    DF_Motion_Melted = pd.melt(DF_Motion, ['Frames'])
    sns.lineplot(data=DF_Motion_Melted, x='Frames', y='value', hue='variable')
    plt.title(f'{Title} Optical Flow throughout Animation')
    plt.savefig(f'./docs/{Title}Lucas_Kanade_Flow_{datetime.today().date()}.png', format="png", dpi=300, bbox_inches="tight")
    plt.close()
    return frame_metrics








if __name__=='__main__':
    '''Animation_Tests={'BouncingBalls':'1HvocLnxjpYmDs3JorPzAoOzhVzh8OQH5',
                        'PlanetOrbitting':'1tP4aRR9R1qgnIP-J2hAr_srgUsWfemJr',
                        'QuiltFalling':'1fJcByWWYgWLfiwsy_nMcx4MaVMxzgFqB',
                        'DriveThroughWall':'1-l77Hr4huDb6sOR6wwLJmYzBYa5O1hqF',
                        'DominoEffect':'1gL-khvBGD0t63ajcW0jl1_wqqQ0wDu4-',
                        'FireworksExploding':'12-3zRVqVWGVSGB_zWTtLtDm2VI1a992C'}

    PlotErrorEvolution(Animation_Tests)
    PlotErrorRates(Animation_Tests)
    Image_Path_List=[]
    for Prompt, File in Animation_Tests.items():
        Folder=Folder_Analysis(File)
        Temp_Path=Folder.Plot_RunTime_Date(Prompt)
        Image_Path_List.append(Temp_Path)
    num_images = len(Image_Path_List)

    fig, axs = plt.subplots(1, num_images, figsize=(num_images * 5, 5))  

    for ax, image_path in zip(axs, Image_Path_List):
        img = mpimg.imread(image_path)
        ax.imshow(img)
        ax.axis("off")  # Turn off axes for cleaner display

    # Display the plot
    plt.tight_layout()
    plt.savefig(f'./docs/Combined_Render_Times_{datetime.today().date()}.png', format="png", dpi=300, bbox_inches="tight")
    '''
    VideoAnalysis=individual_file_analysis('19Y1A6NgnEFfC2ZPhxlR7SgxaEX-C9QuB')
    VideoAnalysisMP4=VideoAnalysis.Analyze_MP4_Files()
    i=1
    for ele in VideoAnalysisMP4:
        try:
            metrics = quantify_optical_flow(ele['file_content'],f'DominoEffect_{i}')
            i+=1
        except:
            print('no motion')
            i+=1