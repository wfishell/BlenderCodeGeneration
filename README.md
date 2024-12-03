# BlenderCodeGeneration

https://github.com/wfishell/BlenderCodeGeneration

This is a program for generating Blender animations using LLMs. The current process is for the user to input a prompt and for the LLM to generate python which is rendered into an animation. We then splice the animation into a kinograph and pass it back to the LLM where it is iteratively called N times.

We are evaluating the effectiveness of LLMs with regards to spatial and temporal reasoning. Specifically we are using these prompts to test the effectiveness of LLMs in this space.

Installing and running the code.
In order to render your own animaitons you will need access to a GPU. Without one you will not be able to 
properly render animations. 

Without loss of generality we will use the example gpu SSH username@remote-server-address for this example with password: password
Furthermore this example uses VSCode for interfacing with the GPU. If you are using a different IDE
or are not using an external GPU instructions may differ

Cloning Repo
1. SSH into your GPU and clone the repo
2. Once cloned you will need will have a directory called BlenderCodeGeneration

Interfacing with repo
3.  you will need to install Remote-SSH extension for VSCode. look in extensions and install this
4. Configure your SSH for easy access. You will be prompted to input your username:
username@remote-server-address and password: password at this point
5. navigate through folders and open BlenderCodeGeneration Folder.
6. Navigate to Packages.py and input your openai API secret key. Note you will need to ensure your key has access to the model version you are using in the AnimationGeneration.py. If you are using the basic verison, you will have access to everything excluding the most recent o1 model. Modify and save python files accordingly.

Running and setting up the code
7. You will now need to install the correct version of blender. Any version from 4.0-4.3 will be compatiable with code generated. On linux, to get 4.3.0 you can run ```sudo snap install blender --classic```
8. install all nessacary other packages by running pip install -r requirements.txt
9. Now that you have set the code up to run you can create a prompt for an animation and a folder name by editing lines 7 and 9 respectively. Please note the folder name shouldn't have spaces in it, and the prompt should follow the format Create me a python scripy for a blender animation of BLANK.
10. Outputted code, blender files and a copy of subsequent animations will be outputted at this link
https://drive.google.com/drive/folders/1VYfJiunHJ8i8JPQIN5IIp8ISr9jp7ni8?usp=sharing
