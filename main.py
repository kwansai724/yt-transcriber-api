from flask import Flask, request, jsonify
import subprocess
import uuid
import os
import openai
import shutil

openai.api_key = "OPENAI_API_KEY"
# Secretファイルのパス
SECRET_COOKIE_PATH = "/etc/secrets/cookies.txt"
WORKING_COOKIE_PATH = "cookies_working.txt"

app = Flask(__name__)

def download_audio(youtube_url, output_filename):
    shutil.copy(SECRET_COOKIE_PATH, WORKING_COOKIE_PATH)

    try:
        command = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "mp3",
            "--cookies", WORKING_COOKIE_PATH,
            "-o", output_filename,
            youtube_url
        ]
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout.decode())

    except subprocess.CalledProcessError as e:
        print("yt-dlp error:\n", e.stdout.decode())
        raise Exception("yt-dlp failed")

    finally:
        if os.path.exists(WORKING_COOKIE_PATH):
            os.remove(WORKING_COOKIE_PATH)

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

        os.remove(mp3_filename)

        return jsonify({"transcript": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    return "API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
