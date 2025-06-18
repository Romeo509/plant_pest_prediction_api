# Maize Disease Classifier API

An API built with FastAPI and TensorFlow for classifying maize leaf diseases from images.

## Features

- Upload an image of a maize leaf.
- Predicts the presence of one of the following diseases:
  - Cercospora leaf spot / Gray leaf spot
  - Common rust
  - Northern Leaf Blight
  - Healthy
- Returns prediction, confidence score, and class probabilities.

## Requirements

- Python 3.8+
- TensorFlow
- FastAPI
- Uvicorn
- Pillow
- NumPy

## run the api server
```
uvicorn main:app --reload
```

## API Endpoints
*example using curl

```
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path_to_image.jpg;type=image/jpeg'

```
*sample response
```
{
  "prediction": "healthy",
  "confidence": 0.9999,
  "probabilities": {
    "Cercospora_leaf_spot Gray_leaf_spot": 0.0000054,
    "Common_rust": 0.0000782,
    "Northern_Leaf_Blight": 0.0000086,
    "healthy": 0.9999077
  }
}
```
