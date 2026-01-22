let currentMediaId = null;
let currentImageBlob = null;
let currentStyleBlob = null;
let availableStyles = [];
let currentCategory = 'all';
let originalImageData = null;
let styledImageData = null;
let currentIntensity = 100;
let isVideo = false;

const camera = new CameraHandler();
const uploader = new UploadHandler();

const styleIcons = {
    pencil_sketch: '✏️',
    charcoal_sketch: '🖊️',
    watercolor: '🎨',
    oil_painting: '🖌️',
    crayon_color: '🖍️',
    rough_paper: '📄',
    sepia: '🌅',
    vintage: '📷',
    hdr_effect: '✨',
    pop_art: '🎭',
    emboss: '🔨',
    cartoon: '🎪',
    candy: '🍬',
    mosaic: '🔲',
    rain_princess: '🌧️',
    udnie: '🎨',
    shinkai: '⛅',
    hayao: '🌿',
    hosoda: '🌸',
    paprika: '🎪'
};

window.addEventListener('DOMContentLoaded', async () => {
    camera.init();
    uploader.init();
    
    await loadStyles();
    setupEventListeners();
});

async function loadStyles() {
    try {
        const data = await API.getStyles();
        availableStyles = data.styles;
        document.getElementById('styleCount').textContent = `${availableStyles.length} styles`;
        renderStyleGrid();
    } catch (error) {
        console.error('Failed to load styles:', error);
    }
}

function renderStyleGrid() {
    const grid = document.getElementById('styleGrid');
    grid.innerHTML = '';
    
    const filtered = currentCategory === 'all' ? availableStyles :
        availableStyles.filter(s => {
            if (currentCategory === 'opencv') return ['pencil_sketch', 'charcoal_sketch', 'watercolor', 'oil_painting', 'crayon_color', 'rough_paper', 'sepia', 'vintage', 'hdr_effect', 'pop_art', 'emboss', 'cartoon'].includes(s);
            if (currentCategory === 'neural') return ['candy', 'mosaic', 'rain_princess', 'udnie'].includes(s);
            if (currentCategory === 'anime') return ['shinkai', 'hayao', 'hosoda', 'paprika'].includes(s);
        });
    
    filtered.forEach(style => {
        const card = document.createElement('div');
        card.className = 'style-card';
        card.innerHTML = `
            <div class="icon">${styleIcons[style] || '🎨'}</div>
            <h4>${formatStyleName(style)}</h4>
        `;
        card.addEventListener('click', () => applyStyle(style, card));
        grid.appendChild(card);
    });
}

function formatStyleName(style) {
    return style.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function setupEventListeners() {
    document.getElementById('uploadBtn').addEventListener('click', () => {
        uploader.triggerFileSelect();
    });
    
    document.getElementById('fileInput').addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploader.handleFile(e.target.files[0]);
        }
    });
    
    document.getElementById('cameraBtn').addEventListener('click', () => {
        camera.start();
    });
    
    document.getElementById('captureBtn').addEventListener('click', () => {
        camera.capture();
    });
    
    document.getElementById('closeCameraBtn').addEventListener('click', () => {
        camera.stop();
    });
    
    document.getElementById('removeBtn').addEventListener('click', removePhoto);
    document.getElementById('downloadBtn').addEventListener('click', downloadStyledMedia);
    document.getElementById('addAnotherBtn').addEventListener('click', addAnother);
    document.getElementById('compareBtn').addEventListener('click', showComparison);
    document.getElementById('closeComparisonBtn').addEventListener('click', hideComparison);
    
    const intensitySlider = document.getElementById('intensitySlider');
    intensitySlider.addEventListener('input', (e) => {
        currentIntensity = e.target.value;
        document.getElementById('intensityValue').textContent = currentIntensity + '%';
        applyIntensity();
    });
    
    document.getElementById('comparisonSlider').addEventListener('input', (e) => {
        document.getElementById('comparisonOverlay').style.width = e.target.value + '%';
    });
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentCategory = e.target.dataset.category;
            renderStyleGrid();
        });
    });
}

