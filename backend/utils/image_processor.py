from PIL import Image
import io

class ImageProcessor:
    @staticmethod
    def load_image(file_bytes, max_size=1024):
        """Load and resize image from bytes"""
        img = Image.open(io.BytesIO(file_bytes))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if larger than max_size
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        return img
    
    @staticmethod
    def image_to_bytes(img, format='JPEG', quality=95):
        """Convert PIL Image to bytes"""
        buffer = io.BytesIO()
        img.save(buffer, format=format, quality=quality)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def validate_extension(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions