from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from utils.notes_generator import get_video_id, download_transcript, chunk_text, generate_notes, suggest_title

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tiwarivt.github.io/Cruxr/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    youtubeUrl: str

@app.post("/api/notes")
def generate_video_notes(req: VideoRequest):
    video_id = get_video_id(req.youtubeUrl)
    if not video_id:
        return {"error": "Invalid YouTube URL."}

    try:
        transcript = download_transcript(video_id)
        title = suggest_title(transcript)
        chunks = chunk_text(transcript)
        notes = [generate_notes(chunk) for chunk in chunks]
        full_markdown = f"# {title}\n\n" + "\n\n".join(notes)
        return {"title": title, "notes": full_markdown}
    except Exception as e:
        return {"error": str(e)}
