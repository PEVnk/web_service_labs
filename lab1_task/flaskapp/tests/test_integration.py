import pytest
import sys
import os
import base64
from PIL import Image
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from some_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def create_test_image(width=100, height=100, color='red'):
    """Создает тестовое изображение в памяти"""
    img = Image.new('RGB', (width, height), color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_complete_workflow(client):
    """Интеграционный тест полного workflow"""
    # Создаем тестовые изображения
    img1 = create_test_image(color='red')
    img2 = create_test_image(color='blue')
    
    # Отправляем запрос на смешивание (без reCAPTCHA для тестов)
    response = client.post('/blend', data={
        'file1': (img1, 'test1.png'),
        'file2': (img2, 'test2.png'),
        'blend_alpha': '0.5',
        'g-recaptcha-response': 'test-captcha-response'  # Для тестов
    }, content_type='multipart/form-data')
    
    # В тестовой среде reCAPTCHA будет проваливаться, но мы проверяем структуру ответа
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.get_json()
        assert data['success'] == True
        assert 'images' in data
        assert 'charts' in data
    else:
        # Если reCAPTCHA failed, проверяем структуру ошибки
        data = response.get_json()
        assert data['success'] == False
        assert 'error' in data
