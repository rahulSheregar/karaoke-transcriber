import os
import subprocess
import whisper
import argparse
import srt
import logging

from datetime import timedelta
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Audio:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path: str) -> List[Dict[str, Any]]:
        """Transcribe audio to text using Whisper."""
        logger.info("Transcribing with Whisper...")
        try:
            result = self.model.transcribe(audio_path, word_timestamps=True)
            return result['segments']
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    @staticmethod
    def extract(video_path: str, audio_path: str) -> None:
        """Extract audio from video using ffmpeg."""
        logger.info("Extracting audio...")
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1", audio_path
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error extracting audio: {e}")
            raise


class Subtitle:
    @staticmethod
    def generate(segments: List[Dict[str, Any]], srt_path: str) -> None:
        """Generate SRT subtitles from segments."""
        logger.info("Generating SRT...")
        subtitles = []
        index = 1
        for seg in segments:
            for word_info in seg["words"]:
                start = timedelta(seconds=word_info["start"])
                end = timedelta(seconds=word_info["end"])
                content = word_info["word"]
                subtitles.append(
                    srt.Subtitle(
                        index=index, start=start,
                        end=end, content=content.strip()
                    )
                )
                index += 1

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt.compose(subtitles))

    @staticmethod
    def burn(video_path: str, srt_path: str, output_path: str) -> None:
        """Burn subtitles into video using ffmpeg."""
        logger.info("Burning subtitles into video...")
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"subtitles={srt_path}",
            "-c:a", "copy", output_path
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error burning subtitles: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Karaoke subtitle generator")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--output", default="output.mp4", help="Output video file path")
    args = parser.parse_args()

    input_video = args.input
    output_video = args.output

    temp_dir = "build"
    os.makedirs(temp_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(input_video))[0]

    audio_path = os.path.join(temp_dir, f"{base}_audio.wav")
    srt_path = os.path.join(temp_dir, f"{base}.srt")

    try:
        audio = Audio()
        audio.extract(input_video, audio_path)
        segments = audio.transcribe(audio_path)
        Subtitle.generate(segments, srt_path)
        Subtitle.burn(input_video, srt_path, output_video)
        logger.info(f"Done! Video saved to: {output_video}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
