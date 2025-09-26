from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
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


@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "Leaf Disease Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "disease_detection_file": "/disease-detection-file (POST, file upload)"
        }
    }
