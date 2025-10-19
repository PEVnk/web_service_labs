from flask import Flask, render_template, request, jsonify, session
import os
import io
import base64
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import functions from net.py
from net import blend_images, generate_color_histograms, generate_captcha, verify_captcha

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-12345'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    """Simple version without CAPTCHA"""
    return render_template('simple.html')

@app.route('/advanced')
def advanced():
    """Advanced version with CAPTCHA and histograms"""
    # Generate CAPTCHA
    captcha_text, captcha_image = generate_captcha()
    session['captcha_text'] = captcha_text
    
    # Convert CAPTCHA image to base64
    buffered = io.BytesIO()
    captcha_image.save(buffered, format="PNG")
    captcha_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('net.html', captcha_image=captcha_b64)

@app.route('/process', methods=['POST'])
def process_images():
    """Process image blending with CAPTCHA verification"""
    try:
        # Verify CAPTCHA
        user_captcha = request.form.get('captcha', '').strip()
        if not verify_captcha(user_captcha, session.get('captcha_text')):
            return jsonify({
                'success': False, 
                'error': 'Invalid CAPTCHA. Please try again.'
            }), 400

        # Validate blend level
        try:
            blend_level = float(request.form.get('blend_level', 0.5))
            if not 0 <= blend_level <= 1:
                raise ValueError("Blend level must be between 0 and 1")
        except (ValueError, TypeError):
            return jsonify({
                'success': False, 
                'error': 'Invalid blend level. Must be between 0 and 1.'
            }), 400

        # Check file uploads
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({
                'success': False, 
                'error': 'Please upload both images.'
            }), 400

        image1 = request.files['image1']
        image2 = request.files['image2']

        # Check if files are selected
        if image1.filename == '' or image2.filename == '':
            return jsonify({
                'success': False, 
                'error': 'No files selected.'
            }), 400

        # Validate file types
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in image1.filename and 
                image1.filename.rsplit('.', 1)[1].lower() in allowed_extensions and
                '.' in image2.filename and 
                image2.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'success': False, 
                'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP'
            }), 400

        # Process images
        result = blend_images(image1, image2, blend_level)
        
        # Generate color histograms
        histograms = generate_color_histograms(image1, image2, result['blended_image'])

        return jsonify({
            'success': True,
            'blended_image': result['blended_b64'],
            'histogram1': histograms['histogram1'],
            'histogram2': histograms['histogram2'],
            'histogram_blended': histograms['histogram_blended']
        })

    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Processing error: {str(e)}'
        }), 500

@app.route('/api/blend', methods=['POST'])
def api_blend():
    """API endpoint for simple blending (no CAPTCHA)"""
    try:
        # Get blend level
        blend_level = float(request.form.get('blend_level', 0.5))
        if not 0 <= blend_level <= 1:
            return jsonify({'success': False, 'error': 'Invalid blend level'}), 400

        # Check files
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'success': False, 'error': 'Missing image files'}), 400

        image1 = request.files['image1']
        image2 = request.files['image2']

        if image1.filename == '' or image2.filename == '':
            return jsonify({'success': False, 'error': 'No files selected'}), 400

        # Process blending
        result = blend_images(image1, image2, blend_level)
        
        return jsonify({
            'success': True,
            'blended_image': result['blended_b64']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/new-captcha')
def new_captcha():
    """Generate new CAPTCHA"""
    captcha_text, captcha_image = generate_captcha()
    session['captcha_text'] = captcha_text
    
    buffered = io.BytesIO()
    captcha_image.save(buffered, format="PNG")
    captcha_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'captcha_image': captcha_b64})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
