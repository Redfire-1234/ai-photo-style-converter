import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.neural_style import NeuralStyler
from models.opencv_styles import OpenCVStyler
from models.cartoon_transformer import CartoonGANStyler
from config import Config
import numpy as np
from PIL import Image

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
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  ✗ Model file not found: {model_path}")
        
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
                    print(f"  ✓ Loaded {style_name} CartoonGAN model")
                except Exception as e:
                    print(f"  ✗ Failed to load {style_name}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  ✗ Model file not found: {model_path}")
        
        print(f"\nTotal anime models loaded: {len(self.anime_models)}")
        print("=" * 50)
    
    def apply_style(self, img, style_name):
        """
        Apply style transformation to image
        
        Args:
            img: Can be either numpy array (BGR from OpenCV) or PIL Image
            style_name: Name of the style to apply
            
        Returns:
            PIL Image with style applied
        """
        style_name = style_name.lower()
        
        # Convert numpy array to PIL Image if needed
        is_numpy = isinstance(img, np.ndarray)
        if is_numpy:
            # OpenCV uses BGR, convert to RGB
            if len(img.shape) == 3 and img.shape[2] == 3:
                img_rgb = img[:, :, ::-1]  # BGR to RGB
            else:
                img_rgb = img
            pil_img = Image.fromarray(img_rgb.astype('uint8'), 'RGB')
        else:
            pil_img = img
        
        # Apply the style
        try:
            # OpenCV styles
            if style_name in Config.OPENCV_STYLES:
                # OpenCV styles work with numpy arrays
                if not is_numpy:
                    # Convert PIL to numpy BGR for OpenCV
                    numpy_img = np.array(pil_img)
                    numpy_img = numpy_img[:, :, ::-1]  # RGB to BGR
                else:
                    numpy_img = img
                
                method = getattr(self.opencv_styler, style_name)
                result = method(numpy_img)
                
                # Convert result back to PIL Image (RGB)
                if isinstance(result, np.ndarray):
                    result_rgb = result[:, :, ::-1] if len(result.shape) == 3 else result
                    return Image.fromarray(result_rgb.astype('uint8'), 'RGB')
                return result
            
            # Neural styles
            elif style_name in Config.NEURAL_STYLES:
                if style_name not in self.neural_models:
                    raise ValueError(f"Model for {style_name} not loaded. Check model file exists.")
                return self.neural_models[style_name].stylize(pil_img)
            
            # Anime styles
            elif style_name in Config.CARTOON_STYLES:
                if style_name not in self.anime_models:
                    raise ValueError(f"Model for {style_name} not loaded. Check model file exists.")
                return self.anime_models[style_name].stylize(pil_img)
            
            else:
                raise ValueError(f"Unknown style: {style_name}")
                
        except Exception as e:
            print(f"❌ Error applying style {style_name}: {e}")
            import traceback
            traceback.print_exc()
            raise

    @property
    def models(self):
        """Return count of all loaded models"""
        return {
            'neural': list(self.neural_models.keys()),
            'anime': list(self.anime_models.keys()),
            'opencv': Config.OPENCV_STYLES
        }
