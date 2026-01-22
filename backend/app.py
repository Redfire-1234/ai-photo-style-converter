from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import uuid
from config import Config
from utils.image_processor import ImageProcessor
from utils.video_processor import VideoProcessor
from utils.style_loader import StyleLoader
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import sys
import subprocess

# Download models on startup function
def ensure_models_downloaded():
    """Ensure all required models are downloaded"""
    pretrained_dir = Path(__file__).parent / "pretrained"
    pretrained_dir.mkdir(exist_ok=True)
    
    # List of required models
    required_models = [
        "shinkai.pth", "hayao.pth", "hosoda.pth", "paprika.pth",
        "candy.pth", "mosaic.pth", "udnie.pth", "rain_princess.pth"
    ]
    
    # Check which models are missing
    missing_models = []
    for model in required_models:
        model_path = pretrained_dir / model
        if not model_path.exists() or model_path.stat().st_size == 0:
            missing_models.append(model)
    
    if missing_models:
        print("=" * 70)
        print(f"⚠️  Missing {len(missing_models)} model files: {', '.join(missing_models)}")
        print("📥 Downloading models from Google Drive...")
        print("=" * 70)
        
        try:
            # Run download script
            result = subprocess.run(
                [sys.executable, "download_models.py"],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            print("✅ Models downloaded successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Model download failed:")
            print(e.stdout)
            print(e.stderr)
            print("⚠️  App will start but some styles may not work")
        except Exception as e:
            print(f"❌ Unexpected error during model download: {e}")
            print("⚠️  App will start but some styles may not work")
    else:
        print("✅ All model files present")
        # Print model sizes for verification
        for model in required_models:
            model_path = pretrained_dir / model
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {model}: {size_mb:.2f} MB")

# Run model check before app initialization
ensure_models_downloaded()

app = FastAPI(title="AI Photo Style Converter API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize style loader AFTER ensuring models are downloaded
style_loader = StyleLoader()

# ... rest of your code stays the same ...
