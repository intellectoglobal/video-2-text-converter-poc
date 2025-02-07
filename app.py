import os
from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import yt_dlp

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure the API key is available
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the .env file!")

# Initialize the Groq client with the API key
client = Groq(api_key=GROQ_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# Function to download YouTube video and extract audio
def download_audio_from_youtube(url, output_folder="downloads"):
    print("Starting download of audio from YouTube...")
    os.makedirs(output_folder, exist_ok=True)

    # Set options to download only audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, 'audio.%(ext)s'),
        'postprocessors': [],
        'ffmpeg_location': 'C:\\ProgramData\\chocolatey\\lib\\ffmpeg-full\\tools\\ffmpeg\\bin\\ffmpeg.exe',  # Updated path
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed. Audio extracted.")
    except Exception as e:
        print(f"Error downloading audio: {e}")
    
    # Construct the full path to the audio file
    audio_path = os.path.join(output_folder, 'audio.webm')
    
    # Check if the file exists
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        return None
    
    return audio_path

# Route to upload YouTube URL
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        youtube_url = request.form["youtube_url"]
        if youtube_url:
            try:
                # Download audio from YouTube
                audio_filename = download_audio_from_youtube(youtube_url)
                
                if audio_filename:
                    print(f"Audio file downloaded and saved as: {audio_filename}")

                    # Open the audio file for transcription
                    with open(audio_filename, "rb") as file:
                        print("Sending audio file for transcription...")
                        transcription = client.audio.transcriptions.create(
                            file=(audio_filename, file.read()),  # Required audio file
                            model="whisper-large-v3-turbo",  # Required model to use for transcription
                            prompt="Specify context or spelling",  # Optional
                            response_format="json",  # Optional
                            temperature=0.0  # Optional
                        )

                    # Access the transcription text directly
                    full_text = transcription.text  # Full transcription text
                    print("Transcription completed.")

                    # Approximate splitting into 30-second chunks
                    words = full_text.split()  # Split the transcription into words
                    words_per_30_sec = 70  # Approximate number of words in 30 seconds (adjust as needed)

                    # Create a directory to save the output text files
                    output_dir = os.path.join(os.path.dirname(__file__), "transcription_chunks")
                    os.makedirs(output_dir, exist_ok=True)

                    # Split and save chunks
                    for i in range(0, len(words), words_per_30_sec):
                        chunk_text = " ".join(words[i:i + words_per_30_sec])  # Get the next 30-second chunk
                        chunk_filename = os.path.join(output_dir, f"chunk_{i // words_per_30_sec + 1}.txt")

                        # Write the chunk to a text file
                        with open(chunk_filename, "w", encoding="utf-8") as f:
                            f.write(chunk_text)

                    return jsonify({"transcription": full_text, "chunks_saved": len(words) // words_per_30_sec})
                else:
                    return jsonify({"error": "Audio file not found. Skipping transcription."})
            except Exception as e:
                return jsonify({"error": str(e)})
        else:
            return jsonify({"error": "No URL provided."})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
