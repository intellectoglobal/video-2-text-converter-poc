import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import yt_dlp
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re

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
    chunks = []
    start_time = 0
    while start_time < len(words):
        end_time = start_time + words_per_chunk
        chunk_text = " \n" + " ".join(words[start_time:end_time]) + "\n"
        chunks.append((start_time, end_time, chunk_text))
        start_time = end_time
    return chunks

def transliterate_tamil_to_tanglish(text):
    return transliterate(text, sanscript.TAMIL, sanscript.ITRANS)

# Function to check if text contains Tamil characters
def contains_tamil(text):
    tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
    return bool(tamil_pattern.search(text))

# Function to delete the file
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file: {e}")
        st.error(f"Error deleting file: {e}")

# Custom CSS for styling
st.markdown("""
    <style>
        .main {background-color: #f9f9f9;}
        .stRadio > div {flex-direction:row;}
        .stTextArea label {font-weight: bold; color: #2e5266;}
        .stAlert {border-radius: 10px;}
        .title-text {font-size: 2.5em; color: #2e5266; text-align: center; 
                     margin-bottom: 20px; font-weight: bold;
                     text-shadow: 2px 2px 4px #d3d3d3;}
        .sidebar .sidebar-content {background-color: #e1e8f0;}
        .transcription-box {border: 2px solid #2e5266; border-radius: 10px; 
                           padding: 20px; margin: 10px 0;}
        .highlight {color: #2e5266; font-weight: bold;}
        .footer {text-align: center; padding: 15px; color: #666; 
                position: fixed; bottom: 0; width: 100%;}
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<p class="title-text">🎙️ Audio Transcription Studio</p>', 
            unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Settings")
    option = st.radio("Input Source:", ["YouTube URL", "Local File Upload"], 
                     help="Choose your audio source")

# Main Content Area
main_container = st.container()

with main_container:
    if option == "YouTube URL":
        with st.form("youtube_form"):
            youtube_url = st.text_input("Enter YouTube URL:", 
                                        placeholder="https://youtube.com/watch?v=...",
                                        help="Paste a YouTube video URL here")
            submitted = st.form_submit_button("🚀 Start Transcription")
            
            if submitted and youtube_url:
                with st.status("🔍 Processing...", expanded=True) as status:
                    st.write("📥 Downloading audio from YouTube...")
                    audio_file_path = download_audio_from_youtube(youtube_url)
                    if audio_file_path:
                        st.write("🔊 Transcribing audio...")
                        transcription_text = transcribe_audio(audio_file_path)
                        status.update(label="✅ Transcription Complete!", 
                                     state="complete", expanded=False)
                        delete_file(audio_file_path)

    else:
        with st.form("upload_form"):
            uploaded_file = st.file_uploader("Choose an audio file", 
                                            type=["mp3", "wav", "mp4", "webm"],
                                            help="Supports MP3, WAV, MP4, WEBM")
            submitted = st.form_submit_button("🚀 Start Transcription")
            
            if submitted and uploaded_file:
                with st.status("🔍 Processing...", expanded=True) as status:
                    st.write("📤 Uploading file...")
                    temp_audio_path = os.path.join("downloads", uploaded_file.name)
                    with open(temp_audio_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.write("🔊 Transcribing audio...")
                    transcription_text = transcribe_audio(temp_audio_path)
                    status.update(label="✅ Transcription Complete!", 
                                 state="complete", expanded=False)
                    delete_file(temp_audio_path)

    # Display Results
    if 'transcription_text' in locals():
        st.subheader("📝 Transcription Results")
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Original Text", "Tanglish Translation"])
        
        with tab1:
            chunks = split_transcription(transcription_text)
            transcription_display = "\n".join(
                [f"⏱️ {start}-{start+30}s:\n{chunk}" 
                 for start, end, chunk in chunks]
            )
            st.code(transcription_display, language="text")
            
        with tab2:
            if contains_tamil(transcription_text):
                tanglish_text = transliterate_tamil_to_tanglish(transcription_text)
                tanglish_chunks = split_transcription(tanglish_text)
                tanglish_display = "\n".join(
                    [f"⏱️ {start}-{start+30}s:\n{chunk}" 
                     for start, end, chunk in tanglish_chunks]
                )
                st.code(tanglish_display, language="text")
            else:
                st.info("🔍 No Tamil text detected for transliteration")

# Footer
st.markdown("---")
st.markdown('<div class="footer">🎉 Powered by Groq & Streamlit | Made with ❤️ by Your Name</div>', 
            unsafe_allow_html=True)