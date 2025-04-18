# Cracker

Cracker is a desktop application built using Python and Tkinter that allows users to extract slides from a YouTube video. This tool helps in extracting key frames (slides) from videos, based on a given frame interval and similarity threshold, and generates a PDF from the extracted slides.

## Features

- **Extract Slides**: Extract slides from a YouTube video by specifying the URL, frame interval, and similarity threshold.
- **Generate PDF**: Generate a PDF document containing the extracted slides.
- **Progress Indicator**: Real-time progress updates while processing the video.

## Requirements

This application requires Python 3.x and the following dependencies:

- `tkinter` (for the GUI)
- `threading` (for background processing)
- `subprocess` (for video downloading)
- `Pillow` (for handling images)
- `reportlab` (for generating PDFs)
- `slide_extractor` (custom class for extracting slides from the video)

To install these dependencies, you can use the following command:

```bash
pip install pillow reportlab
```

Additionally, make sure you have the `slide_extractor.py` file, which contains the `SlideExtractor` class for the slide extraction logic.

## Setup Instructions

1. Clone or download the repository to your local machine.
2. Install the required Python libraries using the following:
   ```bash
   pip install pillow reportlab
   ```
3. Make sure the `slide_extractor.py` file is in the same directory as the script or correctly referenced.

## Usage

1. **Run the Application**: 
   Execute the following command to start the application:
   ```bash
   python slide_extractor_app.py
   ```

2. **Enter YouTube Video URL**: 
   Input the URL of the YouTube video from which you want to extract slides.

3. **Set Frame Interval**: 
   Define the frame interval (in seconds) at which the slides should be extracted.

4. **Set Similarity Threshold**: 
   Specify the similarity threshold (between 0.0 and 1.0) for detecting similar frames. A higher threshold (close to 1.0) means that only very similar frames will be selected.

5. **Extract Slides**: 
   Click the **Extract Slides** button to start the extraction process. The progress bar will show the current status of the operation.

6. **Generate PDF**: 
   Once the slides are extracted, you can click the **Generate PDF** button to create a PDF containing the extracted slides.
   
   You will be prompted to choose where to save the PDF.

## Notes

- Ensure that you have a stable internet connection to download YouTube videos.
- The extracted slides are saved to the `slides/` directory by default.
- If you encounter any errors, make sure the `SlideExtractor` class is implemented correctly and has all the necessary logic for downloading and extracting slides from the video.
