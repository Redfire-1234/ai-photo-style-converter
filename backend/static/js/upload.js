class UploadHandler {
    constructor() {
        this.fileInput = null;
        this.uploadArea = null;
    }

    init() {
        this.fileInput = document.getElementById('fileInput');
        this.uploadArea = document.querySelector('.upload-controls');
        if (this.uploadArea) {
            this.setupDragDrop();
        }
    }

    setupDragDrop() {
        const dropZone = document.querySelector('.container');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.style.opacity = '0.8';
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.style.opacity = '1';
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    handleFile(file) {
        // ✅ FIXED: Now accepts both images and videos
        const validTypes = ['image/', 'video/'];
        const isValid = validTypes.some(type => file.type.startsWith(type));
        
        // Also check for GIF specifically (sometimes has different MIME type)
        const isGif = file.name.toLowerCase().endsWith('.gif');
        
        if (!isValid && !isGif) {
            alert('Please select an image or video file');
            return;
        }

        // ✅ FIXED: Increased size limit for videos (50MB to match backend)
        if (file.size > 50 * 1024 * 1024) {
            alert('File too large. Maximum 50MB allowed.');
            return;
        }

        window.handleImageFile(file);
    }

    triggerFileSelect() {
        if (this.fileInput) {
            this.fileInput.click();
        }
    }
}