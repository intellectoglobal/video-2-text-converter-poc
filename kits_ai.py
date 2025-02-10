import os
import requests
import yt_dlp as youtube_dl  # Use yt-dlp instead of youtube-dl
from pydub import AudioSegment

def download_audio_from_youtube(url, output_path="downloads"):
    print(f"Downloading audio from YouTube: {url}")
    ydl_opts = {
        'format': 'bestaudio/best',
        # 'outtmpl': output_path,  # Output the downloaded audio as "audio.mp3"
        'outtmpl': os.path.join(output_path, 'audio.%(ext)s'),  # Output the downloaded audio as "audio.mp3"
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Audio downloaded and saved as {output_path}")
    except Exception as e:
        print(f"Error downloading audio: {e}")

# def remove_vocals(input_file, output_file="vocals_removed.wav"):
#     kits_ai_url = "https://kits-ai.example.com/vocalremover"  # Replace with actual Kits AI API URL
#     try:
#         print(f"Sending {input_file} for vocal removal...")
#         with open(input_file, 'rb') as audio_file:
#             files = {'file': audio_file}
#             response = requests.post(kits_ai_url, files=files)
        
#         if response.status_code == 200:
#             with open(output_file, 'wb') as out_file:
#                 out_file.write(response.content)
#             print(f"Vocals removed, saved as {output_file}")
#         else:
#             print(f"Error in vocal removal: {response.text}")
#     except Exception as e:
#         print(f"Error in vocal removal: {e}")

# def transcribe_with_whisper(input_file):
#     whisper_ai_url = "https://whisperai.example.com/transcribe"  # Replace with actual Whisper AI API URL
#     try:
#         print(f"Sending {input_file} to Whisper AI for transcription...")
#         with open(input_file, 'rb') as audio_file:
#             files = {'file': audio_file}
#             response = requests.post(whisper_ai_url, files=files)
        
#         if response.status_code == 200:
#             transcription = response.json().get("text")
#             print(f"Transcription: {transcription}")
#         else:
#             print(f"Error in transcription: {response.text}")
#     except Exception as e:
#         print(f"Error in transcription: {e}")

def process_audio(input_url_or_file):
    print(f"Processing input: {input_url_or_file}")
    
    # If it's a YouTube URL, download the audio
    # if input_url_or_file.startswith("http") and "youtube" in input_url_or_file:
    print("Detected YouTube URL. Downloading audio...")
    download_audio_from_youtube(input_url_or_file)
    input_file = "audio.mp3"
    # else:
    #     print("Using local file.")
    #     input_file = input_url_or_file

    # # Remove vocals
    # print(f"Starting vocal removal for {input_file}")
    # remove_vocals(input_file)

    # # Transcribe the vocals removed audio
    # vocals_removed_file = "vocals_removed.wav"
    # print(f"Starting transcription for {vocals_removed_file}")
    # transcribe_with_whisper(vocals_removed_file)

# Example usage
input_url_or_file = "https://youtu.be/X-MZXIXPwFw?si=3MWuXHXaV3WrY4xn"  # Or use a local file path
process_audio(input_url_or_file)
