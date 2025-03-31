from flask import Flask, request, jsonify
import subprocess
import uuid
import os
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

app = Flask(__name__)

def download_audio(youtube_url, output_filename):
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", output_filename,
        youtube_url
    ]
    subprocess.run(command, check=True)

def transcribe_with_whisper(audio_path):
    with open(audio_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
    return transcript["text"]

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    youtube_url = data.get("youtube_url")

    if not youtube_url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    try:
        file_id = str(uuid.uuid4())
        mp3_filename = f"{file_id}.mp3"

        download_audio(youtube_url, mp3_filename)
        text = transcribe_with_whisper(mp3_filename)

        os.remove(mp3_filename)  # 後始末

        return jsonify({"transcript": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
