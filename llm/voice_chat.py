import asyncio
import os
import threading
from dotenv import load_dotenv
import speech_recognition as sr
import edge_tts
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configure Edge TTS voice settings
VOICE = "en-US-AriaNeural"
OUTPUT_FILE = "response.mp3"

async def speak(text):
    """Convert text to speech using Edge TTS and play it."""
    print(f"Assistant: {text}")
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(OUTPUT_FILE)
        os.system(f'mpv --no-terminal {OUTPUT_FILE}')
    except Exception as e:
        print(f"Error in TTS: {e}")
    finally:
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

def listen(callback):
    """Capture audio from microphone and convert to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            callback(text)
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            callback(None)
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            callback(None)

async def fetch_groq_response(prompt):
    """Fetch AI-generated response from Groq API."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error fetching response from Groq: {e}")
        return "I encountered an issue processing your request. Please try again."

async def handle_interaction():
    """Main interaction loop: listen, process, and respond."""
    await speak("Hello! I'm your voice assistant. How can I help you today?")
    
    def process_user_input(user_input):
        if user_input:
            if any(word in user_input.lower() for word in ["quit", "exit", "bye"]):
                asyncio.run(speak("Goodbye!"))
                return
            asyncio.run(process_response(user_input))

    async def process_response(user_input):
        response = await fetch_groq_response(user_input)
        await speak(response)
        threading.Thread(target=listen, args=(process_user_input,)).start()

    threading.Thread(target=listen, args=(process_user_input,)).start()

if __name__ == "__main__":
    asyncio.run(handle_interaction())
