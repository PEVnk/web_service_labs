from flask import Flask, render_template, request, jsonify, session
import os
import io
import base64
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Импортируем функции из net.py
from net import blend_images, generate_color_histograms, generate_captcha, verify_captcha

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route('/')
def index():
    """Главная страница с простой формой"""
    return render_template('simple.html')

@app.route('/advanced')
def advanced():
    """Страница с расширенными функциями и гистограммами"""
    captcha_text, captcha_image = generate_captcha()
    session['captcha_text'] = captcha_text
    
    buffered = io.BytesIO()
    captcha_image.save(buffered, format="PNG")
    captcha_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('net.html', captcha_image=captcha_b64)

@app.route('/process', methods=['POST'])
def process_images():
    """Обработка смешивания изображений"""
    try:
        # Проверка CAPTCHA
        user_captcha = request.form.get('captcha', '').strip()
        if not verify_captcha(user_captcha, session.get('captcha_text')):
            return jsonify({'success': False, 'error': 'Invalid CAPTCHA'}), 400

        # Получение уровня смешивания
        try:
            blend_level = float(request.form.get('blend_level', 0.5))
            if not 0 <= blend_level <= 1:
                raise ValueError("Blend level must be between 0 and 1")
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid blend level'}), 400

        # Проверка файлов
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'success': False, 'error': 'Please upload both images'}), 400

        image1 = request.files['image1']
        image2 = request.files['image2']

        if image1.filename == '' or image2.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Обработка изображений
        result = blend_images(image1, image2, blend_level)
        
        # Генерация гистограмм
        histograms = generate_color_histograms(image1, image2, result['blended_image'])

        return jsonify({
            'success': True,
            'blended_image': result['blended_b64'],
            'histogram1': histograms['histogram1'],
            'histogram2': histograms['histogram2'],
            'histogram_blended': histograms['histogram_blended']
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Processing error: {str(e)}'}), 500

@app.route('/new-captcha')
def new_captcha():
    """Генерация новой CAPTCHA"""
    captcha_text, captcha_image = generate_captcha()
    session['captcha_text'] = captcha_text
    
    buffered = io.BytesIO()
    captcha_image.save(buffered, format="PNG")
    captcha_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'captcha_image': captcha_b64})

@app.route('/api/blend', methods=['POST'])
def api_blend():
    """API endpoint для смешивания изображений"""
    try:
        blend_level = float(request.form.get('blend_level', 0.5))
        image1 = request.files['image1']
        image2 = request.files['image2']
        
        result = blend_images(image1, image2, blend_level)
        
        return jsonify({
            'success': True,
            'blended_image': result['blended_b64']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
