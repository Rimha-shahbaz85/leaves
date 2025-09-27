from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
import logging
import os
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leaf Disease Detection API", version="1.0.0")

@app.post('/disease-detection-file')
async def disease_detection_file(file: UploadFile = File(...)):
    """
    Endpoint to detect diseases in leaf images using direct image file upload.
    Accepts multipart/form-data with an image file.
    """
    try:
        logger.info("Received image file for disease detection")
        
        # Read uploaded file into memory
        contents = await file.read()
        
        # Convert to base64 for processing
        base64_string = base64.b64encode(contents).decode('utf-8')
        
        # For now, return a simple response (you can integrate your ML model later)
        result = {
            "status": "success",
            "message": "Image received successfully",
            "file_size": len(contents),
            "base64_length": len(base64_string),
            "filename": file.filename,
            "content_type": file.content_type
        }
        
        logger.info("Disease detection from file completed successfully")
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in disease detection (file): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint serving the HTML interface"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Leaf Disease Detection API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌿 Leaf Disease Detection API</h1>
                <p>Welcome to the Leaf Disease Detection API. Use the following endpoint to analyze leaf images:</p>
                <div class="endpoint">
                    <strong>POST /disease-detection-file</strong><br>
                    Upload an image file for disease analysis
                </div>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Status:</strong> Running</p>
            </div>
        </body>
        </html>
        """)

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Leaf Disease Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)"
        }
    }