// ✅ FIXED: Upload first, then display preview
window.handleImageFile = async function(file) {
    try {
        // Show loading state
        console.log('Uploading file:', file.name);
        
        // ✅ UPLOAD FIRST - Get media_id before displaying
        const response = await API.uploadImage(file);
        currentMediaId = response.media_id;
        isVideo = response.is_video;
        
        console.log('Upload successful! Media ID:', currentMediaId, 'Is video:', isVideo);
        
        // Now display the preview
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImageData = e.target.result;
            
            if (isVideo) {
                document.getElementById('originalImage').style.display = 'none';
                const videoEl = document.getElementById('originalVideo');
                videoEl.src = originalImageData;
                videoEl.style.display = 'block';
                
                document.getElementById('intensityControl').style.display = 'none';
                document.getElementById('compareBtn').style.display = 'none';
            } else {
                document.getElementById('originalVideo').style.display = 'none';
                const imgEl = document.getElementById('originalImage');
                imgEl.src = originalImageData;
                imgEl.style.display = 'block';
            }
            
            document.getElementById('previewSection').style.display = 'block';
            document.getElementById('styleSection').style.display = 'block';
            document.getElementById('removeBtn').style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
        
    } catch (error) {
        console.error('Upload failed:', error);
        alert('Failed to upload: ' + error.message);
        // Reset state on error
        currentMediaId = null;
        isVideo = false;
    }
};

async function applyStyle(styleName, cardElement) {
    // ✅ ADDED: Better validation
    if (!currentMediaId) {
        alert('Please upload an image or video first');
        console.error('No media ID available');
        return;
    }
    
    console.log('Applying style:', styleName, 'to media:', currentMediaId);
    
    document.querySelectorAll('.style-card').forEach(card => card.classList.remove('active'));
    cardElement.classList.add('active');
    
    document.getElementById('loader').style.display = 'block';
    document.getElementById('styledImage').style.display = 'none';
    document.getElementById('styledVideo').style.display = 'none';
    document.getElementById('placeholderText').style.display = 'none';
    
    if (isVideo) {
        document.getElementById('processingInfo').style.display = 'block';
    }
    
    try {
        const blob = await API.convertStyle(currentMediaId, styleName);
        currentStyleBlob = blob;
        
        console.log('Style applied successfully, blob size:', blob.size);
        
        if (isVideo) {
            const url = URL.createObjectURL(blob);
            const videoEl = document.getElementById('styledVideo');
            videoEl.src = url;
            videoEl.style.display = 'block';
            document.getElementById('processingInfo').style.display = 'none';
        } else {
            const reader = new FileReader();
            reader.onload = (e) => {
                styledImageData = e.target.result;
                currentIntensity = 100;
                document.getElementById('intensitySlider').value = 100;
                document.getElementById('intensityValue').textContent = '100%';
                applyIntensity();
            };
            reader.readAsDataURL(blob);
            
            document.getElementById('intensityControl').style.display = 'block';
            document.getElementById('compareBtn').style.display = 'inline-block';
        }
        
        document.getElementById('downloadBtn').style.display = 'inline-block';
        document.getElementById('addAnotherBtn').style.display = 'inline-block';
        
    } catch (error) {
        console.error('Style conversion error:', error);
        alert('Style conversion failed: ' + error.message);
        document.getElementById('placeholderText').style.display = 'block';
        document.getElementById('placeholderText').textContent = 'Conversion failed. Try again.';
        document.getElementById('processingInfo').style.display = 'none';
    } finally {
        document.getElementById('loader').style.display = 'none';
    }
}

function applyIntensity() {
    if (!originalImageData || !styledImageData) return;
    
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    const original = new Image();
    const styled = new Image();
    
    let loadedCount = 0;
    
    const process = () => {
        loadedCount++;
        if (loadedCount !== 2) return;
        
        canvas.width = styled.width;
        canvas.height = styled.height;
        
        ctx.globalAlpha = 1 - (currentIntensity / 100);
        ctx.drawImage(original, 0, 0, canvas.width, canvas.height);
        
        ctx.globalAlpha = currentIntensity / 100;
        ctx.drawImage(styled, 0, 0, canvas.width, canvas.height);
        
        const styledImg = document.getElementById('styledImage');
        styledImg.src = canvas.toDataURL('image/jpeg', 0.95);
        styledImg.style.display = 'block';
    };
    
    original.onload = process;
    styled.onload = process;
    original.src = originalImageData;
    styled.src = styledImageData;
}

function removePhoto() {
    if (currentMediaId) {
        console.log('Deleting media:', currentMediaId);
        API.deleteImage(currentMediaId);
    }
    
    currentMediaId = null;
    currentImageBlob = null;
    currentStyleBlob = null;
    originalImageData = null;
    styledImageData = null;
    isVideo = false;
    
    document.getElementById('previewSection').style.display = 'none';
    document.getElementById('styleSection').style.display = 'none';
    document.getElementById('removeBtn').style.display = 'none';
    document.getElementById('intensityControl').style.display = 'none';
    document.getElementById('fileInput').value = '';
    
    document.getElementById('originalVideo').style.display = 'none';
    document.getElementById('styledVideo').style.display = 'none';
    document.getElementById('processingInfo').style.display = 'none';
    
    document.querySelectorAll('.style-card').forEach(card => card.classList.remove('active'));
}

