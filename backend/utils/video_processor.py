import cv2
import imageio
import numpy as np
from PIL import Image
import tempfile
import os

class VideoProcessor:
    @staticmethod
    def is_video(filename):
        """Check if file is a video"""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif'}
        ext = os.path.splitext(filename.lower())[1]
        return ext in video_extensions
    
    @staticmethod
    def is_gif(filename):
        """Check if file is a GIF"""
        return filename.lower().endswith('.gif')
    
    @staticmethod
    def extract_frames(video_bytes, max_frames=150):
        """Extract frames from video bytes"""
        # Save bytes to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(video_bytes)
            tmp_path = tmp.name
        
        try:
            # Read video
            cap = cv2.VideoCapture(tmp_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Limit frames to prevent memory issues
            if frame_count > max_frames:
                frame_skip = frame_count // max_frames
            else:
                frame_skip = 1
            
            # ✅ FIX: Adjust FPS based on frame skipping
            adjusted_fps = fps / frame_skip
            
            frames = []
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_skip == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(frame_rgb))
                
                frame_idx += 1
            
            cap.release()
            
            # ✅ Return adjusted FPS
            return frames, adjusted_fps
            
        finally:
            os.unlink(tmp_path)
    
    @staticmethod
    def extract_gif_frames(gif_bytes):
        """Extract frames from GIF bytes"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as tmp:
            tmp.write(gif_bytes)
            tmp_path = tmp.name
        
        try:
            gif = imageio.mimread(tmp_path)
            frames = [Image.fromarray(frame) for frame in gif]
            
            # Get duration (FPS) from GIF metadata
            reader = imageio.get_reader(tmp_path)
            meta = reader.get_meta_data()
            duration = meta.get('duration', 100) / 1000.0  # Convert ms to seconds
            fps = 1.0 / duration if duration > 0 else 10
            
            return frames, fps
            
        finally:
            os.unlink(tmp_path)
    
    @staticmethod
    def create_video(frames, fps, output_format='mp4'):
        """Create video from styled frames"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}') as tmp:
            tmp_path = tmp.name
        
        try:
            if output_format == 'gif':
                # Create GIF
                frames_np = [np.array(frame) for frame in frames]
                duration = 1.0 / fps
                imageio.mimsave(tmp_path, frames_np, duration=duration, loop=0)
            else:
                # Create MP4
                if not frames:
                    return None
                
                height, width = np.array(frames[0]).shape[:2]
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(tmp_path, fourcc, fps, (width, height))
                
                for frame in frames:
                    frame_np = np.array(frame)
                    frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                    out.write(frame_bgr)
                
                out.release()
            
            # Read the created file
            with open(tmp_path, 'rb') as f:
                video_bytes = f.read()
            
            return video_bytes
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)