import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import pandas as pd
import numpy as np
from datetime import datetime

# Import all project modules from core and utils
from core import registry, downloader, cleaner, extractor, benchmarker, brain_bridge
from utils import analytics, memory_viewer

import sys
import io
import queue
import threading

app = FastAPI(title="MetaLearner Enterprise Dashboard API")



# Ensure temp directory exists
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

# Global Instances
reg_obj = registry.SystemRegistry()
bridge_obj = brain_bridge.MetaBrainBridge()

def get_targets(states):
    if isinstance(states, str):
        states = [states]
    return [fid for fid, info in reg_obj.memory.items() if info["state"] in states]

# ---------------------------------------------------------
# API ROUTES: PIPELINE
# ---------------------------------------------------------

@app.get("/api/status")
def get_status():
    """Returns the current pipeline status (Memory counts)."""
    # Reload registry to ensure fresh data
    global reg_obj
    reg_obj = registry.SystemRegistry()
    
    return {
        "total_entries": len(reg_obj.memory),
        "raw": len(get_targets("DOWNLOADED")),
        "cleaned": len(get_targets("CLEANED")),
        "dna": len(get_targets("EXTRACTED")),
        "predicted": len(get_targets("PREDICTED")),
        "oracle_online": bridge_obj.ready
    }




# ---------------------------------------------------------
# API ROUTES: ORACLE UPLOAD & ANALYTICS
# ---------------------------------------------------------

@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    file_path = os.path.join(TEMP_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if not bridge_obj.ready:
            bridge_obj._establish_neural_link()
            if not bridge_obj.ready:
                return JSONResponse(status_code=503, content={"error": "MetaBrain model is offline."})

        winner, confidence = bridge_obj.predict_from_csv(file_path)
        
        if not winner:
            raise HTTPException(status_code=500, detail="MetaBrain prediction failed or returned null.")
            
        # Extract Data DNA Metrics
        df = pd.read_csv(file_path)
        dna_metrics = bridge_obj._extract_dna(df)
        
        clean_metrics = {}
        for k, v in dna_metrics.items():
            if pd.isna(v) or (isinstance(v, float) and np.isnan(v)):
                clean_metrics[k] = 0.0
            else:
                clean_metrics[k] = float(v)
            
        return {
            "filename": file.filename,
            "predicted_algorithm": winner,
            "confidence_score": float(confidence),
            "metrics": clean_metrics,
            "message": "Analysis Complete"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass




# Mount the static frontend directory
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    print("Starting MetaLearner Frontend Web Server...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