function addAnother() {
    removePhoto();
    document.getElementById('uploadBtn').click();
}

function downloadStyledMedia() {
    if (isVideo) {
        if (!currentStyleBlob) return;
        const url = URL.createObjectURL(currentStyleBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'styled-video.' + (currentStyleBlob.type.includes('gif') ? 'gif' : 'mp4');
        a.click();
        URL.revokeObjectURL(url);
    } else {
        const styledImg = document.getElementById('styledImage');
        if (!styledImg || !styledImg.src) return;
        const a = document.createElement('a');
        a.href = styledImg.src;
        a.download = 'styled-image.jpg';
        a.click();
    }
}

function showComparison() {
    if (!originalImageData || isVideo) return;
    
    const modal = document.getElementById('comparisonModal');
    const originalImg = document.getElementById('comparisonOriginal');
    const styledImg = document.getElementById('comparisonStyled');
    const overlay = document.getElementById('comparisonOverlay');
    const slider = document.getElementById('comparisonSlider');
    
    const currentStyledImg = document.getElementById('styledImage');
    const currentStyledSrc = currentStyledImg.src;
    
    originalImg.src = currentStyledSrc;
    styledImg.src = originalImageData;
    
    slider.value = 50;
    overlay.style.width = '50%';
    
    modal.style.display = 'flex';
    
    originalImg.onload = () => {
        const imgWidth = originalImg.offsetWidth;
        overlay.style.width = '50%';
        styledImg.style.width = imgWidth + 'px';
    };
}

function hideComparison() {
    document.getElementById('comparisonModal').style.display = 'none';
}

// let currentMediaId = null;  // Changed from currentImageId
// let currentImageBlob = null;
// let currentStyleBlob = null;
// let availableStyles = [];
// let currentCategory = 'all';
// let originalImageData = null;
// let styledImageData = null;
// let currentIntensity = 100;
// let isVideo = false;

// const camera = new CameraHandler();
// const uploader = new UploadHandler();

// const styleIcons = {
//     pencil_sketch: '✏️',
//     charcoal_sketch: '🖊️',
//     watercolor: '🎨',
//     oil_painting: '🖌️',
//     crayon_color: '🖍️',
//     rough_paper: '📄',
//     sepia: '🌅',
//     vintage: '📷',
//     hdr_effect: '✨',
//     pop_art: '🎭',
//     emboss: '🔨',
//     cartoon: '🎪',
//     candy: '🍬',
//     mosaic: '🔲',
//     rain_princess: '🌧️',
//     udnie: '🎨',
//     shinkai: '⛅',
//     hayao: '🌿',
//     hosoda: '🌸',
//     paprika: '🎪'
// };

// window.addEventListener('DOMContentLoaded', async () => {
//     // Initialize handlers after DOM is ready
//     camera.init();
//     uploader.init();
    
//     await loadStyles();
//     setupEventListeners();
// });

// async function loadStyles() {
//     try {
//         const data = await API.getStyles();
//         availableStyles = data.styles;
//         document.getElementById('styleCount').textContent = `${availableStyles.length} styles`;
//         renderStyleGrid();
//     } catch (error) {
//         console.error('Failed to load styles:', error);
//     }
// }

// function renderStyleGrid() {
//     const grid = document.getElementById('styleGrid');
//     grid.innerHTML = '';
    
//     const filtered = currentCategory === 'all' ? availableStyles :
//         availableStyles.filter(s => {
//             if (currentCategory === 'opencv') return ['pencil_sketch', 'charcoal_sketch', 'watercolor', 'oil_painting', 'crayon_color', 'rough_paper', 'sepia', 'vintage', 'hdr_effect', 'pop_art', 'emboss', 'cartoon'].includes(s);
//             if (currentCategory === 'neural') return ['candy', 'mosaic', 'rain_princess', 'udnie'].includes(s);
//             if (currentCategory === 'anime') return ['shinkai', 'hayao', 'hosoda', 'paprika'].includes(s);
//         });
    
//     filtered.forEach(style => {
//         const card = document.createElement('div');
//         card.className = 'style-card';
//         card.innerHTML = `
//             <div class="icon">${styleIcons[style] || '🎨'}</div>
//             <h4>${formatStyleName(style)}</h4>
//         `;
//         card.addEventListener('click', () => applyStyle(style, card));
//         grid.appendChild(card);
//     });
// }

// function formatStyleName(style) {
//     return style.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
// }

// function setupEventListeners() {
//     document.getElementById('uploadBtn').addEventListener('click', () => {
//         uploader.triggerFileSelect();
//     });
    
//     document.getElementById('fileInput').addEventListener('change', (e) => {
//         if (e.target.files.length > 0) {
//             uploader.handleFile(e.target.files[0]);
//         }
//     });
    
//     document.getElementById('cameraBtn').addEventListener('click', () => {
//         camera.start();
//     });
    
//     document.getElementById('captureBtn').addEventListener('click', () => {
//         camera.capture();
//     });
    
//     document.getElementById('closeCameraBtn').addEventListener('click', () => {
//         camera.stop();
//     });
    
//     document.getElementById('removeBtn').addEventListener('click', removePhoto);
//     document.getElementById('downloadBtn').addEventListener('click', downloadStyledMedia);
//     document.getElementById('addAnotherBtn').addEventListener('click', addAnother);
//     document.getElementById('compareBtn').addEventListener('click', showComparison);
//     document.getElementById('closeComparisonBtn').addEventListener('click', hideComparison);
    
//     // Intensity slider
//     const intensitySlider = document.getElementById('intensitySlider');
//     intensitySlider.addEventListener('input', (e) => {
//         currentIntensity = e.target.value;
//         document.getElementById('intensityValue').textContent = currentIntensity + '%';
//         applyIntensity();
//     });
    
//     // Comparison slider
//     document.getElementById('comparisonSlider').addEventListener('input', (e) => {
//         document.getElementById('comparisonOverlay').style.width = e.target.value + '%';
//     });
    
//     // Category tabs
//     document.querySelectorAll('.tab-btn').forEach(btn => {
//         btn.addEventListener('click', (e) => {
//             document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
//             e.target.classList.add('active');
//             currentCategory = e.target.dataset.category;
//             renderStyleGrid();
//         });
//     });
// }

// window.handleImageFile = async function(file) {
//     try {
//         // Check if video
//         const videoExtensions = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'gif'];
//         const ext = file.name.split('.').pop().toLowerCase();
//         isVideo = videoExtensions.includes(ext);
        
//         const reader = new FileReader();
//         reader.onload = (e) => {
//             originalImageData = e.target.result;
            
//             if (isVideo) {
//                 document.getElementById('originalImage').style.display = 'none';
//                 const videoEl = document.getElementById('originalVideo');
//                 videoEl.src = originalImageData;
//                 videoEl.style.display = 'block';
                
//                 // Hide intensity and compare for videos
//                 document.getElementById('intensityControl').style.display = 'none';
//                 document.getElementById('compareBtn').style.display = 'none';
//             } else {
//                 document.getElementById('originalVideo').style.display = 'none';
//                 const imgEl = document.getElementById('originalImage');
//                 imgEl.src = originalImageData;
//                 imgEl.style.display = 'block';
//             }
            
//             document.getElementById('previewSection').style.display = 'block';
//             document.getElementById('styleSection').style.display = 'block';
//             document.getElementById('removeBtn').style.display = 'inline-block';
//         };
//         reader.readAsDataURL(file);
        
//         const response = await API.uploadImage(file);
//         currentMediaId = response.media_id;  // Using media_id
//         isVideo = response.is_video;
        
//     } catch (error) {
//         alert('Failed to upload: ' + error.message);
//     }
// };

// async function applyStyle(styleName, cardElement) {
//     if (!currentMediaId) return;
    
//     document.querySelectorAll('.style-card').forEach(card => card.classList.remove('active'));
//     cardElement.classList.add('active');
    
//     document.getElementById('loader').style.display = 'block';
//     document.getElementById('styledImage').style.display = 'none';
//     document.getElementById('styledVideo').style.display = 'none';
//     document.getElementById('placeholderText').style.display = 'none';
    
//     if (isVideo) {
//         document.getElementById('processingInfo').style.display = 'block';
//     }
    
//     try {
//         const blob = await API.convertStyle(currentMediaId, styleName);
//         currentStyleBlob = blob;
        
//         if (isVideo) {
//             const url = URL.createObjectURL(blob);
//             const videoEl = document.getElementById('styledVideo');
//             videoEl.src = url;
//             videoEl.style.display = 'block';
//             document.getElementById('processingInfo').style.display = 'none';
//         } else {
//             const reader = new FileReader();
//             reader.onload = (e) => {
//                 styledImageData = e.target.result;
//                 currentIntensity = 100;
//                 document.getElementById('intensitySlider').value = 100;
//                 document.getElementById('intensityValue').textContent = '100%';
//                 applyIntensity();
//             };
//             reader.readAsDataURL(blob);
            
//             document.getElementById('intensityControl').style.display = 'block';
//             document.getElementById('compareBtn').style.display = 'inline-block';
//         }
        
//         document.getElementById('downloadBtn').style.display = 'inline-block';
//         document.getElementById('addAnotherBtn').style.display = 'inline-block';
        
//     } catch (error) {
//         alert('Style conversion failed: ' + error.message);
//         document.getElementById('placeholderText').style.display = 'block';
//         document.getElementById('processingInfo').style.display = 'none';
//     } finally {
//         document.getElementById('loader').style.display = 'none';
//     }
// }

// function applyIntensity() {
//     if (!originalImageData || !styledImageData) return;
    
//     const canvas = document.createElement('canvas');
//     const ctx = canvas.getContext('2d');
    
//     const original = new Image();
//     const styled = new Image();
    
//     let loadedCount = 0;
    
//     const process = () => {
//         loadedCount++;
//         if (loadedCount !== 2) return;
        
//         canvas.width = styled.width;
//         canvas.height = styled.height;
        
//         ctx.globalAlpha = 1 - (currentIntensity / 100);
//         ctx.drawImage(original, 0, 0, canvas.width, canvas.height);
        
//         ctx.globalAlpha = currentIntensity / 100;
//         ctx.drawImage(styled, 0, 0, canvas.width, canvas.height);
        
//         const styledImg = document.getElementById('styledImage');
//         styledImg.src = canvas.toDataURL('image/jpeg', 0.95);
//         styledImg.style.display = 'block';
//     };
    
//     original.onload = process;
//     styled.onload = process;
//     original.src = originalImageData;
//     styled.src = styledImageData;
// }

// function removePhoto() {
//     if (currentMediaId) {
//         API.deleteImage(currentMediaId);
//     }
    
//     currentMediaId = null;
//     currentImageBlob = null;
//     currentStyleBlob = null;
//     originalImageData = null;
//     styledImageData = null;
//     isVideo = false;
    
//     document.getElementById('previewSection').style.display = 'none';
//     document.getElementById('styleSection').style.display = 'none';
//     document.getElementById('removeBtn').style.display = 'none';
//     document.getElementById('intensityControl').style.display = 'none';
//     document.getElementById('fileInput').value = '';
    
//     // Hide video elements
//     document.getElementById('originalVideo').style.display = 'none';
//     document.getElementById('styledVideo').style.display = 'none';
//     document.getElementById('processingInfo').style.display = 'none';
    
//     document.querySelectorAll('.style-card').forEach(card => card.classList.remove('active'));
// }

// function addAnother() {
//     removePhoto();
//     document.getElementById('uploadBtn').click();
// }

// function downloadStyledMedia() {
//     if (isVideo) {
//         // Download video
//         if (!currentStyleBlob) return;
//         const url = URL.createObjectURL(currentStyleBlob);
//         const a = document.createElement('a');
//         a.href = url;
//         a.download = 'styled-video.' + (currentStyleBlob.type.includes('gif') ? 'gif' : 'mp4');
//         a.click();
//         URL.revokeObjectURL(url);
//     } else {
//         // Download image
//         const styledImg = document.getElementById('styledImage');
//         if (!styledImg || !styledImg.src) return;
//         const a = document.createElement('a');
//         a.href = styledImg.src;
//         a.download = 'styled-image.jpg';
//         a.click();
//     }
// }

// function showComparison() {
//     if (!originalImageData || isVideo) return;
    
//     const modal = document.getElementById('comparisonModal');
//     const originalImg = document.getElementById('comparisonOriginal');
//     const styledImg = document.getElementById('comparisonStyled');
//     const overlay = document.getElementById('comparisonOverlay');
//     const slider = document.getElementById('comparisonSlider');
    
//     // Use the currently displayed styled image (with intensity applied)
//     const currentStyledImg = document.getElementById('styledImage');
//     const currentStyledSrc = currentStyledImg.src;
    
//     // Set images - styled (with current intensity) vs original
//     originalImg.src = currentStyledSrc;  // Current styled version with intensity
//     styledImg.src = originalImageData;   // Original image
    
//     // Reset slider to middle
//     slider.value = 50;
//     overlay.style.width = '50%';
    
//     // Show modal
//     modal.style.display = 'flex';
    
//     // After images load, ensure proper sizing
//     originalImg.onload = () => {
//         const imgWidth = originalImg.offsetWidth;
//         overlay.style.width = '50%';
        
//         // Make sure the overlay image is positioned correctly
//         styledImg.style.width = imgWidth + 'px';
//     };
// }

// function hideComparison() {
//     document.getElementById('comparisonModal').style.display = 'none';
// }
