import cv2
import numpy as np
from PIL import Image

class OpenCVStyler:
    @staticmethod
    def pencil_sketch(img):
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        return Image.fromarray(sketch)
    
    @staticmethod
    def charcoal_sketch(img):
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        charcoal = cv2.bitwise_not(sketch)
        return Image.fromarray(charcoal)
    
    @staticmethod
    def watercolor(img):
        img_np = np.array(img)
        for _ in range(2):
            img_np = cv2.bilateralFilter(img_np, 9, 75, 75)
        edges = cv2.adaptiveThreshold(
            cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY),
            255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
        )
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        result = cv2.bitwise_and(img_np, edges)
        return Image.fromarray(result)
    
    @staticmethod
    def oil_painting(img):
        img_np = np.array(img)
        # Alternative oil painting effect without xphoto
        result = cv2.bilateralFilter(img_np, 9, 75, 75)
        result = cv2.bilateralFilter(result, 9, 75, 75)
        return Image.fromarray(result)
    
    @staticmethod
    def crayon_color(img):
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        bilateral = cv2.bilateralFilter(img_np, 9, 75, 75)
        result = cv2.subtract(bilateral, edges)
        return Image.fromarray(result)
    
    @staticmethod
    def rough_paper(img):
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        noise = np.random.randint(0, 50, gray.shape, dtype=np.uint8)
        textured = cv2.add(gray, noise)
        textured = cv2.cvtColor(textured, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(textured)
    
    @staticmethod
    def sepia(img):
        img_np = np.array(img).astype(np.float32)
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]])
        sepia_img = cv2.transform(img_np, sepia_filter)
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        return Image.fromarray(sepia_img)
    
    @staticmethod
    def vintage(img):
        img_np = np.array(img)
        # Apply sepia
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                  [0.349, 0.686, 0.168],
                                  [0.393, 0.769, 0.189]])
        vintage_img = cv2.transform(img_np.astype(np.float32), sepia_filter)
        vintage_img = np.clip(vintage_img, 0, 255).astype(np.uint8)
        # Add vignette
        rows, cols = vintage_img.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols/2)
        kernel_y = cv2.getGaussianKernel(rows, rows/2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        vintage_img = vintage_img.astype(np.float32)
        for i in range(3):
            vintage_img[:,:,i] = vintage_img[:,:,i] * mask
        vintage_img = np.clip(vintage_img, 0, 255).astype(np.uint8)
        return Image.fromarray(vintage_img)
    
    @staticmethod
    def hdr_effect(img):
        img_np = np.array(img)
        hdr = cv2.detailEnhance(img_np, sigma_s=12, sigma_r=0.15)
        return Image.fromarray(hdr)
    
    @staticmethod
    def pop_art(img):
        img_np = np.array(img)
        # Increase saturation
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:,:,1] = hsv[:,:,1] * 1.5
        hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
        img_np = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        # Posterize
        div = 64
        img_np = (img_np // div) * div
        return Image.fromarray(img_np)
    
    @staticmethod
    def emboss(img):
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        kernel = np.array([[0,-1,-1],
                          [1,0,-1],
                          [1,1,0]])
        embossed = cv2.filter2D(gray, -1, kernel)
        embossed = embossed + 128
        embossed = cv2.cvtColor(embossed, cv2.COLOR_GRAY2RGB)
        return Image.fromarray(embossed)
    
    @staticmethod
    def cartoon(img):
        img_np = np.array(img)
        # Bilateral filter for smoothing
        for _ in range(2):
            img_np = cv2.bilateralFilter(img_np, 9, 75, 75)
        # Edge detection
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                       cv2.THRESH_BINARY, 9, 9)
        # Combine
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        cartoon = cv2.bitwise_and(img_np, edges)
        return Image.fromarray(cartoon)