import os
from demucs import pretrained
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure the API key is available
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the .env file!")

# Initialize the Groq client with the API key
client = Groq(api_key=GROQ_API_KEY)

# Load the pre-trained Demucs model (v3)
model = pretrained.get_model("demucs")

def separate_audio_with_demucs(audio_path):
    """Separate vocals and instrumental from the audio file using Demucs"""
    output_dir = os.path.join(os.path.dirname(audio_path), 'separated')
    os.makedirs(output_dir, exist_ok=True)

    # Separate the audio using Demucs
    model.separate(audio_path, output_dir)
    
    # Return the paths for vocals and instrumental
    vocal_path = os.path.join(output_dir, os.path.basename(audio_path).replace(".mp3", "/vocals.wav"))
    instrumental_path = os.path.join(output_dir, os.path.basename(audio_path).replace(".mp3", "/accompaniment.wav"))
    
    return vocal_path, instrumental_path

# Specify the path to the audio file (update this to your file)
filename = os.path.join(os.path.dirname(__file__), "Ed Sheeran - Shape Of You.mp3")  # Ensure demo.mp3 exists!

try:
    # Separate vocals and instrumental using Demucs
    vocal_path, instrumental_path = separate_audio_with_demucs(filename)
    print(f"Vocal audio saved at: {vocal_path}")
    print(f"Instrumental audio saved at: {instrumental_path}")

    # Send the instrumental audio to Groq for transcription
    with open(instrumental_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(instrumental_path, audio_file.read()),  # Send instrumental file to API
            model="whisper-large-v3-turbo",  # Required model for transcription
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            temperature=0.0  # Optional
        )

    # Access the transcription text
    full_text = transcription.text
    print("Transcription completed.")

    # Approximate splitting into 30-second chunks
    words = full_text.split()
    words_per_30_sec = 70

    # Create a directory to save the output text files
    output_dir = os.path.join(os.path.dirname(__file__), "transcription_chunks")
    os.makedirs(output_dir, exist_ok=True)

    # Split and save chunks
    for i in range(0, len(words), words_per_30_sec):
        chunk_text = " ".join(words[i:i + words_per_30_sec])
        chunk_filename = os.path.join(output_dir, f"chunk_{i // words_per_30_sec + 1}.txt")
        
        # Write each chunk to a text file
        with open(chunk_filename, "w", encoding="utf-8") as chunk_file:
            chunk_file.write(chunk_text)

    print(f"Transcription chunks saved in '{output_dir}'.")

except Exception as e:
    print("Error:", e)
