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
    <div class="media-item">
        <h2>Animation Generation Pipeline</h2>
        <img src="AnimationGenerationProcess.png" alt="Animation Generation Code Template">
    </div>
    </div>
