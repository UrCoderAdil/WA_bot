import edge_tts
import uuid
import os

# Create an output directory for generated audio files
AUDIO_DIR = os.path.join(os.getcwd(), "media", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

async def generate_speech(text: str, voice: str = "ur-PK-AsadNeural") -> str:
    """
    Generate an .ogg audio file from text using edge-tts.
    Default voice is Pakistani Urdu (Male).
    Returns the absolute path to the generated file.
    """
    file_id = str(uuid.uuid4())
    file_path = os.path.join(AUDIO_DIR, f"{file_id}.ogg")
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)
    
    return file_path
