import cv2
import numpy as np

def advanced_denoising(image, method='deep_learning_simulated'):
    """
    Продвинутые методы устранения шума (симуляция нейросетевых подходов)
    """
    if method == 'deep_learning_simulated':
        # Симуляция нейросетевого подхода с помощью комбинации фильтров
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        denoised = cv2.bilateralFilter(denoised, 9, 75, 75)
        return denoised
    
    elif method == 'wavelet_simulated':
        # Симуляция вейвлет-преобразования
        denoised = cv2.medianBlur(image, 5)
        denoised = cv2.GaussianBlur(denoised, (3, 3), 0)
        return denoised
    
    return image

def add_test_noise(image, noise_level=25):
    """
    Добавляет тестовый шум для демонстрации
    """
    row, col, ch = image.shape
    mean = 0
    sigma = noise_level
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    noisy = image + gauss
    return np.clip(noisy, 0, 255).astype(np.uint8)
