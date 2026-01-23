from PIL import Image
import io
import numpy as np
import cv2

class ImageProcessor:
    @staticmethod
    def load_image(image_bytes, max_size=1024):
        """Load image from bytes and return PIL Image"""
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.LANCZOS)
        
        return img
    
    @staticmethod
    def image_to_bytes(img):
        """Convert PIL Image to bytes"""
        if isinstance(img, np.ndarray):
            # Convert numpy to PIL
            if len(img.shape) == 3 and img.shape[2] == 3:
                img = Image.fromarray(img[:, :, ::-1])  # BGR to RGB
            else:
                img = Image.fromarray(img)
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        return buffer.getvalue()
    
    @staticmethod
    def validate_extension(filename, allowed_extensions):
        """Check if file extension is valid"""
        ext = filename.lower().split('.')[-1]
        return ext in allowed_extensions
