import requests
import cv2
import numpy as np
import json

def test_denoising_service():
    """
    Тестирует сервис устранения шума
    """
    url = "http://localhost:5000/upload"
    
    # Создаем тестовое изображение
    test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    
    # Добавляем шум
    noise = np.random.normal(0, 25, test_image.shape).astype(np.uint8)
    noisy_image = cv2.add(test_image, noise)
    
    # Сохраняем для отправки
    cv2.imwrite('test_noisy.png', noisy_image)
    
    # Отправляем запрос
    files = {'file': open('test_noisy.png', 'rb')}
    data = {
        'method': 'gaussian',
        'strength': '7'
    }
    
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("Успешная обработка!")
        print(f"Метод: {result['method']}")
        print(f"Сила фильтра: {result['strength']}")
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    test_denoising_service()
