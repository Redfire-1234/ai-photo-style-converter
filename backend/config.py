import os

class Config:
    # Server
    HOST = "0.0.0.0"
    PORT = 8000
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, "pretrained")
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    
    # Create temp directory if not exists
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Styles
    OPENCV_STYLES = [
        "pencil_sketch",
        "charcoal_sketch",
        "watercolor",
        "oil_painting",
        "crayon_color",
        "rough_paper",
        "sepia",
        "vintage",
        "hdr_effect",
        "pop_art",
        "emboss",
        "cartoon"
    ]
    
    NEURAL_STYLES = [
        "candy",
        "mosaic",
        "rain_princess",
        "udnie"
    ]
    
    CARTOON_STYLES = [
        "shinkai",
        "hayao",
        "hosoda",
        "paprika"
    ]
    
    ALL_STYLES = OPENCV_STYLES + NEURAL_STYLES + CARTOON_STYLES
    
    # Image settings
    MAX_IMAGE_SIZE = 1024
    # Updated to include video formats
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "mp4", "avi", "mov", "mkv", "webm", "gif"}
    VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm", "gif"}
    MAX_FILE_SIZE_MB = 50  # Increased for videos
    
    # Model paths
    NEURAL_MODEL_PATHS = {
        "candy": os.path.join(MODELS_DIR, "candy.pth"),
        "mosaic": os.path.join(MODELS_DIR, "mosaic.pth"),
        "rain_princess": os.path.join(MODELS_DIR, "rain_princess.pth"),
        "udnie": os.path.join(MODELS_DIR, "udnie.pth"),
    }
    
    ANIME_MODEL_PATHS = {
        "shinkai": os.path.join(MODELS_DIR, "shinkai.pth"),
        "hayao": os.path.join(MODELS_DIR, "hayao.pth"),
        "hosoda": os.path.join(MODELS_DIR, "hosoda.pth"),
        "paprika": os.path.join(MODELS_DIR, "paprika.pth"),
    }