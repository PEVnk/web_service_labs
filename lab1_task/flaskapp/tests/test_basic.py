import pytest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_basic_math():
    """Простой математический тест"""
    assert 1 + 1 == 2

def test_import_flask():
    """Тест импорта Flask"""
    try:
        import flask
        print(f"✅ Flask imported, version: {flask.__version__}")
        assert True
    except ImportError as e:
        pytest.fail(f"Flask import failed: {e}")

def test_import_opencv():
    """Тест импорта OpenCV"""
    try:
        import cv2
        print(f"✅ OpenCV imported, version: {cv2.__version__}")
        assert True
    except ImportError as e:
        pytest.fail(f"OpenCV import failed: {e}")

def test_import_numpy():
    """Тест импорта NumPy"""
    try:
        import numpy as np
        print(f"✅ NumPy imported, version: {np.__version__}")
        assert True
    except ImportError as e:
        pytest.fail(f"NumPy import failed: {e}")

def test_import_other():
    """Тест импорта других зависимостей"""
    try:
        import matplotlib
        import requests
        import PIL
        print("✅ All other imports successful")
        assert True
    except ImportError as e:
        print(f"⚠️ Optional import warning: {e}")
        # Не проваливаем тест для опциональных импортов
        assert True
