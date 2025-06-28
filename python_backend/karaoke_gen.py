import os
import subprocess
import whisper
import argparse
import srt
from datetime import timedelta

def extract_audio(video_path, audio_path):
    print("Extracting audio...")
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
    ]
    subprocess.run(command, check=True)

def transcribe_audio(audio_path):
    print("Transcribing with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True)
    return result['segments']

def segments_to_srt(segments, srt_path):
    print("Generating SRT...")
    subtitles = []
    index = 1
    for seg in segments:
        for word_info in seg["words"]:
            start = timedelta(seconds=word_info["start"])
            end = timedelta(seconds=word_info["end"])
            content = word_info["word"]
            subtitles.append(srt.Subtitle(index=index, start=start, end=end, content=content.strip()))
            index += 1

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subtitles))

def burn_subtitles(video_path, srt_path, output_path):
    print("Burning subtitles into video...")
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"subtitles={srt_path}",
        "-c:a", "copy", output_path
    ]
    subprocess.run(command, check=True)

def main():
    parser = argparse.ArgumentParser(description="Karaoke subtitle generator")
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--output", default="output.mp4", help="Output video file path")
    args = parser.parse_args()

    input_video = args.input
    output_video = args.output
    base = os.path.splitext(os.path.basename(input_video))[0]

    audio_path = f"{base}_audio.wav"
    srt_path = f"{base}.srt"

    extract_audio(input_video, audio_path)
    segments = transcribe_audio(audio_path)
    segments_to_srt(segments, srt_path)
    burn_subtitles(input_video, srt_path, output_video)

    print(f"Done! Video saved to: {output_video}")

if __name__ == "__main__":
    main()
