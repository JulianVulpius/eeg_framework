import socket
import os
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import mutagen

try:
    import pygame
except ImportError:
    print("WARNING: Pygame not installed. Audio playback disabled.")
    pygame = None

router = APIRouter()

# Unicorn Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 1000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
endpoint = (UDP_IP, UDP_PORT)

if pygame:
    pygame.mixer.init()

BASE_STIMULI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stimuli"))

class SingleAudioRequest(BaseModel):
    audio_file: str

def send_udp_trigger(value: str, desc: str = ""):
    """Sendet den eigentlichen UDP Trigger an den EEG Verstärker"""
    try:
        sock.sendto(value.encode('utf-8'), endpoint)
        print(f"[UDP TRIGGER SENT] Value: {value} | Desc: {desc}")
    except Exception as e:
        print(f"[UDP ERROR] Could not send trigger: {e}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Persistente WebSocket Verbindung zum Vue Frontend.
    Gibt Trigger ohne HTTP-Latenz sofort an das EEG weiter.
    """
    await websocket.accept()
    print("Frontend WebSocket connected for Low-Latency Triggers.")
    try:
        while True:
            data = await websocket.receive_json()
            if "trigger_value" in data:
                send_udp_trigger(data["trigger_value"], data.get("description", ""))
    except WebSocketDisconnect:
        print("Frontend WebSocket disconnected.")

@router.post("/play-single")
async def play_single(req: SingleAudioRequest):
    """Startet asynchron eine Audio-Datei über Pygame"""
    if pygame and req.audio_file:
        filepath = os.path.join(BASE_STIMULI_DIR, req.audio_file)
        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            print(f"PLAYING AUDIO: {req.audio_file}")
        else:
            print(f"WARNING: Audio file not found at {filepath}")
    return {"status": "playing"}

@router.post("/stop-audio")
async def stop_audio():
    if pygame:
        pygame.mixer.music.stop()
    return {"status": "stopped"}

@router.post("/pause")
async def pause_audio():
    if pygame:
        pygame.mixer.music.pause()
    return {"status": "paused"}

@router.post("/resume")
async def resume_audio():
    if pygame:
        pygame.mixer.music.unpause()
    return {"status": "resumed"}

@router.get("/audio-duration/{filename}")
async def get_audio_duration(filename: str):
    """Wird vom Django Backend / Frontend beim Upload genutzt, um die Länge zu extrahieren"""
    filepath = os.path.join(BASE_STIMULI_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        audio = mutagen.File(filepath)
        if audio is not None and audio.info is not None:
            duration_sec = int(round(audio.info.length))
            return {"duration": duration_sec}
        else:
            raise HTTPException(status_code=400, detail="Unknown audio format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))