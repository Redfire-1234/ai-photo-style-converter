# 🎨 AI Photo & Video Style Converter

Transform your photos and videos into stunning artistic styles using AI - all running on CPU!

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🖼️ **20 Artistic Styles** - Classic, Neural, and Anime styles
- 🎬 **Video Support** - Process MP4, GIF, and more
- 📸 **Webcam Capture** - Take photos directly in the app
- 🎚️ **Intensity Control** - Adjust style strength
- 👁️ **Before/After Comparison** - Slider to compare results
- ⚡ **CPU-Optimized** - No GPU required
- 🌐 **Web Interface** - Beautiful, responsive UI

## 🎨 Available Styles

### Classic Styles (OpenCV - Instant)
- ✏️ Pencil Sketch
- 🖊️ Charcoal Sketch
- 🎨 Watercolor
- 🖌️ Oil Painting
- 🖍️ Crayon Color
- 📄 Rough Paper
- 🌅 Sepia
- 📷 Vintage
- ✨ HDR Effect
- 🎭 Pop Art
- 🔨 Emboss
- 🎪 Cartoon

### Neural Styles (AI - High Quality)
- 🍬 Candy
- 🔲 Mosaic
- 🌧️ Rain Princess
- 🎨 Udnie

### Anime Styles (CartoonGAN)
- ⛅ Shinkai (Your Name style)
- 🌿 Hayao (Miyazaki style)
- 🌸 Hosoda
- 🎪 Paprika

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- 2GB+ RAM (4GB recommended)
- Windows/Linux/macOS

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-photo-style-converter.git
cd ai-photo-style-converter
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Download model files** (see [MODELS.md](docs/MODELS.md))

5. **Run the application**
```bash
python app.py
```

6. **Open your browser**
```
http://localhost:8000/app
```

## 📁 Project Structure

```
ai-photo-style-converter/
├── backend/
│   ├── app.py                 # Main FastAPI application
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # AI model implementations
│   │   ├── cartoon_transformer.py
│   │   ├── neural_style.py
│   │   └── opencv_styles.py
│   ├── utils/                 # Utility functions
│   │   ├── image_processor.py
│   │   ├── video_processor.py
│   │   └── style_loader.py
│   ├── pretrained/            # Model weight files (.pth)
│   └── static/                # Frontend files
│       ├── index.html
│       ├── css/
│       └── js/
├── docs/                      # Documentation
│   ├── API.md
│   ├── MODELS.md
│   └── DEPLOYMENT.md
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8000/app
```

## 📖 Documentation

- [API Documentation](docs/API.md) - API endpoints and usage
- [Model Information](docs/MODELS.md) - Download and setup models
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment

## 🎯 Usage

1. **Upload** a photo or video (or use webcam)
2. **Select** an artistic style
3. **Adjust** intensity (images only)
4. **Download** your styled result

### Supported Formats
- **Images**: JPG, PNG, WebP
- **Videos**: MP4, AVI, MOV, GIF (up to 50MB)

## ⚙️ Configuration

Edit `backend/config.py` to customize:
- Max file size
- Image processing size
- Model paths
- Server settings

## 🔧 Troubleshooting

**Slow video processing?**
- Videos are processed frame-by-frame on CPU
- Reduce video length or resolution
- Expect 10-15 minutes for 5-second videos

**Models not loading?**
- Check model files are in `backend/pretrained/`
- Verify filenames match config
- See [MODELS.md](docs/MODELS.md) for details

**Port 8000 already in use?**
- Change port in `backend/config.py`
- Or kill existing process

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Credits

- **FastAPI** - Web framework
- **PyTorch** - Neural style transfer models
- **OpenCV** - Image processing
- **CartoonGAN** - Anime style models

## 📧 Contact

Name - amanansari789dk@gmail.com

Project Link: https://github.com/Redfire-1234/ai-photo-style-converter

---

Made with ❤️ using Python, FastAPI, and PyTorch
