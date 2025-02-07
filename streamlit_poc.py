import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import yt_dlp
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the .env file!")

print("Groq API Key Loaded Successfully")

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

def download_audio_from_youtube(url, output_folder="downloads"):
    print(f"Downloading audio from URL: {url}")
    os.makedirs(output_folder, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, 'audio.%(ext)s'),
        'postprocessors': [],
        'ffmpeg_location': 'C:\\ProgramData\\chocolatey\\lib\\ffmpeg-full\\tools\\ffmpeg\\bin'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        audio_path = os.path.join(output_folder, 'audio.webm')
        if os.path.exists(audio_path):
            print(f"Audio file downloaded successfully: {audio_path}")
            return audio_path
    except Exception as e:
        print(f"Error downloading audio: {e}")
        st.error(f"Error downloading audio: {e}")
    return None

def transcribe_audio(file_path):
    print(f"Starting transcription for file: {file_path}")
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3-turbo",
            response_format="json",
            temperature=0.0
        )
    print("Transcription completed")
    return transcription.text if transcription else None

def split_transcription(text, words_per_chunk=70):
    words = text.split()
    chunks = [(i * 30, (i + 1) * 30, " \n" + " ".join(words[i:i + words_per_chunk]) + "\n") for i in range(0, len(words), words_per_chunk)]
    return chunks

def transliterate_tamil_to_tanglish(text):
    return transliterate(text, sanscript.TAMIL, sanscript.ITRANS)

# Streamlit UI
st.title("YouTube & Local Audio Transcription")

option = st.radio("Choose an option:", ["YouTube URL", "Upload Local File"])

audio_file_path = None
if option == "YouTube URL":
    youtube_url = st.text_input("Enter YouTube URL:", key="youtube_url")
    if youtube_url:
        st.info("Downloading and transcribing audio...")
        print(f"User entered YouTube URL: {youtube_url}")
        audio_file_path = download_audio_from_youtube(youtube_url)
        if audio_file_path:
            st.success("Audio downloaded successfully!")
            st.info("Transcribing...")
            transcription_text = transcribe_audio(audio_file_path)
            if transcription_text:
                st.success("Transcription Completed!")
                print("Displaying transcription in UI")
                chunks = split_transcription(transcription_text)
                transcription_display = "\n".join([f"{start}-{end} sec:\n{chunk}" for start, end, chunk in chunks])
                
                # Check if Tamil exists and create Tanglish version
                tanglish_text = transliterate_tamil_to_tanglish(transcription_text)
                tanglish_chunks = split_transcription(tanglish_text)
                tanglish_display = "\n".join([f"{start}-{end} sec:\n{chunk}" for start, end, chunk in tanglish_chunks])
                
                # Use columns to display the outputs side by side
                col1, col2 = st.columns([10, 10])
                with col1:
                    st.text_area("Transcription Output (Original):", transcription_display, height=400)
                with col2:
                    st.text_area("Transcription Output (Tanglish):", tanglish_display, height=400)
        else:
            st.error("Failed to download the audio.")
            
if option == "Upload Local File":
    uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "wav", "mp4", "webm"], key="file_uploader")
    if uploaded_file:
        temp_audio_path = os.path.join("downloads", uploaded_file.name)
        print(f"User uploaded file: {uploaded_file.name}")
        with open(temp_audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_file_path = temp_audio_path
        st.info("Transcribing...")
        transcription_text = transcribe_audio(audio_file_path)
        if transcription_text:
            st.success("Transcription Completed!")
            print("Displaying transcription in UI")
            chunks = split_transcription(transcription_text)
            transcription_display = "\n".join([f"{start}-{end} sec:\n{chunk}" for start, end, chunk in chunks])

            # Check if Tamil exists and create Tanglish version
            tanglish_text = transliterate_tamil_to_tanglish(transcription_text)
            tanglish_chunks = split_transcription(tanglish_text)
            tanglish_display = "\n".join([f"{start}-{end} sec:\n{chunk}" for start, end, chunk in tanglish_chunks])

            # Use columns to display the outputs side by side
            col1, col2 = st.columns([10, 10])
            with col1:
                st.text_area("Transcription Output (Original):", transcription_display, height=400)
            with col2:
                st.text_area("Transcription Output (Tanglish):", tanglish_display, height=400)
