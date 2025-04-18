import os
import cv2
import numpy as np
import subprocess
from PIL import Image
import pytesseract
from datetime import timedelta
import argparse
from skimage.metrics import structural_similarity as ssim

class SlideExtractor:
    def __init__(self, video_url, output_dir="slides", interval=5, similarity_threshold=0.9, ocr_confidence=30):
        self.video_url = video_url
        self.output_dir = output_dir
        self.interval = interval
        self.similarity_threshold = similarity_threshold
        self.ocr_confidence = ocr_confidence
        self.video_path = os.path.join(self.output_dir, "temp_video.mp4")
        self.previous_text = ""

        os.makedirs(self.output_dir, exist_ok=True)

    def download_video(self):
        """Download the YouTube video using yt-dlp"""
        try:
            command = [
                "yt-dlp",
                "-f", "best[ext=mp4]",
                "-o", self.video_path,
                self.video_url
            ]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Video downloaded to: {self.video_path}")
                return True
            else:
                print(f"yt-dlp error:\n{result.stderr}")
                return False
        except Exception as e:
            print(f"Error downloading video: {e}")
            return False

    def extract_slides(self):
        """Process the video to extract slides"""
        if not os.path.exists(self.video_path):
            if not self.download_video():
                return False

        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * self.interval)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        print(f"Video duration: {timedelta(seconds=duration)}")
        print(f"Processing frames every {self.interval} seconds...")

        prev_frame = None
        slide_count = 0

        for frame_num in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if not ret:
                continue

            current_time = frame_num / fps
            timestamp = str(timedelta(seconds=current_time)).split(".")[0]

            if prev_frame is None:
                self._save_slide(frame, timestamp, slide_count)
                prev_frame = frame
                slide_count += 1
                continue

            if self._is_different_slide(prev_frame, frame):
                self._save_slide(frame, timestamp, slide_count)
                prev_frame = frame
                slide_count += 1

        cap.release()
        print(f"Extracted {slide_count} slides to {self.output_dir}")
        return True

    def _is_different_slide(self, frame1, frame2):
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        similarity, _ = ssim(gray1, gray2, full=True)
        if similarity < self.similarity_threshold:
            return True

        text1 = self._extract_text(frame1)
        text2 = self._extract_text(frame2)

        if text1 and text2:
            words1 = set(text1.split())
            words2 = set(text2.split())
            common_words = words1.intersection(words2)
            diff_ratio = 1 - len(common_words) / max(len(words1), len(words2))

            if diff_ratio > 0.3:
                return True

        return False

    def _extract_text(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            temp_image_path = os.path.join(self.output_dir, "temp_ocr.png")
            cv2.imwrite(temp_image_path, threshold)

            text = pytesseract.image_to_string(Image.open(temp_image_path), config='--psm 6')
            return text.strip()
        except Exception as e:
            print(f"OCR error: {e}")
            return ""

    def _save_slide(self, frame, timestamp, count):
        filename = f"slide_{count:03d}_{timestamp.replace(':', '-')}.png"
        path = os.path.join(self.output_dir, filename)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        pil_image.save(path)
        print(f"Saved slide: {filename}")

    def convert_slides_to_pdf(self, pdf_name="slides_output.pdf"):
        """Convert all extracted slides to a single PDF file."""
        image_files = sorted([
            os.path.join(self.output_dir, file)
            for file in os.listdir(self.output_dir)
            if file.lower().endswith(".png") and file.startswith("slide_")
        ])

        if not image_files:
            print("No slide images found to convert.")
            return

        images = [Image.open(img).convert("RGB") for img in image_files]
        pdf_path = os.path.join(self.output_dir, pdf_name)
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        print(f"PDF created at: {pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract slides from educational YouTube videos")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output", default="slides", help="Output directory for slides")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between frame checks")
    parser.add_argument("--threshold", type=float, default=0.9, help="Similarity threshold")
    args = parser.parse_args()

    extractor = SlideExtractor(
        video_url=args.url,
        output_dir=args.output,
        interval=args.interval,
        similarity_threshold=args.threshold
    )

    if extractor.extract_slides():
        print("Slide extraction completed successfully!")
        extractor.convert_slides_to_pdf()
    else:
        print("Slide extraction failed.")


if __name__ == "__main__":
    main()
