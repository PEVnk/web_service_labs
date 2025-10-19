from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import random
import string

def resize_images(image1, image2):
    """Resize images to match dimensions"""
    # Reset file pointers
    if hasattr(image1, 'seek'):
        image1.seek(0)
    if hasattr(image2, 'seek'):
        image2.seek(0)
        
    img1 = Image.open(image1).convert('RGB')
    img2 = Image.open(image2).convert('RGB')
    
    # Get dimensions
    width1, height1 = img1.size
    width2, height2 = img2.size
    
    # Use smallest dimensions
    new_width = min(width1, width2)
    new_height = min(height1, height2)
    
    # Resize images
    img1_resized = img1.resize((new_width, new_height), Image.Resampling.LANCZOS)
    img2_resized = img2.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img1_resized, img2_resized

def blend_images(image1_file, image2_file, blend_level):
    """Blend two images with given blend level"""
    # Reset streams
    if hasattr(image1_file, 'seek'):
        image1_file.seek(0)
    if hasattr(image2_file, 'seek'):
        image2_file.seek(0)
    
    # Resize images to same dimensions
    image1, image2 = resize_images(image1_file, image2_file)
    
    # Convert to numpy arrays
    arr1 = np.array(image1, dtype=np.float32)
    arr2 = np.array(image2, dtype=np.float32)
    
    # Blend images
    blended_arr = arr1 * blend_level + arr2 * (1 - blend_level)
    blended_arr = np.clip(blended_arr, 0, 255).astype(np.uint8)
    
    # Convert back to PIL Image
    blended_image = Image.fromarray(blended_arr)
    
    # Convert to base64 for web display
    buffered = io.BytesIO()
    blended_image.save(buffered, format="PNG")
    blended_b64 = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        'blended_image': blended_image,
        'blended_b64': blended_b64
    }

def generate_color_histograms(image1_file, image2_file, blended_image):
    """Generate RGB color distribution histograms"""
    def create_histogram(image, title):
        plt.figure(figsize=(10, 4))
        
        if isinstance(image, Image.Image):
            arr = np.array(image)
        else:
            if hasattr(image, 'seek'):
                image.seek(0)
            arr = np.array(Image.open(image).convert('RGB'))
        
        # Plot RGB histograms
        colors = ['red', 'green', 'blue']
        color_labels = ['Red', 'Green', 'Blue']
        
        for i, (color, label) in enumerate(zip(colors, color_labels)):
            plt.hist(arr[:,:,i].ravel(), bins=64, color=color, alpha=0.7, 
                    label=label, density=True, histtype='stepfilled')
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Pixel Intensity', fontsize=12)
        plt.ylabel('Density', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='PNG', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        
        return img_b64
    
    # Reset streams
    if hasattr(image1_file, 'seek'):
        image1_file.seek(0)
    if hasattr(image2_file, 'seek'):
        image2_file.seek(0)
    
    # Create histograms
    histogram1 = create_histogram(image1_file, 'Image 1 - Color Distribution')
    histogram2 = create_histogram(image2_file, 'Image 2 - Color Distribution')
    histogram_blended = create_histogram(blended_image, 'Blended Image - Color Distribution')
    
    return {
        'histogram1': histogram1,
        'histogram2': histogram2,
        'histogram_blended': histogram_blended
    }

def generate_captcha(length=6):
    """Generate random CAPTCHA text and image"""
    # Image dimensions
    width, height = 200, 80
    
    # Create image with light background
    image = Image.new('RGB', (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(image)
    
    # Generate random text
    characters = string.ascii_uppercase + string.digits
    text = ''.join(random.choice(characters) for _ in range(length))
    
    # Try to load font
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
    
    # Add noise - random lines
    for _ in range(6):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(180, 180, 180), width=1)
    
    # Add noise - random dots
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(200, 200, 200))
    
    # Calculate text position
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width = len(text) * 20
        text_height = 36
    
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Draw text with distortion
    for i, char in enumerate(text):
        char_x = x + i * (text_width / len(text))
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        draw.text((char_x + offset_x, y + offset_y), char, 
                 fill=(0, 0, 0), font=font)
    
    return text, image

def verify_captcha(user_input, captcha_text):
    """Verify CAPTCHA input (case insensitive)"""
    if not user_input or not captcha_text:
        return False
    return user_input.upper() == captcha_text.upper()
