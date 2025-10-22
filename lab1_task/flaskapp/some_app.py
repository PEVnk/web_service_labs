from flask import Flask, render_template, request, send_file, jsonify
import cv2
import numpy as np
import os
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Создаем папку для загрузок если её нет
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def apply_denoising(image, method='gaussian', strength=5):
    """
    Применяет различные методы устранения шума
    """
    if method == 'gaussian':
        # Гауссовское размытие
        kernel_size = max(3, 2 * (strength // 2) + 1)
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    elif method == 'median':
        # Медианный фильтр
        kernel_size = max(3, 2 * (strength // 2) + 1)
        return cv2.medianBlur(image, kernel_size)
    
    elif method == 'bilateral':
        # Билатеральный фильтр
        return cv2.bilateralFilter(image, 9, strength * 10, strength * 10)
    
    elif method == 'nlmeans':
        # Non-local means denoising
        return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
    
    return image

def generate_color_distribution(image):
    """
    Генерирует график распределения цветов
    """
    plt.figure(figsize=(10, 6))
    
    if len(image.shape) == 3:  # Цветное изображение
        colors = ('b', 'g', 'r')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            plt.plot(hist, color=color, label=f'Channel {color}')
    else:  # Черно-белое изображение
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        plt.plot(hist, color='gray', label='Grayscale')
    
    plt.title('Color Distribution')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Сохраняем в буфер
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def generate_noise_distribution(original, denoised):
    """
    Генерирует график распределения шума
    """
    noise = original.astype(np.float32) - denoised.astype(np.float32)
    
    plt.figure(figsize=(10, 6))
    
    if len(noise.shape) == 3:
        colors = ('b', 'g', 'r')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([noise.astype(np.uint8)], [i], None, [256], [-128, 128])
            plt.plot(hist, color=color, label=f'Noise channel {color}')
    else:
        hist = cv2.calcHist([noise.astype(np.uint8)], [0], None, [256], [-128, 128])
        plt.plot(hist, color='black', label='Noise distribution')
    
    plt.title('Noise Distribution')
    plt.xlabel('Noise Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Сохраняем в буфер
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/advanced')
def advanced():
    return render_template('net.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Читаем изображение
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if image is None:
        return jsonify({'error': 'Invalid image file'}), 400
    
    # Получаем параметры
    method = request.form.get('method', 'gaussian')
    try:
        strength = int(request.form.get('strength', 5))
    except:
        strength = 5
    
    # Применяем фильтрацию
    denoised_image = apply_denoising(image, method, strength)
    
    # Конвертируем обратно в bytes
    _, buffer = cv2.imencode('.png', denoised_image)
    processed_bytes = base64.b64encode(buffer).decode('utf-8')
    
    # Генерируем графики
    color_dist = generate_color_distribution(image)
    noise_dist = generate_noise_distribution(image, denoised_image)
    
    # Оригинальное изображение в base64
    _, orig_buffer = cv2.imencode('.png', image)
    original_bytes = base64.b64encode(orig_buffer).decode('utf-8')
    
    return jsonify({
        'original': f"data:image/png;base64,{original_bytes}",
        'processed': f"data:image/png;base64,{processed_bytes}",
        'color_distribution': f"data:image/png;base64,{color_dist}",
        'noise_distribution': f"data:image/png;base64,{noise_dist}",
        'method': method,
        'strength': strength
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
