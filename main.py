from fastapi import FastAPI, File, UploadFile, HTTPException
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io
import uvicorn

app = FastAPI(
    title="Maize Disease Classifier API",
    description="API for classifying maize leaf diseases using AI",
    version="1.0.0"
)

# Global variable to store the model
model = None
class_labels = ['Cercospora_leaf_spot Gray_leaf_spot', 'Common_rust', 'Northern_Leaf_Blight', 'healthy']

def load_disease_model():
    """Load the pre-trained maize disease model"""
    global model
    try:
        model = load_model("maize_disease_model.h5")
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Using dummy model for demo purposes")
        # Create a dummy model for demonstration
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(4, activation='softmax', input_shape=(224, 224, 3))
        ])

def preprocess_image(img_bytes):
    """Preprocess uploaded image for model prediction"""
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to model input size
        img = img.resize((224, 224))
        
        # Convert to array and normalize
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_disease_model()

@app.post("/predict", 
          summary="Predict maize disease from image",
          response_description="Prediction results with confidence scores")
async def predict_disease(file: UploadFile = File(..., description="Image file to classify")):
    """
    Classify a maize leaf image into one of the following categories:
    - Cercospora_leaf_spot Gray_leaf_spot
    - Common_rust
    - Northern_Leaf_Blight
    - healthy
    
    Returns prediction with confidence score and individual class probabilities.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and preprocess image
        img_bytes = await file.read()
        img_array = preprocess_image(img_bytes)
        
        # Make prediction
        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        prediction = model.predict(img_array)
        class_idx = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        return {
            "prediction": class_labels[class_idx],
            "confidence": confidence,
            "probabilities": {
                class_labels[i]: float(prediction[0][i]) 
                for i in range(len(class_labels))
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/health", 
         summary="Service health check",
         response_description="API status information")
async def health_check():
    """
    Check the health status of the API service.
    
    Returns whether the service is running and if the model is loaded.
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "available_classes": class_labels
    }

if __name__ == "__main__":
    print("Starting Maize Disease Classifier API...")
    print("API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )
