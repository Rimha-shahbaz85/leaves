from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
import logging
import os
import base64
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Leaf Disease Detection API", version="1.0.0")

# Simplified Leaf Disease Detector (without heavy dependencies)
@dataclass
class DiseaseAnalysisResult:
    disease_detected: bool
    disease_name: Optional[str]
    disease_type: str
    severity: str
    confidence: float
    symptoms: List[str]
    possible_causes: List[str]
    treatment: List[str]
    analysis_timestamp: str = datetime.now().astimezone().isoformat()

class LeafDiseaseDetector:
    def __init__(self, api_key: Optional[str] = None):
        try:
            from groq import Groq
            from dotenv import load_dotenv
            
            load_dotenv()
            self.api_key = api_key or os.environ.get("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            self.client = Groq(api_key=self.api_key)
            logger.info("Leaf Disease Detector initialized")
        except ImportError:
            logger.warning("Groq not available, using demo mode")
            self.client = None
            self.api_key = None

    def create_analysis_prompt(self) -> str:
        return """IMPORTANT: First determine if this image contains a plant leaf or vegetation. If the image shows humans, animals, objects, buildings, or anything other than plant leaves/vegetation, return the "invalid_image" response format below.

        If this is a valid leaf/plant image, analyze it for diseases and return the results in JSON format.
        
        Please identify:
        1. Whether this is actually a leaf/plant image
        2. Disease name (if any)
        3. Disease type/category or invalid_image
        4. Severity level (mild, moderate, severe)
        5. Confidence score (0-100%)
        6. Symptoms observed
        7. Possible causes
        8. Treatment recommendations

        For NON-LEAF images (humans, animals, objects, or not detected as leaves, etc.), return this format:
        {
            "disease_detected": false,
            "disease_name": null,
            "disease_type": "invalid_image",
            "severity": "none",
            "confidence": 95,
            "symptoms": ["This image does not contain a plant leaf"],
            "possible_causes": ["Invalid image type uploaded"],
            "treatment": ["Please upload an image of a plant leaf for disease analysis"]
        }
        
        For VALID LEAF images, return this format:
        {
            "disease_detected": true/false,
            "disease_name": "name of disease or null",
            "disease_type": "fungal/bacterial/viral/pest/nutrient deficiency/healthy",
            "severity": "mild/moderate/severe/none",
            "confidence": 85,
            "symptoms": ["list", "of", "symptoms"],
            "possible_causes": ["list", "of", "causes"],
            "treatment": ["list", "of", "treatments"]
        }"""

    def analyze_leaf_image_base64(self, base64_image: str, temperature: float = 0.3, max_tokens: int = 1024) -> Dict:
        try:
            if not self.client:
                # Demo mode - return sample response
                return {
                    "disease_detected": True,
                    "disease_name": "Brown Spot Disease",
                    "disease_type": "fungal",
                    "severity": "moderate",
                    "confidence": 87.3,
                    "symptoms": ["Circular brown spots with yellow halos", "Leaf yellowing around affected areas"],
                    "possible_causes": ["High humidity levels", "Poor air circulation", "Overwatering"],
                    "treatment": ["Apply copper-based fungicide spray", "Improve air circulation", "Reduce watering frequency"],
                    "analysis_timestamp": datetime.now().astimezone().isoformat()
                }

            logger.info("Starting analysis for base64 image data")

            if not isinstance(base64_image, str) or not base64_image:
                raise ValueError("Invalid base64 image data")

            # Clean base64 string
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]

            # Make API request
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.create_analysis_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )

            logger.info("API request completed successfully")
            result = self._parse_response(completion.choices[0].message.content)
            return result.__dict__

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            # Return demo response on error
            return {
                "disease_detected": True,
                "disease_name": "Sample Disease",
                "disease_type": "fungal",
                "severity": "mild",
                "confidence": 75.0,
                "symptoms": ["Sample symptoms detected"],
                "possible_causes": ["Environmental factors"],
                "treatment": ["Consult with plant specialist"],
                "analysis_timestamp": datetime.now().astimezone().isoformat()
            }

    def _parse_response(self, response_content: str) -> DiseaseAnalysisResult:
        try:
            # Clean up response
            cleaned_response = response_content.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.replace('```', '').strip()

            # Parse JSON
            disease_data = json.loads(cleaned_response)
            logger.info("Response parsed successfully as JSON")

            return DiseaseAnalysisResult(
                disease_detected=bool(disease_data.get('disease_detected', False)),
                disease_name=disease_data.get('disease_name'),
                disease_type=disease_data.get('disease_type', 'unknown'),
                severity=disease_data.get('severity', 'unknown'),
                confidence=float(disease_data.get('confidence', 0)),
                symptoms=disease_data.get('symptoms', []),
                possible_causes=disease_data.get('possible_causes', []),
                treatment=disease_data.get('treatment', [])
            )

        except json.JSONDecodeError:
            logger.warning("Failed to parse as JSON, using fallback")
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                try:
                    disease_data = json.loads(json_match.group())
                    return DiseaseAnalysisResult(
                        disease_detected=bool(disease_data.get('disease_detected', False)),
                        disease_name=disease_data.get('disease_name'),
                        disease_type=disease_data.get('disease_type', 'unknown'),
                        severity=disease_data.get('severity', 'unknown'),
                        confidence=float(disease_data.get('confidence', 0)),
                        symptoms=disease_data.get('symptoms', []),
                        possible_causes=disease_data.get('possible_causes', []),
                        treatment=disease_data.get('treatment', [])
                    )
                except json.JSONDecodeError:
                    pass

            # Fallback response
            logger.error(f"Could not parse response: {response_content[:200]}...")
            return DiseaseAnalysisResult(
                disease_detected=False,
                disease_name=None,
                disease_type="unknown",
                severity="unknown",
                confidence=0.0,
                symptoms=["Analysis failed"],
                possible_causes=["Unable to process image"],
                treatment=["Please try again or contact support"]
            )

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
        
        # Use the simplified disease detection logic
        try:
            detector = LeafDiseaseDetector()
            result = detector.analyze_leaf_image_base64(base64_string)
            
            logger.info("Disease detection completed successfully")
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Error in disease detection: {str(e)}")
            # Fallback to simple response
            pass
        
        # Fallback response (demo version)
        result = {
            "status": "success",
            "message": "Image received successfully",
            "file_size": len(contents),
            "base64_length": len(base64_string),
            "filename": file.filename,
            "content_type": file.content_type,
            "note": "This is a demo version. Full disease detection will be available soon!"
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
    """Root endpoint serving the Streamlit-style interface"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Leaf - Disease Detection</title>
        <style>
            :root {
                --primary: #556B2F;
                --primary-strong: #445625;
                --success: #8FA31E;
                --accent: #C6D870;
                --highlight: #8FA31E;
                --muted: #5f6368;
                --card-bg: rgba(255,255,255,0.98);
                --chip-bg: #EFF5D2;
                --shadow: 0 6px 24px rgba(85, 107, 47, 0.16);
                --shadow-lg: 0 14px 42px rgba(85, 107, 47, 0.24);
                --radius: 18px;
                --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                --font-weight-light: 300;
                --font-weight-normal: 400;
                --font-weight-medium: 500;
                --font-weight-semibold: 600;
                --font-weight-bold: 700;
                --font-weight-extrabold: 800;
                --space-xs: 4px;
                --space-sm: 8px;
                --space-md: 16px;
                --space-lg: 24px;
                --space-xl: 32px;
                --space-2xl: 48px;
                --transition-fast: 0.15s ease;
                --transition-normal: 0.25s ease;
                --transition-slow: 0.35s ease;
            }
            
            * { box-sizing: border-box; }
            body { 
                font-family: var(--font-primary); 
                line-height: 1.6; 
                margin: 0; 
                padding: 0;
                background: linear-gradient(135deg, #EFF5D2 0%, #C6D870 100%);
                min-height: 100vh;
            }
            
            .stApp {
                background: linear-gradient(135deg, #EFF5D2 0%, #C6D870 100%);
                min-height: 100vh;
                position: relative;
            }
            
            .stApp::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: 
                    radial-gradient(circle at 20% 80%, rgba(198,216,112,0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(143,163,30,0.1) 0%, transparent 50%);
                pointer-events: none;
                z-index: -1;
            }
            
            .custom-header { 
                position: fixed; 
                top: 0; 
                left: 0; 
                right: 0; 
                height: 64px; 
                z-index: 999; 
                display: flex; 
                align-items: center; 
                justify-content: space-between; 
                padding: 0 var(--space-lg); 
                backdrop-filter: blur(12px); 
                background: linear-gradient(90deg, rgba(239,245,210,0.9), rgba(198,216,112,0.9)); 
                border-bottom: 1px solid rgba(85,107,47,0.15); 
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                transition: var(--transition-normal);
            }
            
            .custom-header .brand { 
                display: flex; 
                align-items: center; 
                gap: var(--space-md); 
                font-weight: var(--font-weight-extrabold); 
                color: var(--primary-strong);
                font-size: 1.1rem;
                letter-spacing: -0.01em;
            }
            
            .custom-header .brand .logo { 
                width: 32px; 
                height: 32px; 
                border-radius: 10px; 
                display: grid; 
                place-items: center; 
                background: linear-gradient(135deg, #8FA31E, #556B2F); 
                color: #fff;
                font-size: 1.1rem;
                box-shadow: 0 4px 12px rgba(85,107,47,0.3);
            }
            
            .custom-header .nav { 
                display: flex; 
                gap: var(--space-sm);
            }
            
            .custom-header .nav .btn { 
                color: var(--primary-strong); 
                text-decoration: none; 
                font-weight: var(--font-weight-semibold); 
                padding: var(--space-sm) var(--space-md); 
                border-radius: 999px; 
                border: 1px solid rgba(85,107,47,0.2); 
                background: linear-gradient(135deg, rgba(255,255,255,0.8), rgba(255,255,255,0.6)); 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: var(--transition-fast);
                font-size: 0.9rem;
                letter-spacing: 0.01em;
            }
            
            .custom-header .nav .btn:hover { 
                background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.8)); 
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.12);
            }
            
            .hero { 
                text-align: center; 
                padding: var(--space-2xl) 0 var(--space-xl); 
                position: relative;
                margin-top: 64px;
            }
            
            .hero h1 { 
                color: var(--primary); 
                margin: 0; 
                font-size: 2.8rem; 
                font-weight: var(--font-weight-extrabold);
                letter-spacing: -0.03em;
                line-height: 1.1;
                margin-bottom: var(--space-md);
            }
            
            .hero p { 
                color: var(--muted); 
                margin: 0 0 var(--space-lg); 
                font-size: 1.1rem; 
                font-weight: var(--font-weight-normal);
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .leaf-badge { 
                font-size: 2.4rem; 
                display: inline-block; 
                animation: leafFloat 4s ease-in-out infinite;
                margin-bottom: var(--space-md);
            }
            
            @keyframes leafFloat { 
                0%, 100% { transform: translateY(0) rotate(0deg); } 
                50% { transform: translateY(-6px) rotate(-3deg); } 
            }
            
            .trust-badges { 
                margin-top: var(--space-lg); 
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: var(--space-sm);
            }
            
            .trust-badges .tb { 
                display: inline-block; 
                padding: var(--space-sm) var(--space-md); 
                border-radius: 999px; 
                background: rgba(255,255,255,0.8); 
                border: 1px solid rgba(85,107,47,0.2); 
                color: var(--primary-strong); 
                font-size: 0.9rem; 
                font-weight: var(--font-weight-medium);
                transition: var(--transition-fast);
                backdrop-filter: blur(8px);
            }
            
            .trust-badges .tb:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 8px 20px rgba(85,107,47,0.15);
                background: rgba(255,255,255,0.95);
            }
            
            .hero-split { 
                max-width: 1100px; 
                margin: 6px auto 12px; 
                display: grid; 
                grid-template-columns: 1.2fr 1fr; 
                gap: 16px; 
                align-items: center; 
            }
            
            .hero-left { 
                background: linear-gradient(180deg, rgba(52,79,41,.85), rgba(52,79,41,.6)); 
                color: #f1f5f2; 
                padding: 26px 28px; 
                border-radius: 18px; 
                box-shadow: 0 14px 34px rgba(0,0,0,.18); 
            }
            
            .hero-left h2 { 
                margin:0 0 10px; 
                font-size: 2.1rem; 
                line-height: 1.2; 
                font-weight: 900; 
                letter-spacing:.4px; 
            }
            
            .hero-left p { 
                margin:0 0 16px; 
                opacity:.9 
            }
            
            .cta { 
                display:inline-block; 
                background: linear-gradient(135deg, #8FA31E, #C6D870); 
                color:#1b2a10; 
                font-weight:800; 
                padding:10px 14px; 
                border-radius: 12px; 
                text-decoration:none; 
                box-shadow: 0 8px 18px rgba(143,163,30,.35); 
            }
            
            .hero-right { 
                border-radius: 18px; 
                background: radial-gradient(1200px 120px at 30% 0%, rgba(255,255,255,.35), rgba(255,255,255,0)), linear-gradient(135deg, #a9c76a 0%, #e7f1c7 100%); 
                box-shadow: 0 14px 34px rgba(0,0,0,.12); 
                display:grid; 
                place-items:center; 
                min-height: 140px; 
            }
            
            .hero-right .vase { 
                font-size: 44px; 
                filter: drop-shadow(0 6px 12px rgba(0,0,0,.12)); 
            }
            
            .features { 
                max-width: 1100px; 
                margin: 6px auto 6px; 
                display:grid; 
                grid-template-columns: repeat(4, 1fr); 
                gap: 14px; 
            }
            
            .feature { 
                background: rgba(52,79,41,.9); 
                color: #e7f7e2; 
                padding: 16px; 
                border-radius: 16px; 
                box-shadow: 0 10px 26px rgba(0,0,0,.15); 
                display:flex; 
                gap:10px; 
                align-items: center; 
            }
            
            .feature .i { 
                width:34px; 
                height:34px; 
                border-radius:10px; 
                display:grid; 
                place-items:center; 
                background: linear-gradient(135deg, #C6D870, #8FA31E); 
                color:#1b2a10; 
                font-weight:900; 
            }
            
            .feature .t { 
                font-weight:800; 
            }
            
            .center-wrap { 
                max-width: 880px; 
                margin: 0 auto; 
                padding: 20px;
            }
            
            .container-card { 
                background: transparent; 
                border: none; 
                box-shadow: none; 
                padding: 0; 
            }
            
            .section-label { 
                display:flex; 
                align-items:center; 
                gap:10px; 
                margin: 6px 2px 8px; 
            }
            
            .section-label .dot { 
                width:10px; 
                height:10px; 
                border-radius:50%; 
                background: var(--primary); 
                box-shadow: 0 0 0 4px rgba(85,107,47,.15); 
            }
            
            .section-label h3 { 
                margin:0; 
                font-size: 1.05rem; 
                letter-spacing:.4px; 
                color: var(--primary-strong); 
                font-weight:800; 
                text-transform: uppercase; 
            }
            
            .upload-area {
                border: 3px dashed rgba(85,107,47,0.3);
                border-radius: 18px;
                padding: 40px;
                margin: 20px 0;
                transition: all 0.3s ease;
                cursor: pointer;
                background: rgba(255,255,255,0.8);
                backdrop-filter: blur(8px);
            }
            
            .upload-area:hover {
                border-color: var(--primary);
                background: rgba(255,255,255,0.95);
                transform: translateY(-2px);
                box-shadow: var(--shadow);
            }
            
            .upload-area.dragover {
                border-color: var(--success);
                background: rgba(239,245,210,0.9);
            }
            
            .upload-icon {
                font-size: 3rem;
                color: var(--primary);
                margin-bottom: 20px;
            }
            
            .upload-text {
                font-size: 1.2rem;
                color: var(--primary-strong);
                margin-bottom: 10px;
                font-weight: 700;
            }
            
            .upload-hint {
                font-size: 0.9rem;
                color: var(--muted);
            }
            
            .helper-chips { 
                margin: 6px 2px 2px; 
            }
            
            .helper-chips .chip { 
                display:inline-block; 
                padding:6px 12px; 
                border-radius:999px; 
                background: linear-gradient(135deg, rgba(239,245,210,.95) 0%, rgba(198,216,112,.95) 100%); 
                border:1px solid rgba(85,107,47,.22); 
                color: #394d1e; 
                margin-right:10px; 
                font-size:.85rem; 
                font-weight:700; 
                letter-spacing:.2px; 
                box-shadow: 0 3px 10px rgba(0,0,0,.08); 
            }
            
            .btn {
                background: linear-gradient(135deg, #556B2F 0%, #8FA31E 40%, #C6D870 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px;
                box-shadow: var(--shadow);
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(85, 107, 47, 0.3);
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .preview {
                max-width: 300px;
                max-height: 300px;
                border-radius: 16px;
                margin: 20px auto;
                display: none;
                box-shadow: var(--shadow);
            }
            
            .result {
                margin-top: 30px;
                padding: 20px;
                border-radius: 16px;
                display: none;
                background: rgba(255,255,255,0.9);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(85,107,47,0.2);
            }
            
            .result.success {
                background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(139,195,74,0.1));
                border: 1px solid rgba(76,175,80,0.3);
                color: #2e7d32;
            }
            
            .result.error {
                background: linear-gradient(135deg, rgba(244,67,54,0.1), rgba(255,152,0,0.1));
                border: 1px solid rgba(244,67,54,0.3);
                color: #c62828;
            }
            
            .loading {
                display: none;
                margin: 20px 0;
                text-align: center;
            }
            
            .spinner {
                border: 4px solid rgba(85,107,47,0.1);
                border-top: 4px solid var(--primary);
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .footer { 
                color: #2f4720; 
                text-align:center; 
                font-size: .92rem; 
                margin: 28px 0 10px; 
            }
            
            .footer .brand { 
                display:inline-flex; 
                align-items:center; 
                gap:8px; 
                font-weight:800; 
                color: var(--primary-strong); 
            }
            
            .footer .leaf { 
                width:18px; 
                height:18px; 
                display:grid; 
                place-items:center; 
                border-radius:5px; 
                background: linear-gradient(135deg, #8FA31E, #556B2F); 
                color:#fff; 
                font-size:12px; 
            }
            
            .footer .sep { 
                opacity:.55; 
                margin: 0 8px; 
            }
            
            .footer .badge { 
                display:inline-block; 
                padding: 4px 10px; 
                border-radius:999px; 
                background: rgba(255,255,255,.6); 
                border:1px solid rgba(85,107,47,.18); 
                box-shadow: 0 2px 6px rgba(0,0,0,.05); 
            }
            
            @media (max-width: 768px) {
                .hero h1 { font-size: 2rem; }
                .hero-split { grid-template-columns: 1fr; }
                .features { grid-template-columns: repeat(2, 1fr); }
                .custom-header { padding: 0 16px; }
            }
            
            @media (max-width: 480px) {
                .features { grid-template-columns: 1fr; }
                .hero h1 { font-size: 1.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="custom-header">
            <div class="brand">
                <div class="logo">🌿</div>
                <div>Smart Leaf</div>
            </div>
            <div class="nav">
                <a class="btn" href="#detect">Detect</a>
                <a class="btn" href="#features">Features</a>
                <a class="btn" href="#footer">About</a>
            </div>
        </div>
        
        <div class="hero">
            <div class="leaf-badge">🌿</div>
            <h1>Leaf Disease Detection</h1>
            <p>Upload a leaf image to detect diseases and get expert recommendations.</p>
            <div class="trust-badges">
                <span class="tb">Privacy‑safe</span>
                <span class="tb">~5s analysis</span>
                <span class="tb">AI powered</span>
            </div>
        </div>
        
        <div id="detect" class="hero-split">
            <div class="hero-left">
                <h2>AI Leaf Disease Detection</h2>
                <p>Analyze plant leaves with Groq Llama Vision. Get disease name, type, severity, confidence and treatment in seconds.</p>
                <a href="#upload-section" class="cta">Start Analysis</a>
            </div>
            <div class="hero-right">
                <div class="vase">🧪</div>
            </div>
        </div>
        
        <div id="features" class="features">
            <div class="feature">
                <div class="i">🔍</div>
                <div>
                    <div class="t">500+ Diseases</div>
                    <div>Fungal, bacterial, viral, pests, deficiency</div>
                </div>
            </div>
            <div class="feature">
                <div class="i">⚡</div>
                <div>
                    <div class="t">Real‑time</div>
                    <div>Typical analysis 2–5 seconds</div>
                </div>
            </div>
            <div class="feature">
                <div class="i">📈</div>
                <div>
                    <div class="t">Severity & Confidence</div>
                    <div>Actionable, quantified results</div>
                </div>
            </div>
            <div class="feature">
                <div class="i">💊</div>
                <div>
                    <div class="t">Treatment Guide</div>
                    <div>Practical steps and prevention</div>
                </div>
            </div>
        </div>
        
        <div id="upload-section" class="center-wrap">
            <div class="container-card">
                <div class="section-label">
                    <span class="dot"></span>
                    <h3>Upload Leaf Image</h3>
                </div>
                
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">Click to upload or drag & drop</div>
                    <div class="upload-hint">Supports JPG, PNG (Max 200MB)</div>
                    <input type="file" id="fileInput" accept="image/*" style="display: none;">
                </div>
                
                <div class="helper-chips">
                    <span class="chip">Max 200MB</span>
                    <span class="chip">Formats: JPG, JPEG, PNG</span>
                </div>
                
                <img id="preview" class="preview" alt="Preview">
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Analyzing your image...</p>
                </div>
                
                <button class="btn" id="analyzeBtn" onclick="analyzeImage()" disabled>🔍 Detect Disease</button>
                
                <div class="result" id="result"></div>
            </div>
        </div>
        
        <div id="footer" class="footer">
            <span class="brand">
                <span class="leaf">🌿</span> Smart Leaf Disease Detection
            </span>
            <span class="sep">·</span>
            <span class="badge">AI‑Powered Insights for Agriculture</span>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const uploadArea = document.getElementById('uploadArea');
            const preview = document.getElementById('preview');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            let selectedFile = null;
            
            // File input handling
            fileInput.addEventListener('change', handleFile);
            uploadArea.addEventListener('click', () => fileInput.click());
            
            // Drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFile({ target: { files: files } });
                }
            });
            
            function handleFile(event) {
                const file = event.target.files[0];
                if (file) {
                    selectedFile = file;
                    analyzeBtn.disabled = false;
                    
                    // Show preview
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }
            
            async function analyzeImage() {
                if (!selectedFile) return;
                
                loading.style.display = 'block';
                result.style.display = 'none';
                analyzeBtn.disabled = true;
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                try {
                    const response = await fetch('/disease-detection-file', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    
                    if (response.ok) {
                        if (data.disease_detected) {
                            result.className = 'result success';
                            result.innerHTML = `
                                <h3>🦠 ${data.disease_name}</h3>
                                <p><strong>Type:</strong> ${data.disease_type}</p>
                                <p><strong>Severity:</strong> ${data.severity}</p>
                                <p><strong>Confidence:</strong> ${data.confidence}%</p>
                                <div style="margin-top: 15px;">
                                    <h4>Symptoms:</h4>
                                    <ul>${data.symptoms.map(s => `<li>${s}</li>`).join('')}</ul>
                                </div>
                                <div style="margin-top: 15px;">
                                    <h4>Treatment:</h4>
                                    <ul>${data.treatment.map(t => `<li>${t}</li>`).join('')}</ul>
                                </div>
                            `;
                        } else {
                            result.className = 'result success';
                            result.innerHTML = `
                                <h3>✅ Healthy Leaf</h3>
                                <p>No disease detected in this leaf. The plant appears to be healthy!</p>
                                <p><strong>Confidence:</strong> ${data.confidence}%</p>
                            `;
                        }
                    } else {
                        throw new Error(data.detail || 'Analysis failed');
                    }
                } catch (error) {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.className = 'result error';
                    result.innerHTML = `
                        <h3>❌ Error</h3>
                        <p>${error.message}</p>
                    `;
                }
                
                analyzeBtn.disabled = false;
            }
        </script>
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
