# Model Information

## Overview

This application uses three types of style transfer models:

1. **OpenCV Styles** - No models needed, pure algorithmic processing
2. **Neural Style Transfer** - Pre-trained PyTorch models
3. **CartoonGAN/Anime Styles** - Pre-trained transformer models

## Model Requirements

### OpenCV Styles (No Download Needed) ✅
These styles use OpenCV algorithms and don't require model files:
- Pencil Sketch
- Charcoal Sketch
- Watercolor
- Oil Painting
- Crayon Color
- Rough Paper
- Sepia
- Vintage
- HDR Effect
- Pop Art
- Emboss
- Cartoon

### Neural Style Transfer Models 📥

**Location:** `backend/pretrained/`

**Required Files:**
- `candy.pth` (6.4 MB)
- `mosaic.pth` (6.4 MB)
- `rain_princess.pth` (6.4 MB)
- `udnie.pth` (6.4 MB)

**Download from:**
```bash
# Option 1: Download from PyTorch examples
wget https://www.dropbox.com/s/lrvwfehqdcxoza8/candy.pth
wget https://www.dropbox.com/s/ceiunep8pf21cvi/mosaic.pth
wget https://www.dropbox.com/s/oeihkfcwvq4v32r/rain_princess.pth
wget https://www.dropbox.com/s/7cklny3xu7fcvim/udnie.pth

# Option 2: Manual download
# Visit: https://github.com/pytorch/examples/tree/main/fast_neural_style
```

Or use this Python script to download:

```python
import urllib.request
import os

models = {
    "candy.pth": "https://www.dropbox.com/s/lrvwfehqdcxoza8/candy.pth?dl=1",
    "mosaic.pth": "https://www.dropbox.com/s/ceiunep8pf21cvi/mosaic.pth?dl=1",
    "rain_princess.pth": "https://www.dropbox.com/s/oeihkfcwvq4v32r/rain_princess.pth?dl=1",
    "udnie.pth": "https://www.dropbox.com/s/7cklny3xu7fcvim/udnie.pth?dl=1"
}

os.makedirs("pretrained", exist_ok=True)

for name, url in models.items():
    print(f"Downloading {name}...")
    urllib.request.urlretrieve(url, f"pretrained/{name}")
    print(f"✓ {name} downloaded")

print("\n✅ All models downloaded successfully!")
```

### CartoonGAN/Anime Models 📥

**Location:** `backend/pretrained/`

**Required Files:**
- `shinkai.pth` (~8 MB) - Your Name anime style
- `hayao.pth` (~8 MB) - Miyazaki anime style
- `hosoda.pth` (~8 MB) - Hosoda anime style
- `paprika.pth` (~8 MB) - Paprika anime style

**Download from:**
```bash
# These models are from CartoonGAN project
# Visit: https://github.com/SystemErrorWang/White-box-Cartoonization
# Or: https://github.com/TachibanaYoshino/AnimeGANv2

# Direct links (if available from your source):
# Place your download links here
```

**Important:** The anime models must match the `Transformer` architecture defined in `backend/models/cartoon_transformer.py`. Ensure compatibility before use.

---

## Model Architecture Details

### Neural Style Transfer Models

**Architecture:** Fast Neural Style Transfer
- Input: RGB image (any size)
- Output: Stylized RGB image (same size as input)
- Normalization: Input `[0,1] → [-1,1]`, Output `[-1,1] → [0,1]`
- Framework: PyTorch

**Network Structure:**
```
Input (3 channels)
  ↓
Encoder (Conv layers + InstanceNorm)
  ↓
8 Residual Blocks
  ↓
Decoder (Transposed Conv + InstanceNorm)
  ↓
Output (3 channels, Tanh activation)
```

### CartoonGAN Models

**Architecture:** Transformer Network with Custom InstanceNorm
- Input: RGB image (any size, resized to 512x512 internally)
- Output: Stylized RGB image (resized back to original)
- Normalization: Input `[0,1] → [-1,1]`, Output BGR→RGB swap, `[-1,1] → [0,1]`
- Framework: PyTorch

**Network Structure:**
```
Input (3 channels)
  ↓
Downsampling (2 Conv blocks)
  ↓
8 Residual Blocks (256 channels)
  ↓
Upsampling (2 Deconv blocks)
  ↓
Output (3 channels, Tanh activation)
```

---

## File Structure

Place model files in this structure:

```
backend/
└── pretrained/
    ├── candy.pth
    ├── mosaic.pth
    ├── rain_princess.pth
    ├── udnie.pth
    ├── shinkai.pth
    ├── hayao.pth
    ├── hosoda.pth
    └── paprika.pth
```

---

## Model Loading

Models are loaded once at application startup:

```python
# From backend/utils/style_loader.py
style_loader = StyleLoader()
```

Loading status is printed to console:
```
==================================================
Loading Style Models...
==================================================
✓ Loaded candy model
✓ Loaded mosaic model
✓ Loaded rain_princess model
✓ Loaded udnie model
✓ Loaded shinkai CartoonGAN model
✓ Loaded hayao CartoonGAN model
...
```

If a model fails to load, the application will still run but that style won't be available.

---

## Performance Characteristics

### Processing Time (on CPU)

**Images (1024x1024):**
- OpenCV styles: 0.1-0.5 seconds
- Neural styles: 2-5 seconds
- Anime styles: 3-8 seconds

**Videos (5 seconds, 30fps = 150 frames):**
- OpenCV styles: 15-30 seconds
- Neural styles: 5-10 minutes
- Anime styles: 10-20 minutes

### Memory Usage

- Base application: ~500 MB
- Neural model loaded: +50 MB per model
- Anime model loaded: +100 MB per model
- Image processing: ~100-200 MB
- Video processing: ~500 MB - 2 GB (depends on length)

**Recommended:** 4GB+ RAM for video processing

---

## Training Your Own Models

If you want to train custom style models:

**Neural Style Transfer:**
1. Use PyTorch Fast Neural Style Transfer tutorial
2. Train on your style images
3. Export model as `.pth` file
4. Place in `pretrained/` folder

**CartoonGAN:**
1. Follow CartoonGAN/AnimeGAN training guide
2. Ensure architecture matches `cartoon_transformer.py`
3. Export as `.pth` with state_dict
4. Test compatibility before deployment

---

## Troubleshooting

**Models not loading:**
- Check file permissions
- Verify file integrity (not corrupted)
- Ensure correct filenames (case-sensitive)
- Check console output for specific errors

**Out of memory:**
- Reduce `MAX_IMAGE_SIZE` in config
- Limit video frame count
- Process shorter videos
- Use OpenCV styles (no models needed)

**Slow processing:**
- Expected on CPU
- Use OpenCV styles for speed
- Consider GPU deployment for production
- Reduce input image/video size

---

## License & Attribution

**Neural Style Transfer Models:**
- Based on PyTorch examples
- Original paper: "Perceptual Losses for Real-Time Style Transfer and Super-Resolution"
- License: BSD

**CartoonGAN Models:**
- Based on White-box Cartoonization / AnimeGAN
- Varies by model source
- Check original repository for license

Always credit original authors when using pre-trained models.
