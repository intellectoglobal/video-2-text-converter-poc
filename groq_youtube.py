import os
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

# Function to download YouTube video and extract audio
def download_audio_from_youtube(url, output_folder="downloads"):
    print("Starting download of audio from YouTube...")
    os.makedirs(output_folder, exist_ok=True)

    # Set options to download only audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, 'audio.%(ext)s'),
        'postprocessors': [],  # Disable post-processing step
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


# Specify the YouTube video URL
youtube_url = "https://youtu.be/kJQP7kiw5Fk?si=cFbdj2fH1u40s1S0"  # Replace with your video URL
print(f"Video URL: {youtube_url}")

try:
    # Download audio from YouTube
    audio_filename = download_audio_from_youtube(youtube_url)
    
    if audio_filename:
        print(f"Audio file downloaded and saved as: {audio_filename}")

        # Open the audio file
        with open(audio_filename, "rb") as file:
            print("Sending audio file for transcription...")
            # Create a transcription of the audio file
            transcription = client.audio.transcriptions.create(
                file=(audio_filename, file.read()),  
                model="whisper-large-v3-turbo",  # Required model to use for transcription
                prompt="Specify context or spelling",  # Optional
                response_format="json",  # Optional
                # language="en",  # Optional
                temperature=0.0  # Optional
            )

        # Access the transcription text directly
        full_text = transcription.text  # Full transcription text
        print("Transcription completed. Processing text...")

        # Approximate splitting into 30-second chunks
        words = full_text.split()  # Split the transcription into words
        words_per_30_sec = 70  # Approximate number of words in 30 seconds (adjust as needed)

        # Create a directory to save the output text files
        output_dir = os.path.join(os.path.dirname(__file__), "transcription_chunks")
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory created at: {output_dir}")

        # Split and save chunks
        for i in range(0, len(words), words_per_30_sec):
            chunk_text = " ".join(words[i:i + words_per_30_sec])  # Get the next 30-second chunk
            chunk_filename = os.path.join(output_dir, f"chunk_{i // words_per_30_sec + 1}.txt")

            # Write the chunk to a text file
            with open(chunk_filename, "w", encoding="utf-8") as f:
                f.write(chunk_text)
            print(f"Chunk {i // words_per_30_sec + 1} saved to: {chunk_filename}")

        print(f"Transcription chunks saved in '{output_dir}'.")
    else:
        print("Audio file not found. Skipping transcription.")

except Exception as e:
    print("Error:", e)
