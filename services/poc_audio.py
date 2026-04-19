import socket
import asyncio
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import mutagen

try:
    import pygame
except ImportError:
    print("WARNING: Pygame not installed. Audio playback disabled.")
    pygame = None

router = APIRouter()

UDP_IP = "127.0.0.1"
UDP_PORT = 1000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
endpoint = (UDP_IP, UDP_PORT)

if pygame:
    pygame.mixer.init()

BASE_STIMULI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stimuli"))

class SongItem(BaseModel):
    name: str
    duration: int
    audio_file: Optional[str] = None 

class PlaylistStartRequest(BaseModel):
    songs: List[SongItem]
    transition_time: int = 15

class ManualTriggerRequest(BaseModel):
    trigger_value: str
    description: Optional[str] = ""

class EngineState:
    is_running: bool = False
    is_paused: bool = False
    current_tasks: List[asyncio.Task] = []

state = EngineState()

def send_udp_trigger(value: str, desc: str):
    try:
        sock.sendto(value.encode('utf-8'), endpoint)
        print(f"TRIGGER SENT: {value} ({desc})")
    except Exception as e:
        print(f"UDP ERROR: {e}")

def play_audio(filename: str):
    if pygame and filename:
        filepath = os.path.join(BASE_STIMULI_DIR, filename)
        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            print(f"PLAYING AUDIO: {filepath}")
        else:
            print(f"WARNING: Audio file not found at {filepath}")

async def schedule_trigger(delay_sec: float, value: str, desc: str):
    try:
        await asyncio.sleep(delay_sec)
        if state.is_running:
            send_udp_trigger(value, desc)
    except asyncio.CancelledError:
        pass

async def schedule_audio(delay_sec: float, filename: str):
    try:
        await asyncio.sleep(delay_sec)
        if state.is_running and filename:
            play_audio(filename)
    except asyncio.CancelledError:
        pass

@router.post("/manual-trigger")
async def manual_trigger(req: ManualTriggerRequest):
    send_udp_trigger(req.trigger_value, f"Manual: {req.description}")
    return {"status": "success", "trigger": req.trigger_value}

@router.post("/start")
async def start_playlist(req: PlaylistStartRequest):
    if state.is_running:
        raise HTTPException(status_code=400, detail="Playlist is already running.")
    
    state.is_running = True
    state.is_paused = False
    state.current_tasks.clear()
    current_time_offset = 0
    
    for i, song in enumerate(req.songs):
        start_s = current_time_offset
        end_s = start_s + song.duration
        
        if song.audio_file:
            ta = asyncio.create_task(schedule_audio(start_s, song.audio_file))
            state.current_tasks.append(ta)

        t1 = asyncio.create_task(schedule_trigger(start_s, '1', f"Start: {song.name}"))
        state.current_tasks.append(t1)

        if req.transition_time > 0 and i > 0:
            t2 = asyncio.create_task(schedule_trigger(start_s + req.transition_time, '10', f"Trans End: {song.name}"))
            state.current_tasks.append(t2)

        if song.duration > req.transition_time and i < len(req.songs) - 1:
            t3 = asyncio.create_task(schedule_trigger(end_s - req.transition_time, '9', "Trans Start"))
            state.current_tasks.append(t3)

        t4 = asyncio.create_task(schedule_trigger(end_s, '2', f"End: {song.name}"))
        state.current_tasks.append(t4)

        current_time_offset += song.duration

    return {"status": "started", "total_duration": current_time_offset}

@router.post("/stop")
async def stop_playlist():
    if not state.is_running:
        return {"status": "already stopped"}

    for task in state.current_tasks:
        task.cancel()
    state.current_tasks.clear()

    if pygame:
        pygame.mixer.music.stop()

    state.is_running = False
    state.is_paused = False
    return {"status": "stopped"}

@router.post("/pause")
async def pause_playlist():
    if pygame and state.is_running:
        pygame.mixer.music.pause()
        state.is_paused = True
    return {"status": "paused"}

@router.post("/resume")
async def resume_playlist():
    if pygame and state.is_running and state.is_paused:
        pygame.mixer.music.unpause()
        state.is_paused = False
    return {"status": "resumed"}

@router.get("/audio-duration/{filename}")
async def get_audio_duration(filename: str):
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