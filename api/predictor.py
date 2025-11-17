import torch
from torchvision import models, transforms
from PIL import Image
import io

class MaizeDiseasePredictor:
    def __init__(self):
        # Load model
        self.model = models.resnet18(pretrained=False)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 7)
        
        url = "https://huggingface.co/albertosei/agricom-new-maize-disease-resnet18/resolve/main/pytorch_model.bin"
        state_dict = torch.hub.load_state_dict_from_url(url, map_location='cpu')
        self.model.load_state_dict(state_dict)
        self.model.eval()
        
        # Preprocessing
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        self.classes = [
            "common_rust", "gray_leaf_spot", "healthy", "maize_ear_rot",
            "maize_fall_armyworm", "maize_stem_borer", "northern_leaf_blight"
        ]
    
    def predict(self, image_bytes):
        # Load image from bytes
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Inference
        input_tensor = self.transform(img).unsqueeze(0)
        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.softmax(output, dim=1)[0]
            pred_idx = torch.argmax(probs).item()
        
        return {
            "disease": self.classes[pred_idx],
            "confidence": float(probs[pred_idx]),
            "all_probs": {self.classes[i]: float(probs[i]) for i in range(7)}
        }
