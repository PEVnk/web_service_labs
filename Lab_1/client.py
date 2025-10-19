import requests
import base64
from PIL import Image
import io

def test_blend_api():
    """Тестирование API смешивания изображений"""
    
    # Создание тестовых изображений
    def create_test_image(color, size=(100, 100)):
        img = Image.new('RGB', size, color=color)
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io
    
    # URL API
    url = "http://localhost:5000/api/blend"
    
    # Подготовка данных
    files = {
        'image1': ('red.jpg', create_test_image('red'), 'image/jpeg'),
        'image2': ('blue.jpg', create_test_image('blue'), 'image/jpeg')
    }
    
    data = {
        'blend_level': '0.5'
    }
    
    try:
        # Отправка запроса
        response = requests.post(url, files=files, data=data)
        result = response.json()
        
        if result['success']:
            # Декодирование и сохранение результата
            image_data = base64.b64decode(result['blended_image'])
            image = Image.open(io.BytesIO(image_data))
            image.save('blended_result.png')
            print("Success! Result saved as 'blended_result.png'")
        else:
            print("Error:", result['error'])
            
    except Exception as e:
        print("Request failed:", e)

if __name__ == '__main__':
    test_blend_api()
