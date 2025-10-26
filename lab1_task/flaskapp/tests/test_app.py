import pytest
import sys
import os
import numpy as np

# Обновите путь импорта
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
    # Создаем тестовые изображения
    img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255  # Белое изображение
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)       # Черное изображение
    
    # Тестируем смешивание
    blended = blend_images(img1, img2, 0.5)
    
    assert blended.shape == (100, 100, 3)
    assert blended.dtype == np.uint8
    
    # Проверяем, что смешивание работает
    expected_value = 127  # Среднее между 0 и 255
    assert np.abs(blended[0, 0, 0] - expected_value) <= 1

def test_color_distribution_function():
    """Тест функции генерации графиков"""
    # Создаем тестовое изображение
    test_image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    
    # Генерируем график
    chart_data = generate_color_distribution(test_image, "Test Chart")
    
    # Проверяем, что возвращается base64 строка
    assert isinstance(chart_data, str)
    assert len(chart_data) > 1000  # График должен быть достаточно большим

def test_invalid_blend_alpha(client):
    """Тест обработки неверного параметра смешивания"""
    response = client.post('/blend', data={
        'blend_alpha': 'invalid'
    })
    assert response.status_code == 400
    assert b'Invalid blend value' in response.data

def test_missing_files(client):
    """Тест обработки отсутствующих файлов"""
    response = client.post('/blend')
    assert response.status_code == 400
    assert b'upload both images' in response.data
