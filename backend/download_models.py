import os
import gdown
from pathlib import Path

# Create pretrained directory if it doesn't exist
MODELS_DIR = Path(__file__).parent / "pretrained"
MODELS_DIR.mkdir(exist_ok=True)

# Model file IDs from Google Drive
MODELS = {
    "shinkai.pth": "12qjzKoC9DYkbiAAflIB1dhLf2rAE58ZG",
    "hayao.pth": "19CyAIpRnzAlI_M-72SA_Kg8BswchgDJ4", 
    "hosoda.pth": "1RrRLD-2vO3fG0CFE1ianJx7OX663zCXc",
    "paprika.pth": "1UR-RVuelUmyuBIs4qdh9rrT1wwP5IjfU",
    "candy.pth": "1GVpEZab4ULuaWFTW86bNWID7QcaEnjld",
    "mosaic.pth": "1ja1uH-J3vc5vq-kLPTa5fREa7t7Bn5vZ",
    "udnie.pth": "1Bb9Oaq9nGClp5_RviyxhG_bqeA0rjyHa",
    "rain_princess.pth": "1HiQjcirwE5l7rVx68kbQUn3cgEVRjsep"
}

def download_from_gdrive(file_id, output_path):
    """Download file from Google Drive using gdown"""
    url = f"https://drive.google.com/uc?id={file_id}"
    try:
        print(f"  Downloading from: {url}")
        gdown.download(url, str(output_path), quiet=False, fuzzy=True)
        
        # Verify file was downloaded
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"  ✓ File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
            return True
        else:
            print(f"  ✗ Download failed or file is empty")
            return False
            
    except Exception as e:
        print(f"  ✗ Error downloading: {e}")
        return False

def download_all_models():
    """Download all model files from Google Drive"""
    print("=" * 60)
    print("Downloading model files from Google Drive...")
    print(f"Target directory: {MODELS_DIR.absolute()}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for model_name, file_id in MODELS.items():
        model_path = MODELS_DIR / model_name
        
        # Skip if already exists
        if model_path.exists() and model_path.stat().st_size > 0:
            print(f"\n✓ {model_name} already exists ({model_path.stat().st_size / (1024*1024):.2f} MB), skipping")
            skip_count += 1
            continue
        
        print(f"\n📥 Downloading {model_name}...")
        if download_from_gdrive(file_id, model_path):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"Download Summary:")
    print(f"  ✓ Downloaded: {success_count}")
    print(f"  ⊘ Skipped: {skip_count}")
    print(f"  ✗ Failed: {fail_count}")
    print("=" * 60)
    
    # List all files in pretrained directory
    print("\nFiles in pretrained directory:")
    for file in MODELS_DIR.iterdir():
        size_mb = file.stat().st_size / (1024*1024)
        print(f"  - {file.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    download_all_models()
