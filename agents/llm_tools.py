import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = OpenAI()
google_api_key = os.getenv("GOOGLE_API_KEY")
search_engine_id = os.getenv("SEARCH_ENGINE_ID")

def read_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    return text

def search_web(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 5  # hardcoded to return 5 URL results for demo purposes
    }

    response = requests.get(url, params=params)
    data = response.json().get("items") or []
    urls = []
    for item in data:
        url = item.get('link')
        urls.append(url)

    return urls


def create_audio(script):
    audio_filename = "podcast.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="ballad",
        instructions="""Persona: You are a newscaster.
                        Delivery: Crisp and articulate, with measured pacing.
                        Tone: Objective and neutral, confident and 
                        authoritative, conversational yet formal.""",
        input=script
    ) as response:
        response.stream_to_file(audio_filename)
    
    return True