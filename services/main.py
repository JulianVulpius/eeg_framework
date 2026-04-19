import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poc_audio import router as audio_router
from poc_heartrate import router as heartrate_router

app = FastAPI(title="EEG Framework Engine & Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_router)
app.include_router(heartrate_router)

if __name__ == "__main__":
    print("Starte Engine Hub auf Port 8001...")
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)