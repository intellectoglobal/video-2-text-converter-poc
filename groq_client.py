import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure the API key is available
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the .env file!")

# Initialize the Groq client with the API key
client = Groq(api_key=GROQ_API_KEY)

# Specify the path to the audio file
filename = os.path.join(os.path.dirname(__file__), "Mudhal-Kanave.mp3")  # Ensure demo.mp3 exists!

try:
    # Open the audio file
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),  # Required audio file
            model="whisper-large-v3-turbo",  # Required model to use for transcription
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            # language="en",
            temperature=0.0  # Optional
        )

    # Access the transcription text directly
    full_text = transcription.text  # Full transcription text

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

    print(f"Transcription chunks saved in '{output_dir}'.")

except Exception as e:
    print("Error:", e)
