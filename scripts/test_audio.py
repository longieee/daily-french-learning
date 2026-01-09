#!/usr/bin/env python3
"""
Test script to verify audio generation and conversion works locally.
"""
import os
import subprocess
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.gemini_client import GeminiClient


def test_audio():
    client = GeminiClient()

    # Simple test script
    test_script = [
        {"role": "tutor_en", "text": "Hello! Today we will learn some French."},
        {"role": "actor_fr", "text": "Bonjour! Comment allez-vous?"},
        {"role": "tutor_en", "text": "That means: Hello! How are you?"},
    ]

    print("Generating audio from Gemini TTS...")
    audio_data = client.generate_audio(test_script)

    print(f"Received {len(audio_data)} bytes of audio data")

    # Save raw PCM
    os.makedirs("content/temp", exist_ok=True)
    raw_path = "content/temp/test_audio.pcm"
    mp3_path = "content/temp/test_audio.mp3"

    with open(raw_path, "wb") as f:
        f.write(audio_data)
    print(f"Saved raw PCM to {raw_path}")

    # Convert to MP3
    print("Converting to MP3 with ffmpeg...")
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "s16le",  # Input format: signed 16-bit little-endian
                "-ar",
                "24000",  # Sample rate: 24kHz
                "-ac",
                "1",  # Channels: mono
                "-i",
                raw_path,
                "-codec:a",
                "libmp3lame",
                "-qscale:a",
                "2",
                mp3_path,
            ],
            check=True,
            capture_output=True,
        )
        print(f"Successfully created {mp3_path}")
        print(f"MP3 file size: {os.path.getsize(mp3_path)} bytes")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg error: {e.stderr.decode()}")
        raise
    finally:
        if os.path.exists(raw_path):
            os.remove(raw_path)

    # Verify the MP3
    print("\nVerifying MP3 file...")
    result = subprocess.run(["file", mp3_path], capture_output=True, text=True)
    print(result.stdout)

    print(f"\n✅ Success! Test audio saved to: {mp3_path}")
    print("You can play it with: open content/temp/test_audio.mp3")


if __name__ == "__main__":
    test_audio()
