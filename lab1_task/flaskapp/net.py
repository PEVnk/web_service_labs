import cv2
import numpy as np

def advanced_blending(image1, image2, alpha, method='linear'):
    """
    Продвинутые методы смешивания изображений
    """
    h1, w1 = image1.shape[:2]
    h2, w2 = image2.shape[:2]
    h = min(h1, h2)
    w = min(w1, w2)
    
    img1_resized = cv2.resize(image1, (w, h))
    img2_resized = cv2.resize(image2, (w, h))
    
    if method == 'linear':
        return cv2.addWeighted(img1_resized, alpha, img2_resized, 1 - alpha, 0)
    elif method == 'multiply':
        blended = img1_resized.astype(np.float32) * img2_resized.astype(np.float32) / 255.0
        return cv2.addWeighted(img1_resized, alpha, blended.astype(np.uint8), 1 - alpha, 0)
    elif method == 'screen':
        blended = 255 - (255 - img1_resized.astype(np.float32)) * (255 - img2_resized.astype(np.float32)) / 255.0
        return cv2.addWeighted(img1_resized, alpha, blended.astype(np.uint8), 1 - alpha, 0)
    
    return img1_resized
