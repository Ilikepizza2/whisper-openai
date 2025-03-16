from openai import OpenAI
import base64
import json

client = OpenAI(
    base_url="http://localhost:8000/v1",  # Your FastAPI server
    api_key="dummy-key"  # Not used, but required by OpenAI SDK
)

# Read and encode the audio file
with open("output.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode("utf-8")

# Send request to FastAPI server
response = client.chat.completions.create(
    model="whisper",
    modalities=["audio"],
    audio={
        "word_timestamps": True,  # Set to False if you don't need timestamps
        "model_repo": "mlx-community/whisper-large-v3-turbo",
    },
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_data,
                        "format": "wav"
                    }
                }
            ]
        }
    ]
)

# Convert response to a dictionary before JSON serialization
response_dict = response.model_dump()

# Print formatted JSON output
print(json.dumps(response_dict, indent=2))

# Extract and print the transcription text
print("Transcription:", response_dict["choices"][0]["message"]["content"])
