const API = {
    BASE_URL: 'http://localhost:8000',
    
    async getStyles() {
        const response = await fetch(`${this.BASE_URL}/api/styles`);
        if (!response.ok) throw new Error('Failed to fetch styles');
        return await response.json();
    },
    
    async uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        return await response.json();
    },
    
    async convertStyle(mediaId, style) {
        const formData = new FormData();
        formData.append('media_id', mediaId);  // Changed from image_id to media_id
        formData.append('style', style);
        
        const response = await fetch(`${this.BASE_URL}/api/convert`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Conversion failed');
        }
        return await response.blob();
    },
    
    async deleteImage(mediaId) {
        const response = await fetch(`${this.BASE_URL}/api/delete/${mediaId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Delete failed');
        }
        return await response.json();
    }
};