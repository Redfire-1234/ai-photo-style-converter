class CameraHandler {
    constructor() {
        this.stream = null;
        this.video = null;
        this.modal = null;
    }

    init() {
        this.video = document.getElementById('cameraPreview');
        this.modal = document.getElementById('cameraModal');
    }

    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user' }
            });
            
            this.video.srcObject = this.stream;
            this.modal.style.display = 'flex';
        } catch (error) {
            alert('Camera access denied or not available');
            console.error('Camera error:', error);
        }
    }

    capture() {
        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.video, 0, 0);
        
        canvas.toBlob((blob) => {
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
            window.handleImageFile(file);
        }, 'image/jpeg', 0.95);
        
        this.stop();
    }

    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.modal.style.display = 'none';
    }
}