from Packages import *
from Iterator import *
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
            json.dump(self.json_file, file, indent=4)
        fileupload = UploadFile(prompt_file)
        fileupload.upload_file_to_drive(fileupload.filename, fileupload.filename, "application/json", SubFolderID)
        print('Killing File')
    def chat_with_LLM(self, text_prompt,Kill_Function=0):
        if Kill_Function == 4:
            #At the 4th iteration the text prompt will be the code
            self.ErrorLog(text_prompt)
            print('Max Number of OpenAI Calls reached. Consider adjusting prompt or code')
            return None, None
        try:
            gpt_query_start_time=time.time()
            # Send request to OpenAI's API
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"{text_prompt}."
                            f"Use {self.TemplateCode} as a general template to improve the quality of the animation "
                            f"Return the code enclosed in triple backticks like ``` at both the start and end of the code section. "
                            f"Lastly, always save it as a blend file to this path {self.filename}"
                            f"Do not include anything in the code that assigns a resolution to the render or renders the images"
                            f"assume no objects or functions have been created."
                            f"Do not use a main() class and avoid attribute errors."
                            f"Do not use the cell_fracture_operator"
                            f"If the cell_fracture_operator is not found, try using 'object.add_fracture_cell_objects' instead."
                            f"Always check if an add-on or operator exists before using it."
                            f"Provide alternative methods or error handling if certain operations fail."
                        ),
                    },
                ],
                max_completion_tokens=10000,

            )
            gpt_query_end_time=time.time()
            self.json_file[f'gpt_query_time_{Kill_Function}']=gpt_query_end_time-gpt_query_start_time

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

                        moving_objects = []

                        # Threshold to determine if an object has moved (can be set to 0)
                        threshold = 0.0001

                        # Iterate over all objects in the scene
                        for obj in bpy.context.scene.objects:
                            if obj.type not in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'EMPTY'}:
                                continue  # Skip cameras, lights, etc.

                            # Exclude specific objects if needed (e.g., the Sun)
                            if obj.name == 'Sun':
                                continue

                            # Sample the object's world location at the start and end frames
                            scene.frame_set(inicio)
                            start_loc = obj.matrix_world.to_translation().copy()
                            scene.frame_set(fin)
                            end_loc = obj.matrix_world.to_translation().copy()

                            # Check if the object has moved
                            if (start_loc - end_loc).length > threshold:
                                moving_objects.append(obj)

                        # Reset to the original frame
                        scene.frame_set(actual)

                        # Generate motion paths for the moving objects
                        for obj in moving_objects:
                            print(f"Creating motion path for: {obj.name}")
                            recorrido = bpy.data.curves.new(f'recorrido_{obj.name}', 'CURVE')
                            curva = bpy.data.objects.new(f'curva_{obj.name}', recorrido)
                            bpy.context.scene.collection.objects.link(curva)
                            recorrido.dimensions = '3D'

                            # Give the curve some thickness so it's visible in the render
                            recorrido.bevel_depth = 0.05  # Adjust thickness as needed
                            recorrido.bevel_resolution = 4  # Increase for smoother curves

                            # Create and assign material to the curve
                            material = bpy.data.materials.new(name=f"Material_{curva.name}")
                            material.use_nodes = True
                            nodes = material.node_tree.nodes
                            links = material.node_tree.links

                            # Remove default Principled BSDF
                            principled_bsdf = nodes.get('Principled BSDF')
                            if principled_bsdf:
                                nodes.remove(principled_bsdf)

                            # Add Emission shader to make the path glow
                            emission_node = nodes.new(type='ShaderNodeEmission')
                            emission_node.inputs['Color'].default_value = (1, 0, 0, 1)  # Red color
                            emission_node.inputs['Strength'].default_value = 5

                            output_node = nodes.get('Material Output')
                            links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

                            curva.data.materials.append(material)

                            spline = recorrido.splines.new('BEZIER')
                            spline.bezier_points.add(len(puntos) - 1)

                            for c, n in enumerate(puntos):
                                scene.frame_set(n)
                                matrix = obj.matrix_world.copy()
                                nodo = spline.bezier_points[c]
                                nodo.co = matrix.to_translation()
                                nodo.handle_right_type = 'AUTO'
                                nodo.handle_left_type = 'AUTO'

                            # Optionally, parent the curve to the object
                            # curva.parent = obj

                        # Reset the frame to the current frame
                        scene.frame_set(actual)

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
                        render_start_time=time.time()
                        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
                        bpy.ops.render.render(animation=True)
                        render_end_time=time.time()
                        self.json_file[f'render_time_{Kill_Function}']=render_end_time-render_start_time
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
            try:
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
            except Exception as e:
                self.json_file[f'GPT_Query_Bug_{Kill_Function}']='failed to extract code from LLM'
                Kill_Function_Updated=Kill_Function+1
                return self.chat_with_LLM(self.prompt,Kill_Function_Updated)                
