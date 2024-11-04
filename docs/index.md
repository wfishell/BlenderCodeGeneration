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
            position: relative; /* Added for aspect ratio control */
            overflow: hidden;   /* Added to contain the video */
        }

        /* Enforce consistent aspect ratio */
        .video-item::before {
            content: '';
            display: block;
            padding-top: 56.25%; /* 16:9 Aspect Ratio */
        }

        .video-item video {
            position: absolute; /* Position the video absolutely within the container */
            top: 0;
            left: 0;
            width: 100%; /* Video fills its container */
            height: 100%; /* Ensures the video matches the container's height */
            object-fit: cover; /* Maintains aspect ratio and fills container */
        }

        /* Responsive Video Item for Smaller Screens */
        @media (max-width: 600px) {
            .video-item {
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

        /* Bouncing Balls Video Container Styles */
        .video-container.bouncing-balls {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px; /* Adjust gap as needed */
        }

        @media (max-width: 800px) {
            .video-container.bouncing-balls {
                grid-template-columns: repeat(2, 1fr); /* 2 columns on medium screens */
            }
        }

        @media (max-width: 600px) {
            .video-container.bouncing-balls {
                grid-template-columns: 1fr; /* Stack items vertically on small screens */
            }
        }
    </style>
</head>
<body>
    <h1>Animation Generation Using Large Language Models</h1>
    <div style="text-align: center;">
        <a href="https://github.com/wfishell/BlenderCodeGeneration" style="margin-right: 10px;">Github Repo</a>
        <a href="KinographicPipeline.html" style="margin-right: 10px;">Kinographic Pipeline</a>
        <a href="CodeTemplate.html">Initial Code Template</a>
    </div>
    <div class="video-container">
        <div class="video-item">
            <h2>Quilt Falling</h2>
            <video controls loop autoplay muted>
                <source src="QuiltFallingImprovedQuality.mp4" type="video/mp4">
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
            to the 3D space, showcasing their ability to handle the complexity of spatial and temporal reasoning in 3D environments. Note that we render these animations at 256p X 256p to reduce the run time of rendering, but this process also outputs the blender file enabeling a user to render at a higher resolution if desired. We are using 4 templates to test the effectivesness of our pipeline:
            <li>Create me a python script for a blender animation of a ball bouncing</li>
            <li>Create me a python script for a blender animation of a quilt falling onto a sphere"</li>
            <li>Create me a python script for an object driving through a wall</li>
            <li>Create me a python script for a blender animation of a Planets orbitting around the Sun</li>
        </p>
    </div>
    <div class="media-item">
        <h2>Animation Generation Pipeline Issues</h2>
        <img src="AnimationGenerationProcess.png" alt="Animation Generation Code Template">
    </div>
    <h1>Animation of Bouncing Balls Over Time</h1>
    <div class="video-container bouncing-balls">
        <div class="video-item">
            <h3>Bouncing Balls Animation After 1 Iterations</h3>
            <video autoplay loop muted>
                <source src="BouncingBalls/BouncingBallso10.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="video-item">
            <h3>Bouncing Balls Animation After 2 Iterations</h3>
            <video autoplay loop muted>
                <source src="BouncingBalls/BouncingBallso11.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="video-item">
            <h3>Bouncing Balls Animation After 3 Iterations</h3>
            <video autoplay loop muted>
                <source src="BouncingBalls/BouncingBallso12.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="video-item">
            <h3>Bouncing Balls Animation After 4 Iterations</h3>
            <video autoplay loop muted>
                <source src="BouncingBalls/BouncingBallso13.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="video-item">
            <h3>Bouncing Balls Animation After 5 Iterations</h3>
            <video autoplay loop muted>
                <source src="BouncingBalls/BouncingBallso14.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </div>
    <div class="media-item">
        <!-- Analysis Section -->
        <h2>Analysis</h2>
        <p>
            This is a simple animation of balls bouncing. The LLM makes key decisions about the speed of how the ball bounces, 
            how it is distorted by the ground, and the complexity of the overall animation which create more realism. While there 
            is still much to be desired from this animation, there is a clear changes in each succesive animation which can be tied back to
            the feedback provided at each instance.
        </p>
    </div>
    <div class="section">
        <h2>Issues</h2>
        <p>
            While this process has had success, there remain a few key issues with this framework that are creating difficulties with increasing the complexity in the animations generated:
            <li>There is randomness in the LLM's outputs which can cause variance in the output without any changes to the underlying code on our part. This is exemplified in instances of generating animations of orbits which vary from highly detailed animations to black screens because the camera was not initialized properly. </li>
            <li>The LLM often references functions and objects that don't exist. This causes errors which are fixed by recursively calling the function and passing in the failed code with the error to see if the LLM can fix itself. As the complexity of the prompt increases, the more the LLM tries to reference these nonexistent objects. We have specified a max recursive depth to prevent endless queries to the LLM but are still trying to figure out how to reduce these errors for more complex animations.</li>
        </p>
    </div>

