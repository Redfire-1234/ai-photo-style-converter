# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**GET** `/`

Check if API is running.

**Response:**
```json
{
  "message": "AI Photo Style Converter API",
  "status": "running"
}
```

---

### 2. Get Available Styles

**GET** `/api/styles`

Returns list of all available styles.

**Response:**
```json
{
  "styles": ["pencil_sketch", "watercolor", "candy", "shinkai", ...],
  "opencv_styles": ["pencil_sketch", "charcoal_sketch", ...],
  "neural_styles": ["candy", "mosaic", "rain_princess", "udnie"],
  "cartoon_styles": ["shinkai", "hayao", "hosoda", "paprika"]
}
```

---

### 3. Upload Media

**POST** `/api/upload`

Upload an image or video file.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: Image or video file (JPG, PNG, WebP, MP4, GIF, etc.)

**Limits:**
- Max file size: 50MB
- Supported formats: JPG, JPEG, PNG, WebP, MP4, AVI, MOV, GIF

**Response:**
```json
{
  "media_id": "uuid-string",
  "filename": "photo.jpg",
  "is_video": false
}
```

**Error Responses:**
- `400` - Invalid file extension or file too large
- `500` - Upload failed

---

### 4. Convert Style

**POST** `/api/convert`

Apply artistic style to uploaded media.

**Request:**
- **Content-Type:** `application/x-www-form-urlencoded`
- **Body:**
  - `media_id`: UUID from upload response
  - `style`: Style name (e.g., "watercolor", "candy", "shinkai")

**Response:**
- **Content-Type:** `image/jpeg` (for images) or `video/mp4` / `image/gif` (for videos)
- Binary file data

**Processing Time:**
- Images: 1-5 seconds
- Videos: 1-3 minutes (depends on length and style)

**Error Responses:**
- `404` - Media not found
- `400` - Invalid style name
- `500` - Style conversion failed

---

### 5. Delete Media

**DELETE** `/api/delete/{media_id}`

Delete uploaded media from server memory.

**Parameters:**
- `media_id`: UUID of the media to delete

**Response:**
```json
{
  "message": "Media deleted"
}
```

**Error Responses:**
- `404` - Media not found

---

## Example Usage

### Python Example

```python
import requests

# 1. Upload image
with open('photo.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f}
    )
    media_id = response.json()['media_id']

# 2. Apply style
response = requests.post(
    'http://localhost:8000/api/convert',
    data={
        'media_id': media_id,
        'style': 'watercolor'
    }
)

# 3. Save result
with open('styled.jpg', 'wb') as f:
    f.write(response.content)

# 4. Delete from server
requests.delete(f'http://localhost:8000/api/delete/{media_id}')
```

### JavaScript Example

```javascript
// 1. Upload image
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData
});
const { media_id } = await uploadResponse.json();

// 2. Apply style
const convertFormData = new FormData();
convertFormData.append('media_id', media_id);
convertFormData.append('style', 'candy');

const convertResponse = await fetch('http://localhost:8000/api/convert', {
    method: 'POST',
    body: convertFormData
});

// 3. Get result as blob
const blob = await convertResponse.blob();
const url = URL.createObjectURL(blob);

// 4. Display or download
document.getElementById('result').src = url;
```

### cURL Example

```bash
# Upload image
curl -X POST http://localhost:8000/api/upload \
  -F "file=@photo.jpg" \
  -o upload_response.json

# Extract media_id from response
MEDIA_ID=$(cat upload_response.json | jq -r '.media_id')

# Apply style
curl -X POST http://localhost:8000/api/convert \
  -F "media_id=$MEDIA_ID" \
  -F "style=watercolor" \
  -o styled.jpg

# Delete media
curl -X DELETE http://localhost:8000/api/delete/$MEDIA_ID
```

---

## Style Names Reference

### OpenCV Styles (Fast)
- `pencil_sketch`
- `charcoal_sketch`
- `watercolor`
- `oil_painting`
- `crayon_color`
- `rough_paper`
- `sepia`
- `vintage`
- `hdr_effect`
- `pop_art`
- `emboss`
- `cartoon`

### Neural Styles (Medium)
- `candy`
- `mosaic`
- `rain_princess`
- `udnie`

### Anime Styles (Slow)
- `shinkai`
- `hayao`
- `hosoda`
- `paprika`

---

## Rate Limits

Currently no rate limits implemented. For production deployment, consider adding:
- Request rate limiting
- Concurrent processing limits
- Memory management for large files

---

## CORS

CORS is enabled for all origins (`*`) by default. For production, update `app.py` to restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
