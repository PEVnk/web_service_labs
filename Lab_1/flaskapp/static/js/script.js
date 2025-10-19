// Update blend level display
document.getElementById('blendLevel').addEventListener('input', function() {
    document.getElementById('blendValue').textContent = this.value;
});

// Refresh CAPTCHA
document.getElementById('refreshCaptcha').addEventListener('click', function() {
    fetch('/new-captcha')
        .then(response => response.json())
        .then(data => {
            document.getElementById('captchaImage').src = 'data:image/png;base64,' + data.captcha_image;
            document.getElementById('captchaInput').value = '';
        });
});

// Image preview
document.getElementById('image1').addEventListener('change', function(e) {
    previewImage(e.target.files[0], 'preview1');
});

document.getElementById('image2').addEventListener('change', function(e) {
    previewImage(e.target.files[0], 'preview2');
});

function previewImage(file, previewId) {
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            preview.src = e.target.result;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

// Form submission
document.getElementById('blendForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    error.classList.add('hidden');
    
    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loading.classList.add('hidden');
        
        if (data.success) {
            // Display results
            document.getElementById('blendedResult').src = 'data:image/png;base64,' + data.blended_image;
            document.getElementById('result1').src = document.getElementById('preview1').src;
            document.getElementById('result2').src = document.getElementById('preview2').src;
            
            // Display histograms
            document.getElementById('histogram1').src = 'data:image/png;base64,' + data.histogram1;
            document.getElementById('histogram2').src = 'data:image/png;base64,' + data.histogram2;
            document.getElementById('histogramBlended').src = 'data:image/png;base64,' + data.histogram_blended;
            
            results.classList.remove('hidden');
        } else {
            error.textContent = data.error;
            error.classList.remove('hidden');
            document.getElementById('refreshCaptcha').click();
        }
    })
    .catch(error => {
        loading.classList.add('hidden');
        document.getElementById('error').textContent = 'Network error: ' + error.message;
        document.getElementById('error').classList.remove('hidden');
    });
});
