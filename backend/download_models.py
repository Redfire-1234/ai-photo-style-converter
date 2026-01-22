import os
import gdown
from pathlib import Path

# Create pretrained directory if it doesn't exist
MODELS_DIR = Path(__file__).parent / "pretrained"
MODELS_DIR.mkdir(exist_ok=True)

# Google Drive folder ID from your link
FOLDER_ID = "1xJ2jpqnkhePmsba6UFKg3wF4lH_oP-5y"

# Model file IDs (you need to get these - see instructions below)
# To get file IDs:
# 1. Open each file in Google Drive
# 2. Click "Share" → "Anyone with the link can view"
# 3. Copy the file ID from the URL
# Format: https://drive.google.com/file/d/FILE_ID_HERE/view

MODELS = {
    "shinkai.pth": "12qjzKoC9DYkbiAAflIB1dhLf2rAE58ZG",
    "hayao.pth": "19CyAIpRnzAlI_M-72SA_Kg8BswchgDJ4", 
    "hosoda.pth": "1RrRLD-2vO3fG0CFE1ianJx7OX663zCXc",
    "paprika.pth": "1UR-RVuelUmyuBIs4qdh9rrT1wwP5IjfU",
    "candy.pth":"1GVpEZab4ULuaWFTW86bNWID7QcaEnjld",
    "mosaic.pth":"1ja1uH-J3vc5vq-kLPTa5fREa7t7Bn5vZ",
    "udnie.pth":"1Bb9Oaq9nGClp5_RviyxhG_bqeA0rjyHa",
    "rain_princess.pth":"1HiQjcirwE5l7rVx68kbQUn3cgEVRjsep"
}

def download_from_gdrive(file_id, output_path):
    """Download file from Google Drive using gdown"""
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        gdown.download(url, str(output_path), quiet=False)
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

def download_all_models():
    """Download all model files from Google Drive"""
    print("=" * 60)
    print("Downloading model files from Google Drive...")
    print("=" * 60)
    
    for model_name, file_id in MODELS.items():
        model_path = MODELS_DIR / model_name
        
        # Skip if already exists
        if model_path.exists():
            print(f"✓ {model_name} already exists, skipping")
            continue
        
        # Check if file_id is set
        if file_id.startswith("YOUR_"):
            print(f"⚠ {model_name}: File ID not set, skipping")
            continue
        
        print(f"\nDownloading {model_name}...")
        if download_from_gdrive(file_id, model_path):
            print(f"✓ {model_name} downloaded successfully")
        else:
            print(f"✗ {model_name} download failed")
    
    print("\n" + "=" * 60)
    print("Model download complete!")
    print("=" * 60)

if __name__ == "__main__":
    download_all_models()
