import os
import re
from dotenv import load_dotenv
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = OpenAI()
serp_api_key = os.getenv("SERP_API_KEY")

def read_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    return text

def search_web(query):
    # Uses serpapi.com web search API
    url = f"""https://serpapi.com/search.json?q={query}
              &engine=google&api_key={serp_api_key}"""

    response = requests.get(url)
    data = response.json().get("organic_results") or []
    urls = []
    for item in data:
        url = item.get('link')
        urls.append(url)

    return urls[:5]  # return the first 5 URLS

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