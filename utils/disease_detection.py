import cv2
import numpy as np
from PIL import Image
import io
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Define common crop diseases and their descriptions
DISEASE_CLASSES = {
    0: {"name": "Healthy", "description": "No disease detected", "severity": "None"},
    1: {"name": "Leaf Blight", "description": "Fungal infection causing brown lesions", "severity": "High"},
    2: {"name": "Leaf Spot", "description": "Small, circular spots on leaves", "severity": "Medium"},
    3: {"name": "Rust", "description": "Orange-brown pustules on leaves", "severity": "Medium"},
}

class DiseaseDetector:
    def __init__(self):
        """Initialize the disease detector with a simple model"""
        self.scaler = StandardScaler()
        self.model = self._create_simple_model()
        self.target_size = (224, 224)

    def _create_simple_model(self):
        """Create a simple random forest model for disease detection"""
        return RandomForestClassifier(n_estimators=100, random_state=42)

    def _extract_features(self, img_array):
        """Extract color and texture features from the image"""
        # Color features
        mean_colors = np.mean(img_array, axis=(0,1))
        std_colors = np.std(img_array, axis=(0,1))

        # Texture features using grayscale image
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        glcm = cv2.resize(gray, (32, 32))  # Simplified texture analysis
        features = np.concatenate([
            mean_colors, std_colors, 
            glcm.mean(axis=1)  # Simple texture features
        ])
        return features.reshape(1, -1)

    def preprocess_image(self, image_data):
        """Preprocess the image for feature extraction"""
        if isinstance(image_data, bytes):
            img = Image.open(io.BytesIO(image_data))
        else:
            img = Image.open(image_data)

        img = img.convert('RGB')
        img = img.resize(self.target_size)
        img_array = np.array(img)
        return img_array

    def detect_disease(self, image_data):
        """Detect disease in the given image"""
        try:
            # Preprocess the image
            img_array = self.preprocess_image(image_data)

            # Extract features
            features = self._extract_features(img_array)

            # Simple anomaly detection based on color distributions
            if features[0, :3].mean() > 0.7:  # If average color is too bright
                predicted_class = 0  # Healthy
            else:
                # Simplified logic based on color features
                green_content = features[0, 1] / features[0, :3].sum()
                if green_content < 0.3:
                    predicted_class = 3  # Rust
                elif features[0, 0] > features[0, 1]:
                    predicted_class = 1  # Leaf Blight
                elif features[0, 2] > features[0, 1]:
                    predicted_class = 2  # Leaf Spot
                else:
                    predicted_class = 0  # Healthy

            # Get disease details
            disease_info = DISEASE_CLASSES[predicted_class].copy()
            confidence = 0.7 + (0.2 * green_content)  # Simplified confidence score
            disease_info['confidence'] = f"{confidence * 100:.1f}%"

            return {
                'success': True,
                'disease_info': disease_info,
                'recommendations': self._get_recommendations(predicted_class)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _get_recommendations(self, disease_class):
        """Get treatment recommendations based on detected disease"""
        recommendations = {
            0: [
                "Continue regular monitoring",
                "Maintain current agricultural practices",
                "Regular watering and fertilization"
            ],
            1: [
                "Apply appropriate fungicide",
                "Improve air circulation",
                "Remove infected leaves",
                "Reduce overhead watering"
            ],
            2: [
                "Apply copper-based fungicide",
                "Maintain proper plant spacing",
                "Avoid water splashing on leaves"
            ],
            3: [
                "Apply rust-specific fungicide",
                "Remove infected plant debris",
                "Improve air circulation",
                "Consider resistant varieties for next season"
            ]
        }
        return recommendations.get(disease_class, ["Consult with an agricultural expert"])