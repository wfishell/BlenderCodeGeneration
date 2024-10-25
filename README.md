# BlenderCodeGeneration
This is a program for generating Blender animations using LLMs. The current process is for the user to input a prompt and for the LLM to generate python which is rendered into an animation. We then splice the animation into a kinograph and pass it back to the LLM where it is iteratively called N times.

We are evaluating the effectiveness of LLMs with regards to spatial and temporal reasoning. Specifically we are using these prompts to test the effectiveness of LLMs in this space.
"Prompt": "Create me a python script for a blender animation of a quilt falling onto a sphere use color"

"Prompt": "Create me a python blender script of an animation of planets orbitting the sun "
"Prompt": "Create me a python script for a blender animation of balls bouncing"
"Prompt": "Create me a python script for a blender animation of an object going through a wall"

Currently there is a choke point in rendering the images in one pipeline. Specifically, rendering animations and images locally takes a very long amount of time, so I am using a google collab notebook and leveaging the gpu resoures to render these images which greatly speeds up the process. The main blocker is that I have not found a way of easily triggering the google colab notebook to automatically run when the main python file is run so currently it is a two step process. I hope to change that blocker soon. 
