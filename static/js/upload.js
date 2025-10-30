// Upload form handling - Simple and reliable

document.addEventListener('DOMContentLoaded', function() {
    console.log('Upload script loaded');
    
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const fileInput = document.getElementById('audio_file');
    const uploadArea = document.getElementById('uploadArea');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileDetails = document.getElementById('fileDetails');
    const removeFileBtn = document.getElementById('removeFile');
    
    if (!uploadForm || !submitBtn || !fileInput || !uploadArea) {
        console.error('Required elements not found');
        return;
    }
    
    const processingModal = new bootstrap.Modal(document.getElementById('processingModal'));
    let selectedFile = null;
    
    // Upload area interactions - prevent event propagation issues
    uploadArea.addEventListener('click', function(e) {
        // Only trigger if the click is on the upload area itself, not the file input
        if (e.target === uploadArea || uploadArea.contains(e.target)) {
            console.log('Upload area clicked');
            // The file input overlay should handle the click
        }
    });
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#0d6efd';
        uploadArea.style.background = 'rgba(13, 110, 253, 0.1)';
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.background = 'transparent';
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#dee2e6';
        uploadArea.style.background = 'transparent';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    // File selection handler
    function handleFileSelection(file) {
        console.log('File selected:', file.name, file.size);
        
        // Validate file type
        const validTypes = ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/mp4', 'audio/m4a'];
        const validExtensions = /\.(mp3|wav|mp4|m4a)$/i;
        
        if (!validTypes.includes(file.type) && !file.name.toLowerCase().match(validExtensions)) {
            showAlert('error', 'Invalid file type. Please upload MP3, WAV, MP4, or M4A audio files only.');
            return;
        }
        
        // Validate file size (100MB)
        if (file.size > 100 * 1024 * 1024) {
            showAlert('error', 'File is too large. Maximum size is 100MB.');
            return;
        }
        
        selectedFile = file;
        displayFileInfo(file);
        validateForm();
    }
    
    // Display file information
    function displayFileInfo(file) {
        const fileSize = formatFileSize(file.size);
        const fileType = file.type || 'Unknown';
        
        fileName.textContent = file.name;
        fileDetails.textContent = `Size: ${fileSize} | Type: ${fileType}`;
        fileInfo.style.display = 'block';
        uploadArea.style.display = 'none';
    }
    
    // Remove file
    removeFileBtn.addEventListener('click', function() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadArea.style.display = 'block';
        validateForm();
    });

    // Form validation
    function validateForm() {
        const meetingTitle = document.getElementById('meeting_title').value.trim();
        const hasFile = selectedFile !== null || fileInput.files.length > 0;
        
        submitBtn.disabled = !(meetingTitle && hasFile);
        return meetingTitle && hasFile;
    }

    // Form input listeners
    document.getElementById('meeting_title').addEventListener('input', validateForm);
    
    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            showAlert('error', 'Please fill in all required fields and select an audio file.');
            return;
        }
        
        // Make sure we have a file in the form data
        if (!selectedFile && fileInput.files.length === 0) {
            showAlert('error', 'Please select an audio file.');
            return;
        }
        
        // Show processing modal
        processingModal.show();
        
        // Submit form
        const formData = new FormData(uploadForm);
        
        fetch(uploadForm.action, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                // Handle redirect
                window.location.href = response.url;
            } else {
                return response.text();
            }
        })
        .then(html => {
            if (html) {
                // Handle error response
                processingModal.hide();
                document.body.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            processingModal.hide();
            showAlert('error', 'An error occurred while uploading the file. Please try again.');
        });
    });

    // Helper functions
    function createFileList(files) {
        const dt = new DataTransfer();
        files.forEach(file => dt.items.add(file));
        return dt.files;
    }

    function showFileInfo(file) {
        hideFileInfo(); // Remove any existing info
        
        const fileSize = formatFileSize(file.size);
        const fileType = file.type || 'Unknown';
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'file-upload-info mt-3';
        infoDiv.id = 'fileInfo';
        infoDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file-audio text-success me-3 fa-2x"></i>
                <div class="flex-grow-1">
                    <h6 class="mb-1">${file.name}</h6>
                    <small class="text-muted">
                        Size: ${fileSize} | Type: ${fileType}
                    </small>
                </div>
                <i class="fas fa-check-circle text-success fa-lg"></i>
            </div>
        `;
        
        dropzoneElement.parentNode.insertBefore(infoDiv, dropzoneElement.nextSibling);
    }

    function hideFileInfo() {
        const existingInfo = document.getElementById('fileInfo');
        if (existingInfo) {
            existingInfo.remove();
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // File input change listener
    fileInput.addEventListener('change', function(e) {
        console.log('File input changed', e.target.files.length);
        
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            handleFileSelection(file);
        }
    });

    // Initial form validation
    validateForm();
});
