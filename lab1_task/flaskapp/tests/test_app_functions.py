import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_blend_images_function():
    """Тест функции смешивания изображений"""
    try:
        from some_app import blend_images
        
        # Создаем тестовые изображения
        img1 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Тестируем смешивание
        blended = blend_images(img1, img2, 0.5)
        
        # Проверяем результат
        assert blended.shape == (100, 100, 3)
        assert blended.dtype == np.uint8
        print("✅ blend_images function works")
        
    except Exception as e:
        pytest.fail(f"blend_images test failed: {e}")

def test_flask_app_exists():
    """Тест что Flask приложение существует"""
    try:
        from some_app import app
        assert app is not None
        assert hasattr(app, 'route')
        print("✅ Flask app exists and has routes")
    except Exception as e:
        pytest.fail(f"Flask app test failed: {e}")
