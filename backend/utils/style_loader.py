import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.neural_style import NeuralStyler
from models.opencv_styles import OpenCVStyler
from models.cartoon_transformer import CartoonGANStyler
from config import Config

print("=" * 50)
print("Loading Style Models...")
print("=" * 50)

class StyleLoader:
    def __init__(self):
        self.neural_models = {}
        self.anime_models = {}
        self.opencv_styler = OpenCVStyler()
        self.load_neural_models()
        self.load_anime_models()
    
    def load_neural_models(self):
        """Load neural style transfer models"""
        print(f"\nLooking for models in: {Config.MODELS_DIR}")
        print(f"Models directory exists: {os.path.exists(Config.MODELS_DIR)}\n")
        
        for style_name, model_path in Config.NEURAL_MODEL_PATHS.items():
            print(f"Checking {style_name}: {model_path}")
            if os.path.exists(model_path):
                try:
                    self.neural_models[style_name] = NeuralStyler(model_path)
                    print(f"  ✓ Loaded {style_name} model")
                except Exception as e:
                    print(f"  ✗ Failed to load {style_name}: {e}")
            else:
                print(f"  ✗ Model file not found")
        
        print(f"\nTotal neural models loaded: {len(self.neural_models)}")
        print("=" * 50)
    
    def load_anime_models(self):
        """Load CartoonGAN anime style models"""
        print(f"\nLoading anime models...")
        
        for style_name, model_path in Config.ANIME_MODEL_PATHS.items():
            print(f"Checking {style_name}: {model_path}")
            if os.path.exists(model_path):
                try:
                    self.anime_models[style_name] = CartoonGANStyler(model_path, style_name)
                except Exception as e:
                    print(f"  ✗ Failed to load {style_name}: {e}")
            else:
                print(f"  ✗ Model file not found")
        
        print(f"\nTotal anime models loaded: {len(self.anime_models)}")
        print("=" * 50)
    
    def apply_style(self, img, style_name):
        """Apply style transformation to image"""
        style_name = style_name.lower()
        
        # OpenCV styles
        if style_name in Config.OPENCV_STYLES:
            method = getattr(self.opencv_styler, style_name)
            return method(img)
        
        # Neural styles
        elif style_name in Config.NEURAL_STYLES:
            if style_name in self.neural_models:
                return self.neural_models[style_name].stylize(img)
            else:
                raise ValueError(f"Model for {style_name} not loaded")
        
        # Anime styles
        elif style_name in Config.CARTOON_STYLES:
            if style_name in self.anime_models:
                return self.anime_models[style_name].stylize(img)
            else:
                raise ValueError(f"Model for {style_name} not loaded")
        
        else:
            raise ValueError(f"Unknown style: {style_name}")