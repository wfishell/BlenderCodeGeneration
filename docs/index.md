<html>
<head>
    <title>Embed Videos Side by Side with Autoplay</title>
    <style>
        /* General Styles */
        h1, h2, h3 {
            text-align: center;
        }

        /* Video Container Styles */
        .video-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px; /* Space between videos */
        }

        .video-item {
            flex: 1 1 calc(50% - 20px); /* Each video item takes up 50% minus the gap */
            box-sizing: border-box;
        }

        .video-item video {
            width: 100%; /* Video fills its container */
            height: auto; /* Maintains aspect ratio */
            display: block;
        }

        /* Responsive Video Item for Smaller Screens */
        @media (max-width: 600px) {
            .video-item, .media-item {
                flex: 1 1 100%; /* Items stack vertically on small screens */
            }
        }

        /* Project Overview Section Styles */
        .section {
            margin-top: 40px;
            padding: 10px;
        }

        .section h2 {
            text-align: left;
            margin-bottom: 10px;
        }

        .section p {
            font-size: 16px;
            line-height: 1.6;
            text-align: justify;
        }

        /* Media Container Styles */
        .media-container {
            display: flex;
            gap: 20px; /* Space between items */
            margin-top: 20px;
            align-items: flex-start; /* Align items at the top */
        }

        .media-item {
            flex: 1 1 calc(50% - 20px); /* Each item takes up 50% minus the gap */
            box-sizing: border-box;
        }

        .media-item img,
        .media-item video {
            width: 100%; /* Media fills its container */
            height: auto; /* Maintains aspect ratio */
            display: block;
        }

        /* Responsive Styles */
        @media (max-width: 600px) {
            .media-item {
                flex: 1 1 100%; /* Items stack vertically on small screens */
            }
        }
    </style>
</head>
<body>
    <h1>Animation Generation Using Large Language Models</h1>
<div style="text-align: center;">
  <a href="KinographicPipeline.html" style="margin-right: 10px;">Kinographic Pipeline</a>
  <a href="CodeTemplate.html">Initial Code Template</a>
</div>
    <div class="video-container">
        <div class="video-item">
            <h2>Quilt Falling</h2>
            <video controls loop autoplay muted>
                <source src="QuiltFalling01Video.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>

        <div class="video-item">
            <h2>Orbits</h2>
            <video controls loop autoplay muted>
                <source src="Orbits01Video.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </div>

    <!-- Project Overview Section -->
    <div class="section">
        <h2>Project Overview</h2>
        <p>
            We are using large language models to generate animations in Blender by prompting the LLM to generate code 
            which is used to create the animation. We have developed an iterative pipeline that generates an animation, 
            then passes the finished product back into the LLM. The LLM critiques the animation based on how accurately 
            it represents the inputted prompt and then provides an updated prompt along with the generated code for the 
            next iteration of animation. This process offers clear insights into how LLMs can critique their own work 
            and use that information to improve. It also provides interesting results in how LLMs transition from a prompt 
            to the 3D space, showcasing their ability to handle the complexity of spatial and temporal reasoning in 3D environments.
        </p>
    </div>
    <!-- Code Template Section -->
    <div class="code-template-content">
        <h2>Initial Code Template</h2>
        <p>
            This initial code template that is fed into the LLM creates an object, camera, and light source. 
            This template helps the LLM in initializing code during the first iteration. Having the first iteration 
            generate a proper animation ensures that successive iterations have a solid foundation to build upon. 
        </p>
        <pre><code>
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
        </code></pre>
        <p>
            Since including this template code, we have seen an improvement in the quality of the generated animations. 
            These animations are more closely aligned with the prompt, have a lower number of errors, 
            and enable us to have a standard starting point for each animation, making the results more replicable.
        </p>
    </div>

    <!-- Kinographic Conversion Section -->
    <div class="Kinographic Feedback Loop">
        <h2>Kinographic Conversion</h2>
        <p>
            Many LLMs are not able to take in an mp4 video as an input, so we have created a feedback loop that inputs a kinograph. This 
            enables the LLM to critique its own work from each previous iteration. This loop has three steps:
        </p>
        <ol>
            <li>Take the previous iteration's animation and convert it into a kinograph.</li>
            <li>Input the previous animation's kinograph, the penultimate iteration's kinograph, and the original prompt into the LLM and compare which 
                animation better matches the original prompt.</li> 
            <li>Take the better performing animation and input it back into the LLM for feedback. This feedback is used to inform the next iteration's prompt.</li>
        </ol>
        <div class="media-container">
            <!-- Video Item with Title -->
            <div class="media-item">
                <h2>Animation</h2>
                <video controls loop autoplay muted>
                    <source src="PlanetaryOrbitAnimation_o1.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>

            <!-- Image Item with Title -->
            <div class="media-item">
                <h3>Kinograph</h3>
                <img src="OrbitsKinographFinal.png" alt="Kinograph Image">
                <p>
                    The animation is cut every 20 frames to create a sequence of images, which is then fed into the LLM. This is the process
                    by which the LLM is able to critique the animation.
                </p>
            </div>
        </div>
    </div>

<div class="LLM Decision">
    <h2>LLM Decision</h2>
    <p>
        Through this iterative process, the LLM needs to make a choice as to whether the previous iteration's animation was an improvement on the animation before it. 
        This decision prevents the LLM from regressing in quality over time, as we are constantly progressing the best performing animation and its associated code.
    </p>
    <pre>
        LLM Decision on the two previous iterations:
        #Set 2 refers to the the previous iteration's kinograph
        #Set 1 refers to the penultimate iteration's kinograph
        ```Set 2```

        The second set of images offers a clearer representation of a
        ball mid-bounce, showing its elevation above ground and then 
        returning back to the surface, which suggests motion more effectively
        than the first set. In Set 2, there is a more dynamic depiction with 
        visible changes in the ball’s height, supporting the theme of 'balls bouncing'. 
        This set also shows the ball at different heights, which better visualizes the 
        action of bouncing compared to the relatively static positioning in Set 1 where 
        the ball seems to make smaller, less noticeable movements. Set 2 captures the 
        essence of bounce through more apparent vertical motion.
    </pre>
<div class="media-container">
  <style>
    .media-container {
      display: flex;
    }
  </style>
  
  <div class="media-item" style="width: 50%;">
    <h2> Kinograph Feedback Flowchart</h2>
    <figure>
      <img src="Flowchart.png" alt="Kinograph Critique Flow Chart">
    </figure>
    <p>
      A kinograph is passed through to the LLM and critiqued against the original prompt, and this 
      updated prompt is used to generate the next iteration's code. This example depicts a bouncing 
      ball kinograph and the process of how it is critiqued.
    </p>
    <pre>
LLM Feedback on Animation:
To improve the animation and better fit the prompt, consider increasing the number of 
balls and introducing varied movement patterns and heights of the bounces to add more 
dynamism and interest to the animation.
    </pre>
  </div>
</div>
