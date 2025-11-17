# AgriCom Pest Prediction Project

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Web Application (Recommended)

Start the FastAPI web server:

```bash
python -m uvicorn app:app --reload
```

Then open your browser and navigate to:
```
http://127.0.0.1:8000
```

You can upload an image through the web interface and get predictions.

### Option 2: Command Line Script

Run the standalone script to predict maize diseases from images:

```bash
python maize_disease_predictor.py
```

## How It Works

The program uses an AI model to analyze maize leaf images and predict potential diseases. The model evaluates the image and generates confidence scores for seven different diseases. The system then identifies the disease with the highest probability score and displays it as the final prediction along with its confidence percentage.

## Sample Output

```
{'disease': 'common_rust', 'confidence': 0.9952038526535034, 'all_probs': {'common_rust': 0.9952038526535034, 'gray_leaf_spot': 0.0030148974619805813, 'healthy': 2.7720963771571405e-05, 'maize_ear_rot': 4.144687773077749e-05, 'maize_fall_armyworm': 0.00035858937189914286, 'maize_stem_borer': 6.461035081883892e-05, 'northern_leaf_blight': 0.0012887364719063044}}
🎯 Final Prediction: common_rust (99.52%)
```

## API Endpoints

### POST /api/predict

Upload an image file to predict maize disease.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image file)

**Response:**
```json
{
  "disease": "common_rust",
  "confidence": 0.9952038526535034,
  "all_probs": {
    "common_rust": 0.9952038526535034,
    "gray_leaf_spot": 0.0030148974619805813,
    "healthy": 2.7720963771571405e-05,
    "maize_ear_rot": 4.144687773077749e-05,
    "maize_fall_armyworm": 0.00035858937189914286,
    "maize_stem_borer": 6.461035081883892e-05,
    "northern_leaf_blight": 0.0012887364719063044
  },
  "final_prediction": "common_rust (99.52%)"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```