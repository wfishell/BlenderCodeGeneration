from Iterator import *
from Packages import *
from collections import defaultdict

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
                Warning_DF_List.append(Warning_DF)
            else:
                file=individual_file_analysis(self.subfolder_ids[i])
                Temp_Warning_DF, Temp_Error_DF=file.Get_Error_Frequencies_DataFrame()
                Error_DF_List.append(Temp_Error_DF)
                Warning_DF_List.append(Temp_Warning_DF)
        Error_DF_Final=pd.concat(Error_DF_List,ignore_index=True)
        Error_DF_Final = Error_DF_Final.groupby('ErrorMessage', as_index=False)['Frequency'].sum()
        Warning_DF_Final=pd.concat(Warning_DF_List,ignore_index=True)
        Warning_DF_Final=Warning_DF_Final.groupby('WarningMessage', as_index=False)['Frequency'].sum()
        return Warning_DF_Final, Error_DF_Final
    def PlotErrorRates(self,Prompt):
        Warning_DF, Error_DF=self.FileAnalysis()
        sns.barplot(x='ErrorMessage', y='Frequency', data=Error_DF)
        max_label_width = 20  # Set the maximum width for each line
        labels = [textwrap.fill(label, max_label_width) for label in Error_DF['ErrorMessage']]
        plt.xticks(range(len(labels)), labels, rotation=90, ha='right',fontsize=8)
        plt.title(f'{Prompt} Errors')
        plt.xlabel('Error Messages')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(f'./docs/{Prompt}_{datetime.today().date()}_ErrorPlot.png', format="png", dpi=300, bbox_inches="tight")
        plt.close()
    def PlotWarningRates(self,Prompt):
        Warning_DF, Error_DF=self.FileAnalysis()
        sns.barplot(x='WarningMessage', y='Frequency', data=Warning_DF)

        max_label_width = 20  # Set the maximum width for each line
        labels = [textwrap.fill(label, max_label_width) for label in Error_DF['WarningMessage']]
        plt.xticks(range(len(labels)), labels, rotation=90, ha='right')
        plt.title(f'{Prompt} Errors')
        plt.xlabel('Warning Messages')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(f'./docs/{Prompt}_{datetime.today().date()}_WarningPlot.png', format="png", dpi=300, bbox_inches="tight")
        plt.close()
    def QueryRunTimeAvgs(self,Prompt):
        Dict_LIST=[]
        for ele in self.subfolder_ids:
            file=individual_file_analysis(ele)
            RunTimeDict=file.Get_Query_Runtimes()
            Dict_LIST.append(RunTimeDict)
        Avg_Dict=DictAvgs(Dict_LIST)
        print(Avg_Dict)
        Instance_List = list(Avg_Dict.keys())
        RunTime_List = list(Avg_Dict.values())
        temp_dict = {'Instance': Instance_List, 'RunTime List': RunTime_List}
        RunTime_DF = pd.DataFrame(temp_dict)
        sns.lineplot(x='Instance', y='RunTime List', data=RunTime_DF)  # Changed 'df' to 'data'
        plt.title(f'{Prompt} Average LLM Query Time')
        plt.xlabel('Instance')
        plt.ylabel('Average Query Time')
        plt.savefig(f'./docs/{Prompt}_{datetime.today().date()}_QueryTimePlot.png', format="png", dpi=300, bbox_inches="tight")
        plt.close()
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
            fields='files(id, name)'
        ).execute()
        
        subfolders = results.get('files', [])
        all_json_contents = []

        for folder in subfolders:
            json_query = f"'{folder['id']}' in parents and mimeType='application/json'"
            json_results = drive_service.files().list(
                q=json_query,
                spaces='drive',
                fields='files(id, name, parents)',
                orderBy='createdTime'
            ).execute()
            
            json_files = json_results.get('files', [])
            
            # Download and read each JSON file's contents
            for json_file in json_files:
                file_id = json_file['id']
                request = drive_service.files().get_media(fileId=file_id)
                file_content = request.execute()
                json_content = json.loads(file_content)
                all_json_contents.append(json_content)

        return all_json_contents
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
    def ElaspedTime(self):
        ElaspedTime=[]
        instance=1
        for ele in self.JSON_Files:
            ElaspedTime.append(instance,ele['elapsed_time'])
            instance+=1
        return ElaspedTime
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
    

import pandas as pd
import traceback
import warnings
import contextlib
import io

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
            'warnings': self.warnings,
            'outputs': self.outputs
        }
Folder=Folder_Analysis('1B_8X6zNoSybJIlKCodb3cAKph3J0FGwH')
Folder.QueryRunTimeAvgs('Bouncing Balls')


if __name__=='__main__':
    Animation_Tests={'BouncingBalls':'1B_8X6zNoSybJIlKCodb3cAKph3J0FGwH',
                    'PlanetOrbitting':'1BTzPw7dXIbzUKxXyyWxcrwu8NWW_QcpW',
                    'QuiltFalling':'1MBPff_u8VDaGpyOj7XAudMvNydeVdn6w',
                    'DriveThroughWall':'1HL4x82wwIt2AAS19HbqlDeJnbPt7fRV4'}
    
    for key in Animation_Tests:
        Folder=Folder_Analysis(Animation_Tests[key])
        Warning_DF, Error_DF=Folder.FileAnalysis()
        Error_DF.to_csv(f'./docs/{key}_{datetime.today().date()}_ErrorFrequency.csv')
        Warning_DF.to_csv(f'./docs/{key}_{datetime.today().date()}_WarningFrequency.csv')
        Folder.PlotErrorRates(key)
        Folder.QueryRunTimeAvgs(key)


