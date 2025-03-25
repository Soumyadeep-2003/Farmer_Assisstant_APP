import cv2
import numpy as np
from PIL import Image
import io
from utils.disease_detection import DiseaseDetector

# Initialize disease detector
disease_detector = DiseaseDetector()

def analyze_crop_image(uploaded_file):
    """
    Analyze uploaded crop image for health indicators and diseases
    """
    # Convert uploaded file to opencv format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Reset file pointer for disease detection
    uploaded_file.seek(0)

    # Perform disease detection
    disease_results = disease_detector.detect_disease(uploaded_file)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define green color range
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    # Create mask for green pixels
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Calculate green ratio
    total_pixels = img.shape[0] * img.shape[1]
    green_pixels = cv2.countNonZero(green_mask)
    green_ratio = green_pixels / total_pixels

    # Estimate NIR (Near-infrared) using red channel
    red_channel = img[:,:,2]
    nir_estimate = np.mean(red_channel) / 255.0

    return {
        'green_ratio': green_ratio,
        'nir_estimate': nir_estimate,
        'disease_detection': disease_results
    }

def calculate_ndvi(green_ratio, nir_estimate):
    """
    Calculate a simplified NDVI-like score
    """
    # Simplified NDVI calculation
    ndvi = (nir_estimate - (1 - green_ratio)) / (nir_estimate + (1 - green_ratio))

    # Normalize to 0-1 range
    ndvi = (ndvi + 1) / 2

    return ndvi