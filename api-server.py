import base64
import io
import mlx_whisper
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class AudioContent(BaseModel):
    data: str  # Base64-encoded audio
    format: str  # Audio format (e.g., "wav")

class AudioRequest(BaseModel):
    model: str = "whisper"
    modalities: list = ["audio"]
    audio: dict
    messages: list

@app.post("/v1/chat/completions")
async def transcribe_audio(request: AudioRequest):
    try:
        # Extract base64 audio data
        user_message = next((msg for msg in request.messages if msg["role"] == "user"), None)
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        input_audio = next((c["input_audio"] for c in user_message["content"] if c["type"] == "input_audio"), None)
        if not input_audio:
            raise HTTPException(status_code=400, detail="No audio content found")

        audio_data = base64.b64decode(input_audio["data"])
        audio_format = input_audio["format"]

        # Save audio to a temporary file
        with NamedTemporaryFile(delete=True, suffix=f".{audio_format}") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio.flush()

            # Run Whisper transcription
            output = mlx_whisper.transcribe(
                temp_audio.name, 
                path_or_hf_repo="mlx-community/whisper-large-v3-turbo", 
                word_timestamps=request.audio.get("word_timestamps", False)
            )

        return {
            "id": "chatcmpl-xyz",
            "object": "chat.completion",
            "created": 1234567890,
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": output["text"],
                        "audio": {
                            "data": [seg["words"] for seg in output["segments"]] if request.audio.get("word_timestamps", False) else None
                        }
                    }
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)