GuPie Video: AI Video Flow & Branding Analyzer
GuPie Video is a specialized desktop application designed to evaluate the effectiveness of video content—specifically for marketing and social media. By extracting keyframes from the Start, Middle, and End of a video, it uses Google Gemini AI to analyze storytelling flow, product focus, and brand recall.

Key Features

Triple-Frame Extraction: Automatically captures the 1st frame (Intro), middle frame (Development), and last frame (Outro/Logo) for a holistic view of the video.
Strategic AI Analysis: Uses a custom prompt to evaluate:
Introduction: Is the hook strong enough?
Development: Is the focus maintained on the product?
Conclusion: Is the brand/logo visible and memorable?
Gemini Flash Integration: Leverages the gemini-flash-latest model for fast and cost-effective multimodal analysis.
Visual Feedback: Displays all three captured frames in the UI before processing to ensure the extraction was successful.
Safe Analysis: Implements BLOCK_NONE safety settings to prevent false-positive content filtering during professional analysis.

Installation
Install dependencies:
Bash
pip install google-generativeai pillow numpy opencv-python matplotlib
API Key: Open GuPie_Video - V2.py and replace API_KEY = "apı key" with your actual Google AI Studio key.

How it Works
Load Video: Select an MP4, AVI, or MOV file.
Auto-Preview: The app automatically finds the beginning, middle, and end frames and displays them on your screen.
Analyze: The AI looks at these three images together to understand the "narrative arc."
Actionable Insights: It provides an "Improvement Summary" to help editors and marketers optimize their videos for better brand retention.

Comparison with Standard GuPie
While the standard GuPie tool is for batch image description, this version is built for video strategy. It treats the video as a story rather than just a collection of pixels.

Technologies
OpenCV (cv2): Used for precise frame seeking and extraction.
Tkinter: Lightweight GUI for desktop use.
Pillow (PIL): Image formatting for AI input.
Google Gemini API: Multimodal LLM for visual reasoning.
