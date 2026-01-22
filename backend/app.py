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
    
    required_models = [
        "shinkai.pth", "hayao.pth", "hosoda.pth", "paprika.pth",
        "candy.pth", "mosaic.pth", "udnie.pth", "rain_princess.pth"
    ]
    
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

# In-memory storage for images and videos
media_storage = {}

# Define static directory
static_dir = Path(__file__).parent / "static"

# ========== API ROUTES (MUST BE DEFINED BEFORE STATIC MOUNTS) ==========

@app.get("/api")
async def api_root():
    return {"message": "AI Photo Style Converter API", "status": "running"}

@app.get("/api/styles")
async def get_styles():
    """Return available styles"""
    return {
        "styles": Config.ALL_STYLES,
        "opencv_styles": Config.OPENCV_STYLES,
        "neural_styles": Config.NEURAL_STYLES,
        "cartoon_styles": Config.CARTOON_STYLES
    }

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload image or video and return media_id"""
    is_valid_image = ImageProcessor.validate_extension(file.filename, {"jpg", "jpeg", "png", "webp"})
    is_valid_video = VideoProcessor.is_video(file.filename)
    
    if not (is_valid_image or is_valid_video):
        raise HTTPException(400, "Invalid file extension. Supported: images (jpg, png, webp) and videos (mp4, avi, mov, mkv, webm, gif)")
    
    try:
        contents = await file.read()
        
        if len(contents) > Config.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(400, f"File too large. Maximum size: {Config.MAX_FILE_SIZE_MB}MB")
        
        media_id = str(uuid.uuid4())
        is_video = VideoProcessor.is_video(file.filename)
        
        media_storage[media_id] = {
            'data': contents,
            'filename': file.filename,
            'is_video': is_video
        }
        
        print(f"✅ Uploaded: {file.filename} (ID: {media_id}, Video: {is_video})")
        
        return {
            "media_id": media_id, 
            "filename": file.filename,
            "is_video": is_video
        }
    
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.post("/api/convert")
async def convert_style(
    media_id: str = Form(...),
    style: str = Form(...)
):
    """Apply style to uploaded image or video"""
    print(f"🎨 Convert request - Media ID: {media_id}, Style: {style}")
    
    if media_id not in media_storage:
        print(f"❌ Media not found: {media_id}")
        print(f"Available media IDs: {list(media_storage.keys())}")
        raise HTTPException(404, "Media not found")
    
    if style not in Config.ALL_STYLES:
        raise HTTPException(400, f"Invalid style. Available: {Config.ALL_STYLES}")
    
    try:
        media_info = media_storage[media_id]
        media_data = media_info['data']
        is_video = media_info['is_video']
        filename = media_info['filename']
        
        print(f"Processing {filename} with style: {style}")
        
        if is_video:
            print(f"Processing video with style: {style}")
            
            if VideoProcessor.is_gif(filename):
                frames, fps = VideoProcessor.extract_gif_frames(media_data)
            else:
                frames, fps = VideoProcessor.extract_frames(media_data)
            
            print(f"Extracted {len(frames)} frames at {fps} FPS")
            
            styled_frames = []
            for i, frame in enumerate(frames):
                if i % 10 == 0:
                    print(f"Processing frame {i+1}/{len(frames)}")
                styled_frame = style_loader.apply_style(frame, style)
                styled_frames.append(styled_frame)
            
            output_format = 'gif' if VideoProcessor.is_gif(filename) else 'mp4'
            video_bytes = VideoProcessor.create_video(styled_frames, fps, output_format)
            
            if not video_bytes:
                raise HTTPException(500, "Failed to create output video")
            
            media_type = 'image/gif' if output_format == 'gif' else 'video/mp4'
            return StreamingResponse(
                io.BytesIO(video_bytes),
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename=styled_{style}.{output_format}"
                }
            )
        
        else:
            # Process image
            img = ImageProcessor.load_image(media_data, Config.MAX_IMAGE_SIZE)
            styled_img = style_loader.apply_style(img, style)
            img_bytes = ImageProcessor.image_to_bytes(styled_img)
            
            print(f"✅ Style applied successfully")
            
            return StreamingResponse(
                io.BytesIO(img_bytes),
                media_type="image/jpeg",
                headers={
                    "Content-Disposition": f"attachment; filename=styled_{style}.jpg"
                }
            )
    
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Style conversion failed: {str(e)}")

@app.delete("/api/delete/{media_id}")
async def delete_media(media_id: str):
    """Delete media from storage"""
    if media_id in media_storage:
        del media_storage[media_id]
        print(f"🗑️  Deleted media: {media_id}")
        return {"message": "Media deleted"}
    raise HTTPException(404, "Media not found")

# ========== STATIC FILES AND FRONTEND (AFTER API ROUTES) ==========

# Mount static assets
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend UI"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"error": "Frontend not found. Make sure static/index.html exists."}

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    
    print("\n" + "="*70)
    print("🎨 AI PHOTO STYLE CONVERTER")
    print("="*70)
    print(f"✅ Server starting on port {port}")
    print("="*70 + "\n")
    print("🔗 OPEN YOUR APP:")
    print(f"👉 http://localhost:{port}")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# import io
# import uuid
# from config import Config
# from utils.image_processor import ImageProcessor
# from utils.video_processor import VideoProcessor
# from utils.style_loader import StyleLoader
# from pathlib import Path
# from fastapi.staticfiles import StaticFiles
# import sys
# import subprocess

# # Download models on startup function
# def ensure_models_downloaded():
#     """Ensure all required models are downloaded"""
#     pretrained_dir = Path(__file__).parent / "pretrained"
#     pretrained_dir.mkdir(exist_ok=True)
    
#     # List of required models
#     required_models = [
#         "shinkai.pth", "hayao.pth", "hosoda.pth", "paprika.pth",
#         "candy.pth", "mosaic.pth", "udnie.pth", "rain_princess.pth"
#     ]
    
#     # Check which models are missing
#     missing_models = []
#     for model in required_models:
#         model_path = pretrained_dir / model
#         if not model_path.exists() or model_path.stat().st_size == 0:
#             missing_models.append(model)
    
#     if missing_models:
#         print("=" * 70)
#         print(f"⚠️  Missing {len(missing_models)} model files: {', '.join(missing_models)}")
#         print("📥 Downloading models from Google Drive...")
#         print("=" * 70)
        
#         try:
#             # Run download script
#             result = subprocess.run(
#                 [sys.executable, "download_models.py"],
#                 capture_output=True,
#                 text=True,
#                 check=True
#             )
#             print(result.stdout)
#             print("✅ Models downloaded successfully!")
            
#         except subprocess.CalledProcessError as e:
#             print(f"❌ Model download failed:")
#             print(e.stdout)
#             print(e.stderr)
#             print("⚠️  App will start but some styles may not work")
#         except Exception as e:
#             print(f"❌ Unexpected error during model download: {e}")
#             print("⚠️  App will start but some styles may not work")
#     else:
#         print("✅ All model files present")
#         # Print model sizes for verification
#         for model in required_models:
#             model_path = pretrained_dir / model
#             size_mb = model_path.stat().st_size / (1024 * 1024)
#             print(f"  ✓ {model}: {size_mb:.2f} MB")

# # Run model check before app initialization
# ensure_models_downloaded()

# app = FastAPI(title="AI Photo Style Converter API")

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize style loader
# style_loader = StyleLoader()

# # In-memory storage for images and videos
# media_storage = {}

# # Define static directory
# static_dir = Path(__file__).parent / "static"

# # API ROUTES (all under /api prefix)
# @app.get("/api")
# async def api_root():
#     return {"message": "AI Photo Style Converter API", "status": "running"}

# @app.get("/api/styles")
# async def get_styles():
#     """Return available styles"""
#     return {
#         "styles": Config.ALL_STYLES,
#         "opencv_styles": Config.OPENCV_STYLES,
#         "neural_styles": Config.NEURAL_STYLES,
#         "cartoon_styles": Config.CARTOON_STYLES
#     }

# @app.post("/api/upload")
# async def upload_image(file: UploadFile = File(...)):
#     """Upload image or video and return media_id"""
#     # Check if it's either a valid image or video
#     is_valid_image = ImageProcessor.validate_extension(file.filename, {"jpg", "jpeg", "png", "webp"})
#     is_valid_video = VideoProcessor.is_video(file.filename)
    
#     if not (is_valid_image or is_valid_video):
#         raise HTTPException(400, "Invalid file extension. Supported: images (jpg, png, webp) and videos (mp4, avi, mov, mkv, webm, gif)")
    
#     try:
#         contents = await file.read()
        
#         # Validate file size
#         if len(contents) > Config.MAX_FILE_SIZE_MB * 1024 * 1024:
#             raise HTTPException(400, f"File too large. Maximum size: {Config.MAX_FILE_SIZE_MB}MB")
        
#         # Generate unique ID
#         media_id = str(uuid.uuid4())
        
#         # Determine if video or image
#         is_video = VideoProcessor.is_video(file.filename)
        
#         # Store media
#         media_storage[media_id] = {
#             'data': contents,
#             'filename': file.filename,
#             'is_video': is_video
#         }
        
#         return {
#             "media_id": media_id, 
#             "filename": file.filename,
#             "is_video": is_video
#         }
    
#     except Exception as e:
#         raise HTTPException(500, f"Upload failed: {str(e)}")

# @app.post("/api/convert")
# async def convert_style(
#     media_id: str = Form(...),
#     style: str = Form(...)
# ):
#     """Apply style to uploaded image or video"""
#     if media_id not in media_storage:
#         raise HTTPException(404, "Media not found")
    
#     if style not in Config.ALL_STYLES:
#         raise HTTPException(400, f"Invalid style. Available: {Config.ALL_STYLES}")
    
#     try:
#         media_info = media_storage[media_id]
#         media_data = media_info['data']
#         is_video = media_info['is_video']
#         filename = media_info['filename']
        
#         if is_video:
#             # Process video
#             print(f"Processing video with style: {style}")
            
#             # Extract frames
#             if VideoProcessor.is_gif(filename):
#                 frames, fps = VideoProcessor.extract_gif_frames(media_data)
#             else:
#                 frames, fps = VideoProcessor.extract_frames(media_data)
            
#             print(f"Extracted {len(frames)} frames at {fps} FPS")
            
#             # Apply style to each frame
#             styled_frames = []
#             for i, frame in enumerate(frames):
#                 if i % 10 == 0:  # Progress indicator
#                     print(f"Processing frame {i+1}/{len(frames)}")
#                 styled_frame = style_loader.apply_style(frame, style)
#                 styled_frames.append(styled_frame)
            
#             # Create output video
#             output_format = 'gif' if VideoProcessor.is_gif(filename) else 'mp4'
#             video_bytes = VideoProcessor.create_video(styled_frames, fps, output_format)
            
#             if not video_bytes:
#                 raise HTTPException(500, "Failed to create output video")
            
#             # Return video
#             media_type = 'image/gif' if output_format == 'gif' else 'video/mp4'
#             return StreamingResponse(
#                 io.BytesIO(video_bytes),
#                 media_type=media_type,
#                 headers={
#                     "Content-Disposition": f"attachment; filename=styled_{style}.{output_format}"
#                 }
#             )
        
#         else:
#             # Process image (existing logic)
#             img = ImageProcessor.load_image(media_data, Config.MAX_IMAGE_SIZE)
#             styled_img = style_loader.apply_style(img, style)
#             img_bytes = ImageProcessor.image_to_bytes(styled_img)
            
#             return StreamingResponse(
#                 io.BytesIO(img_bytes),
#                 media_type="image/jpeg",
#                 headers={
#                     "Content-Disposition": f"attachment; filename=styled_{style}.jpg"
#                 }
#             )
    
#     except Exception as e:
#         raise HTTPException(500, f"Style conversion failed: {str(e)}")

# @app.delete("/api/delete/{media_id}")
# async def delete_media(media_id: str):
#     """Delete media from storage"""
#     if media_id in media_storage:
#         del media_storage[media_id]
#         return {"message": "Media deleted"}
#     raise HTTPException(404, "Media not found")

# # STATIC FILES - Mount static assets (CSS, JS, images, etc.)
# app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# # FRONTEND - Serve index.html at root
# @app.get("/")
# async def serve_frontend():
#     """Serve the frontend UI"""
#     index_file = static_dir / "index.html"
#     if index_file.exists():
#         return FileResponse(str(index_file))
#     return {"error": "Frontend not found. Make sure static/index.html exists."}

# if __name__ == "__main__":
#     import uvicorn
#     import os
    
#     # Get port from environment
#     port = int(os.environ.get("PORT", 8000))
    
#     print("\n" + "="*70)
#     print("🎨 AI PHOTO STYLE CONVERTER")
#     print("="*70)
#     print(f"✅ Server starting on port {port}")
#     print("="*70 + "\n")
#     print("🔗 OPEN YOUR APP:")
#     print(f"👉 http://localhost:{port}")
#     print("="*70 + "\n")
    
#     uvicorn.run(app, host="0.0.0.0", port=port)
