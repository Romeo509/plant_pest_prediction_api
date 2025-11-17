import torch
from torchvision import models, transforms
from PIL import Image
import requests
from io import BytesIO

# ===== Load model =====
model = models.resnet18(pretrained=False)
model.fc = torch.nn.Linear(model.fc.in_features, 7)

url = "https://huggingface.co/albertosei/agricom-new-maize-disease-resnet18/resolve/main/pytorch_model.bin"
state_dict = torch.hub.load_state_dict_from_url(url, map_location='cpu')
model.load_state_dict(state_dict)
model.eval()

# ===== Preprocess =====
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ===== Predict =====
def predict_maize_disease(image_path_or_url):
    # Handle URL or local file
    if image_path_or_url.startswith("http"):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(image_path_or_url, headers=headers, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        img = Image.open(image_path_or_url).convert("RGB")

    # Inference
    input_tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)[0]
        pred_idx = torch.argmax(probs).item()

    classes = [
        "common_rust", "gray_leaf_spot", "healthy", "maize_ear_rot",
        "maize_fall_armyworm", "maize_stem_borer", "northern_leaf_blight"
    ]
    return {
        "disease": classes[pred_idx],
        "confidence": float(probs[pred_idx]),
        "all_probs": {classes[i]: float(probs[i]) for i in range(7)}
    }

# ===== New helper function =====
def display_top_prediction(result):
    # Find the class with the highest probability
    top_class = max(result["all_probs"], key=result["all_probs"].get)
    top_confidence = result["all_probs"][top_class] * 100  # convert to %
    print(f"🎯 Final Prediction: {top_class} ({top_confidence:.2f}%)")

# ===== Example =====
image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQcgbMso7ohbxIaviIh5mqMJxbXx36mj2ToWQ&s"
result = predict_maize_disease(image_url)
print(result)              # original detailed output
display_top_prediction(result)  # simplified final prediction with %
