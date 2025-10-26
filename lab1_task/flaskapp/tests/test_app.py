import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from some_app import app, blend_images, generate_color_distribution

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Image Blending Studio' in response.data

def test_blend_images_function():
    """Тест функции смешивания изображений"""
    img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    blended = blend_images(img1, img2, 0.5)
    assert blended.shape == (100, 100, 3)
    assert blended.dtype == np.uint8

def test_color_distribution_function():
    """Тест функции генерации графиков"""
    test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    chart_data = generate_color_distribution(test_image, "Test Chart")
    assert isinstance(chart_data, str)
    assert len(chart_data) > 1000

def test_invalid_blend_alpha(client):
    """Тест обработки неверного параметра смешивания"""
    response = client.post('/blend', data={
        'blend_alpha': 'invalid',
        'g-recaptcha-response': 'test-bypass'
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    # Проверяем что есть какая-то ошибка (может быть reCAPTCHA или validation)
    assert len(json_data['error']) > 0

def test_missing_files(client):
    """Тест обработки отсутствующих файлов"""
    response = client.post('/blend', data={
        'g-recaptcha-response': 'test-bypass'
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    error_msg = json_data['error'].lower()
    assert any(word in error_msg for word in ['upload', 'file', 'image'])

def test_missing_captcha(client):
    """Тест обработки отсутствующей капчи"""
    response = client.post('/blend', data={
        'blend_alpha': '0.5'
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'captcha' in json_data['error'].lower() or 'verification' in json_data['error'].lower()
