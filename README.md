# 🌿 Plant Disease Identifier API

This is a FastAPI-based application that uses NVIDIA’s VILA model to **identify plant diseases**, determine **what causes them**, and suggest **control measures** based on uploaded media (images or videos of plants).

---

## 🚀 Features

- Upload images or videos of diseased plants
- Returns diagnosis, cause, and control measures
- Uses NVIDIA's VILA model via their hosted API
- Fully documented via Swagger UI (`/docs`)
- Easy-to-use demo web interface (`/`)
- Supports JPG, PNG, JPEG, and MP4

---

## 🖼 Demo UI

Visit `http://localhost:8000` to use a simple frontend:

1. Upload a photo or video of a plant
2. Click "Analyze"
3. Get results instantly (no prompt writing needed)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/plant-disease-identifier.git
cd plant-disease-identifier
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 🔐 Setup `.env`

Before running the app, create a `.env` file in the root of your project and add your NVIDIA API key:
NVIDIA_API_KEY=your_nvidia_api_key_here
You can obtain the API key by registering on [https://platform.nvidia.com](https://platform.nvidia.com).

## 🏃 Run the App

Start the FastAPI server using:

```bash
uvicorn main:app --reload
```

## 🌐 Access Points

Once running, you’ll have access to:

### 🌍 Frontend Demo  
**URL:** [http://localhost:8000](http://localhost:8000)  
A simple web interface where you can upload plant images or videos and receive an automatic diagnosis.

---

### 🔧 Swagger Docs  
**URL:** [http://localhost:8000/docs](http://localhost:8000/docs)  
Auto-generated documentation with an interactive UI to test the API endpoints directly in your browser.

---

### 📘 Redoc Docs  
**URL:** [http://localhost:8000/redoc](http://localhost:8000/redoc)  
An alternative, neatly structured documentation page for browsing and understanding your API.

## 🧪 API Usage

### `POST /describe`

**Purpose:** Analyze uploaded plant media and identify:

- ✅ The plant disease  
- ✅ What causes it  
- ✅ How to control or treat it  

---

### ✅ Parameters

- `media` (multipart/form-data): One or more image or video files  
- **Supported formats:** `.jpg`, `.jpeg`, `.png`, `.mp4`

#🧾 Example with curl
```
curl -X POST http://localhost:8000/describe \
  -F "media=@leaf1.jpg" \
  -F "media=@leaf2.jpg"
```

# 📤 Example Response
```
{
  "choices": [
    {
      "message": {
        "content": "The plant appears to be affected by maize streak virus, caused by leafhoppers..."
      }
    }
  ]
}
```

# 🖼 Frontend Demo
- The root path (/) hosts a simple HTML page:

- Upload a photo or video of a plant

- Click “Analyze”

- See the generated diagnosis directly below

- This is useful for:

- Quick tests

- Showcasing your tool

- Letting farmers or users interact easily

# 📁 Folder Structure
```
plant_diagnosis_app/
├── main.py               # FastAPI application
├── .env                  # NVIDIA API key (ignored in version control)
├── requirements.txt      # Python dependencies
├── uploads/              # Temporary storage for uploaded files
├── templates/
│   └── index.html        # Web UI template
└── README.md             # Documentation
```

# 💡 How It Works
- 🧑‍🌾 User uploads media via UI or API

- ☁️ Backend uploads the media to NVIDIA’s cloud

- 🤖 VILA model is invoked with this prompt:

- "Identify the plant disease, what it's caused by, and how to control it."

- 📬 The response is returned as structured text

- 🧹 Uploaded media and cloud assets are deleted automatically

# 📦 Tech Stack
- FastAPI – For API and web routing

- Uvicorn – ASGI server for local development

- NVIDIA VILA API – Vision-language model doing the actual plant analysis

- Jinja2 – For HTML rendering

- Requests – For handling external API calls

- dotenv – To manage secrets and environment variables

## 📚 Use Cases

- 🌾 Agricultural support tools for farmers  
- 🔬 Academic research on plant disease detection  
- 📷 Drone or camera-based crop monitoring  
- 🛰️ Satellite image analysis for large-scale crop health  
- 🌍 NGOs or ministries improving rural food security and crop health
