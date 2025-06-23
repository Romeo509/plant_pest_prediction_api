from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import uuid, requests, os
from typing import List
from pathlib import Path

load_dotenv()

app = FastAPI(
    title="Plant Disease Identifier API",
    description="Upload a photo or video of a plant, and this API will identify the disease, what causes it, and how to control it.",
    version="1.0.0"
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("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")
UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

kNvcfAssetUrl = "https://api.nvcf.nvidia.com/v2/nvcf/assets"
INVOKE_URL = "https://ai.api.nvidia.com/v1/vlm/nvidia/vila"

kSupportedList = {
    "png": ["image/png", "img"],
    "jpg": ["image/jpg", "img"],
    "jpeg": ["image/jpeg", "img"],
    "mp4": ["video/mp4", "video"],
}

def get_ext(filename): return filename.split(".")[-1].lower()
def mime_type(ext): return kSupportedList[ext][0]
def media_type(ext): return kSupportedList[ext][1]

def _upload_asset(file_path, description):
    ext = get_ext(file_path)
    with open(file_path, "rb") as f:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        auth_response = requests.post(kNvcfAssetUrl, headers=headers, json={
            "contentType": mime_type(ext), "description": description
        })

        try:
            auth_json = auth_response.json()
        except:
            raise Exception(f"Auth failed: {auth_response.status_code} {auth_response.text}")

        upload = requests.put(
            auth_json["uploadUrl"],
            data=f,
            headers={
                "x-amz-meta-nvcf-asset-description": description,
                "content-type": mime_type(ext)
            }
        )
        upload.raise_for_status()
        return auth_json["assetId"]

def _delete_asset(asset_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    requests.delete(f"{kNvcfAssetUrl}/{asset_id}", headers=headers)

@app.post("/describe")
async def describe_plant_disease(media: List[UploadFile] = File(...)):
    """
    Upload media to identify plant diseases, causes, and control measures.
    """
    query = "Identify the plant disease, what it's caused by, and how to control it."
    asset_ids, media_tags, file_paths = [], [], []

    for file in media:
        ext = get_ext(file.filename)
        if ext not in kSupportedList:
            return JSONResponse({"error": f"{file.filename} format not supported"}, status_code=400)

        filename = f"{uuid.uuid4()}.{ext}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        with open(path, "wb") as f:
            f.write(await file.read())

        asset_id = _upload_asset(path, "Plant media")
        asset_ids.append(asset_id)
        file_paths.append(path)
        media_tags.append(f'<{media_type(ext)} src="data:{mime_type(ext)};asset_id,{asset_id}" />')

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "NVCF-INPUT-ASSET-REFERENCES": ",".join(asset_ids),
        "NVCF-FUNCTION-ASSET-IDS": ",".join(asset_ids),
        "Accept": "application/json"
    }

    payload = {
        "max_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.7,
        "seed": 42,
        "messages": [{
            "role": "user",
            "content": f"{query} {' '.join(media_tags)}"
        }],
        "stream": False,
        "model": "nvidia/vila"
    }

    res = requests.post(INVOKE_URL, headers=headers, json=payload)
    result = res.json()

    for asset_id in asset_ids:
        _delete_asset(asset_id)
    for path in file_paths:
        os.remove(path)

    return result

@app.get("/", response_class=HTMLResponse)
def demo_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ REQUIRED for Render deployment to bind to 0.0.0.0:$PORT
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
