from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import random
import string
from PIL import ImageDraw, ImageFont

def resize_images(image1, image2):
    """Изменение размера изображений до одинакового"""
    img1 = Image.open(image1).convert('RGB')
    img2 = Image.open(image2).convert('RGB')
    
    size1 = img1.size
    size2 = img2.size
    
    # Используем минимальные размеры
    new_size = (min(size1[0], size2[0]), min(size1[1], size2[1]))
    
    img1_resized = img1.resize(new_size, Image.Resampling.LANCZOS)
    img2_resized = img2.resize(new_size, Image.Resampling.LANCZOS)
    
    return img1_resized, img2_resized

def blend_images(image1_file, image2_file, blend_level):
    """Смешивание двух изображений"""
    image1_file.seek(0)
    image2_file.seek(0)
    
    image1, image2 = resize_images(image1_file, image2_file)
    
    # Конвертация в numpy arrays
    arr1 = np.array(image1, dtype=np.float32)
    arr2 = np.array(image2, dtype=np.float32)
    
    # Смешивание
    blended_arr = arr1 * blend_level + arr2 * (1 - blend_level)
    blended_arr = np.clip(blended_arr, 0, 255).astype(np.uint8)
    
    # Обратно в PIL Image
    blended_image = Image.fromarray(blended_arr)
    
    # Конвертация в base64
    buffered = io.BytesIO()
    blended_image.save(buffered, format="PNG")
    blended_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        'blended_image': blended_image,
        'blended_b64': blended_b64
    }

def generate_color_histograms(image1_file, image2_file, blended_image):
    """Генерация RGB гистограмм"""
    def create_histogram(image, title):
        plt.figure(figsize=(8, 3))
        
        if isinstance(image, Image.Image):
            arr = np.array(image)
        else:
            image.seek(0)
            arr = np.array(Image.open(image).convert('RGB'))
        
        colors = ['red', 'green', 'blue']
        for i, color in enumerate(colors):
            plt.hist(arr[:,:,i].ravel(), bins=50, color=color, alpha=0.7, 
                    label=color.upper(), density=True)
        
        plt.title(title)
        plt.xlabel('Pixel Value')
        plt.ylabel('Density')
        plt.legend()
        plt.tight_layout()
        
        # Конвертация в base64
        buf = io.BytesIO()
        plt.savefig(buf, format='PNG', dpi=80)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        
        return img_b64
    
    image1_file.seek(0)
    image2_file.seek(0)
    
    histogram1 = create_histogram(image1_file, 'Image 1 - Color Distribution')
    histogram2 = create_histogram(image2_file, 'Image 2 - Color Distribution')
    histogram_blended = create_histogram(blended_image, 'Blended Image - Color Distribution')
    
    return {
        'histogram1': histogram1,
        'histogram2': histogram2,
        'histogram_blended': histogram_blended
    }

def generate_captcha(length=6):
    """Генерация CAPTCHA"""
    # Создание изображения
    width, height = 200, 80
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Генерация текста
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    # Попытка использования шрифта
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Добавление шума
    for _ in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='gray', width=1)
    
    # Рисование текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    for i, char in enumerate(text):
        char_x = x + i * (text_width / len(text))
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        draw.text((char_x + offset_x, y + offset_y), char, fill='black', font=font)
    
    return text, image

def verify_captcha(user_input, captcha_text):
    """Проверка CAPTCHA"""
    return user_input.upper() == captcha_text.upper()
