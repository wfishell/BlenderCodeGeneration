# BlenderCodeGeneration
A simple program for generating blender images and animations and then uploading them to google drive where they can be rendered in google collab
This program is made up of 2 main classes animationgeneration, and UploadFile. The animaiton generation class creates an object which gets a prompt and a file path and then creates a blender file which is then uploaded to a google drive folder. 

Currently there is a choke point in rendering the images in one pipeline. Specifically, rendering animations and images locally takes a very long amount of time, so I am using a google collab notebook and leveaging the gpu resoures to render these images which greatly speeds up the process. The main blocker is that I have not found a way of easily triggering the google colab notebook to automatically run when the main python file is run so currently it is a two step process. I hope to change that blocker soon. 
