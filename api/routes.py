from fastapi import APIRouter, File, UploadFile, HTTPException
from api.predictor import MaizeDiseasePredictor

router = APIRouter()
predictor = MaizeDiseasePredictor()

@router.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    """
    Endpoint to predict maize disease from uploaded image
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Get prediction
        result = predictor.predict(image_bytes)
        
        # Calculate top prediction percentage
        top_class = max(result["all_probs"], key=result["all_probs"].get)
        top_confidence = result["all_probs"][top_class] * 100
        
        return {
            "disease": result["disease"],
            "confidence": result["confidence"],
            "all_probs": result["all_probs"],
            "final_prediction": f"{top_class} ({top_confidence:.2f}%)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
