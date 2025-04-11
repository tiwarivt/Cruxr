import os
import re
import textwrap
import time
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from google.api_core.exceptions import ResourceExhausted
from google.generativeai import configure, GenerativeModel

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or not api_key.strip():
    raise Exception("❌ GEMINI_API_KEY is missing in .env file")

configure(api_key=api_key)
model = GenerativeModel("models/gemini-1.5-flash")

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def download_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry['text'] for entry in transcript])

def chunk_text(text, max_tokens=3000):
    return textwrap.wrap(text, width=max_tokens)

def retry_request(prompt_func, retries=3, delay=5):
    for attempt in range(retries):
        try:
            return prompt_func()
        except ResourceExhausted:
            print(f"⚠️ Rate limit hit, retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            print(f"❌ API error: {e}")
            break
    return "### Gemini failed to process this section. ###"

def generate_notes(chunk):
    prompt = f"""
You are a study assistant. Convert the following transcript chunk into detailed markdown notes:

Transcript:
{chunk}

Notes must include:
- Summary
- Key points
- Definitions of terms if found
- Questions for revision

Format the response in clear, structured Markdown.
"""
    return retry_request(lambda: model.generate_content(prompt).text.strip())

def suggest_title(full_transcript):
    prompt = f"""
You are a helpful assistant. Suggest a short, user-friendly and meaningful title (max 8 words) for the following YouTube video transcript:

Transcript:
{full_transcript[:3000]}

Only return the suggested title, nothing else.
"""
    return retry_request(lambda: model.generate_content(prompt).text.strip())
