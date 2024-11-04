# BlenderCodeGeneration
This is a program for generating Blender animations using LLMs. The current process is for the user to input a prompt and for the LLM to generate python which is rendered into an animation. We then splice the animation into a kinograph and pass it back to the LLM where it is iteratively called N times.

We are evaluating the effectiveness of LLMs with regards to spatial and temporal reasoning. Specifically we are using these prompts to test the effectiveness of LLMs in this space.

