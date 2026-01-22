const API = {
    BASE_URL: window.location.origin,
    
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
            const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(error.detail || 'Upload failed');
        }
        return await response.json();
    },
    
    async convertStyle(mediaId, style) {
        const formData = new FormData();
        formData.append('media_id', mediaId);
        formData.append('style', style);
        
        try {
            const response = await fetch(`${this.BASE_URL}/api/convert`, {
                method: 'POST',
                body: formData,
                // Add timeout of 5 minutes for video processing
                signal: AbortSignal.timeout(300000)
            });
            
            // Check content type
            const contentType = response.headers.get('content-type');
            
            if (!response.ok) {
                // Try to get JSON error
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Conversion failed');
                } else {
                    // If HTML error page, extract useful info
                    const text = await response.text();
                    console.error('Server returned HTML error:', text);
                    throw new Error(`Server error (${response.status}): The server encountered an error processing this style.`);
                }
            }
            
            // Check if we got a valid response
            if (!contentType || (!contentType.includes('image') && !contentType.includes('video'))) {
                const text = await response.text();
                console.error('Unexpected response type:', contentType, text);
                throw new Error('Server returned unexpected response. Please try again.');
            }
            
            return await response.blob();
            
        } catch (error) {
            if (error.name === 'TimeoutError') {
                throw new Error('Processing timeout. Video may be too long or complex.');
            }
            throw error;
        }
    },
    
    async deleteImage(mediaId) {
        const response = await fetch(`${this.BASE_URL}/api/delete/${mediaId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Delete failed' }));
            throw new Error(error.detail || 'Delete failed');
        }
        return await response.json();
    }
};

// const API = {
//     BASE_URL: window.location.origin, // Use current domain (works both locally and on Render)
    
//     async getStyles() {
//         const response = await fetch(`${this.BASE_URL}/api/styles`); // Fixed: Added parentheses
//         if (!response.ok) throw new Error('Failed to fetch styles');
//         return await response.json();
//     },
    
//     async uploadImage(file) {
//         const formData = new FormData();
//         formData.append('file', file);
        
//         const response = await fetch(`${this.BASE_URL}/api/upload`, { // Fixed: Added parentheses
//             method: 'POST',
//             body: formData
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Upload failed');
//         }
//         return await response.json();
//     },
    
//     async convertStyle(mediaId, style) {
//         const formData = new FormData();
//         formData.append('media_id', mediaId);
//         formData.append('style', style);
        
//         const response = await fetch(`${this.BASE_URL}/api/convert`, { // Fixed: Added parentheses
//             method: 'POST',
//             body: formData
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Conversion failed');
//         }
//         return await response.blob();
//     },
    
//     async deleteImage(mediaId) {
//         const response = await fetch(`${this.BASE_URL}/api/delete/${mediaId}`, { // Fixed: Added parentheses
//             method: 'DELETE'
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Delete failed');
//         }
//         return await response.json();
//     }
// };
