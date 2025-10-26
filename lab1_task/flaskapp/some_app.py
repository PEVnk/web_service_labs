from flask import Flask, render_template, request, jsonify, session
import cv2
import numpy as np
import os
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import requests
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'your-secret-key-here'

#Конфигурация Google reCAPTCHA
RECAPTCHA_SECRET_KEY = '6LfGz_crAAAAAJ5mt6R7loNfaw9BUdllgpaAKxJC'  
RECAPTCHA_SITE_KEY = '6LfGz_crAAAAANTE_nHwuDF5NLIHNJ0wJHlVZqbH'  


def verify_recaptcha(recaptcha_response):
    """
    Проверяет Google reCAPTCHA ответ с отладкой
    """
    if not recaptcha_response:
        print("❌ reCAPTCHA: No response received")
        return False
        
    data = {
        'secret': RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    
    try:
        print(f"🔍 reCAPTCHA: Sending verification request...")
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            timeout=10
        )
        result = response.json()
        print(f"🔍 reCAPTCHA Response: {result}")
        
        success = result.get('success', False)
        if not success:
            print(f"❌ reCAPTCHA failed. Errors: {result.get('error-codes', [])}")
        
        return success
        
    except requests.RequestException as e:
        print(f"❌ reCAPTCHA network error: {e}")
        return False

def blend_images(image1, image2, alpha):
    """
    Смешивает два изображения с заданным коэффициентом
    """
    # Приводим изображения к одному размеру
    h1, w1 = image1.shape[:2]
    h2, w2 = image2.shape[:2]
    
    # Используем минимальные размеры
    h = min(h1, h2)
    w = min(w1, w2)
    
    # Изменяем размер изображений
    img1_resized = cv2.resize(image1, (w, h))
    img2_resized = cv2.resize(image2, (w, h))
    
    # Смешиваем изображения
    blended = cv2.addWeighted(img1_resized, alpha, img2_resized, 1 - alpha, 0)
    return blended

def generate_color_distribution(image, title="Color Distribution"):
    """
    Генерирует график распределения цветов
    """
    plt.figure(figsize=(10, 6))
    
    if len(image.shape) == 3:  # Цветное изображение
        colors = ('b', 'g', 'r')
        channel_names = ('Blue', 'Green', 'Red')
        for i, (color, name) in enumerate(zip(colors, channel_names)):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            plt.plot(hist, color=color, label=f'{name} Channel', alpha=0.7)
    else:  # Черно-белое изображение
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        plt.plot(hist, color='gray', label='Grayscale', alpha=0.7)
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Сохраняем в буфер
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

@app.route('/')
def index():
    return render_template('simple.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)

@app.route('/advanced')
def advanced():
    return render_template('net.html', recaptcha_site_key=RECAPTCHA_SITE_KEY)

@app.route('/blend', methods=['POST'])
def blend_images_route():
    # Отладочная информация
    print(f"reCAPTCHA response received: {bool(request.form.get('g-recaptcha-response'))}")
    
    recaptcha_response = request.form.get('g-recaptcha-response')
    
    # === ПРОВЕРКА reCAPTCHA ===
    recaptcha_response = request.form.get('g-recaptcha-response')
    
    if not recaptcha_response:
        return jsonify({
            'success': False,
            'error': 'Please complete the reCAPTCHA verification.'
        }), 400
    
    if not verify_recaptcha(recaptcha_response):
        return jsonify({
            'success': False,
            'error': 'reCAPTCHA verification failed. Please try again.'
        }), 400
        
    # Проверяем файлы
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Please upload both images.'
        }), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        return jsonify({
            'success': False,
            'error': 'Please select both images.'
        }), 400
    
    try:
        # Получаем параметр смешивания
        blend_alpha = float(request.form.get('blend_alpha', 0.5))
        blend_alpha = max(0.0, min(1.0, blend_alpha))  # Ограничиваем от 0 до 1
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid blend value. Please use a number between 0 and 1.'
        }), 400
    
    try:
        # Читаем изображения
        file1_bytes = np.frombuffer(file1.read(), np.uint8)
        file2_bytes = np.frombuffer(file2.read(), np.uint8)
        
        image1 = cv2.imdecode(file1_bytes, cv2.IMREAD_COLOR)
        image2 = cv2.imdecode(file2_bytes, cv2.IMREAD_COLOR)
        
        if image1 is None or image2 is None:
            return jsonify({
                'success': False,
                'error': 'Invalid image files. Please upload valid images.'
            }), 400
        
        # Смешиваем изображения
        blended_image = blend_images(image1, image2, blend_alpha)
        
        # Конвертируем изображения в base64
        def image_to_base64(img):
            _, buffer = cv2.imencode('.png', img)
            return base64.b64encode(buffer).decode('utf-8')
        
        original1_base64 = image_to_base64(image1)
        original2_base64 = image_to_base64(image2)
        blended_base64 = image_to_base64(blended_image)
        
        # Генерируем графики распределения цветов
        color_dist1 = generate_color_distribution(image1, "Image 1 Color Distribution")
        color_dist2 = generate_color_distribution(image2, "Image 2 Color Distribution")
        color_dist_blended = generate_color_distribution(blended_image, "Blended Image Color Distribution")
        
        return jsonify({
            'success': True,
            'images': {
                'original1': f"data:image/png;base64,{original1_base64}",
                'original2': f"data:image/png;base64,{original2_base64}",
                'blended': f"data:image/png;base64,{blended_base64}"
            },
            'charts': {
                'color_dist1': f"data:image/png;base64,{color_dist1}",
                'color_dist2': f"data:image/png;base64,{color_dist2}",
                'color_dist_blended': f"data:image/png;base64,{color_dist_blended}"
            },
            'blend_alpha': blend_alpha
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing images: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
