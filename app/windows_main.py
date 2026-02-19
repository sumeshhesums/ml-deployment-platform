"""
Windows-compatible version of the ML Deployment Platform
Uses only basic Python modules that are guaranteed to work
"""

import os
import uuid
import json
import pickle
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Simple in-memory database
models_db = {}
MODELS_DIR = "deployed_models"
os.makedirs(MODELS_DIR, exist_ok=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(200)
        self.wfile.write(b"OK")
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/":
            response = {
                "message": "ML Model Deployment Platform (Windows)",
                "status": "running",
                "endpoints": {
                    "upload_model": "POST /models/upload",
                    "list_models": "GET /models",
                    "predict": "POST /predict/{model_id}",
                    "model_stats": "GET /models/{model_id}/stats"
                }
            }
            self._set_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif parsed_path.path == "/models":
            response = {
                "status": "success",
                "count": len(models_db),
                "models": list(models_db.values())
            }
            self._set_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif parsed_path.path.startswith("/models/"):
            # Extract model_id from path
            parts = parsed_path.path.split("/")
            if len(parts) > 2:
                model_id = parts[-2]
                if model_id in models_db:
                    model_info = models_db[model_id]
                    response = {
                        "status": "success",
                        "model_info": model_info,
                        "statistics": {
                            "usage_count": model_info.get("usage_count", 0),
                            "upload_date": model_info["upload_date"]
                        }
                    }
                    self._set_headers()
                    self.wfile.write(json.dumps(response, indent=2).encode())
                    return
            
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Model not found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if parsed_path.path == "/models/upload":
            try:
                # Simple file upload handling without cgi
                content_type = self.headers.get('Content-Type', '')
                
                if 'multipart/form-data' in content_type:
                    # Parse boundary
                    boundary = content_type.split('boundary=')[1].encode()
                    parts = post_data.split(b'--' + boundary)
                    
                    file_data = None
                    form_data = {}
                    
                    for part in parts:
                        if b'Content-Disposition' in part:
                            lines = part.split(b'\r\n')
                            disposition = lines[0].decode()
                            
                            if 'filename=' in disposition:
                                # File part
                                file_start = part.find(b'\r\n\r\n') + 4
                                file_data = part[file_start:].rstrip(b'\r\n--')
                            else:
                                # Form field
                                name_start = disposition.find('name="') + 6
                                name_end = disposition.find('"', name_start)
                                field_name = disposition[name_start:name_end]
                                value_start = part.find(b'\r\n\r\n') + 4
                                field_value = part[value_start:].rstrip(b'\r\n--').decode()
                                form_data[field_name] = field_value
                    
                    if file_data:
                        # Generate model ID
                        model_id = str(uuid.uuid4())
                        
                        # Save file
                        model_path = os.path.join(MODELS_DIR, f"{model_id}.pkl")
                        with open(model_path, 'wb') as f:
                            f.write(file_data)
                        
                        # Get form data
                        name = form_data.get('name', 'Unnamed Model')
                        framework = form_data.get('framework', 'scikit-learn')
                        description = form_data.get('description', '')
                        
                        # Store model info
                        upload_date = datetime.now().isoformat()
                        models_db[model_id] = {
                            "model_id": model_id,
                            "name": name,
                            "framework": framework,
                            "upload_date": upload_date,
                            "description": description,
                            "file_path": model_path,
                            "usage_count": 0
                        }
                        
                        response = {
                            "status": "success",
                            "message": "Model uploaded successfully",
                            "model_info": models_db[model_id]
                        }
                        self._set_headers()
                        self.wfile.write(json.dumps(response, indent=2).encode())
                    else:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "No file uploaded"}).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Unsupported content type"}).encode())
                    
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Upload failed: {str(e)}"}).encode())
                
        elif parsed_path.path.startswith("/predict/"):
            try:
                # Extract model_id
                model_id = parsed_path.path.split("/")[-1]
                
                if model_id not in models_db:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"error": "Model not found"}).encode())
                    return
                
                # Parse JSON body
                try:
                    request_data = json.loads(post_data.decode())
                    input_data = request_data.get('input_data', [])
                except:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                    return
                
                # Load model and make prediction
                model_path = models_db[model_id]["file_path"]
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                
                # Simple prediction
                if hasattr(model, 'predict'):
                    predictions = model.predict(input_data)
                    predictions_list = predictions.tolist() if hasattr(predictions, 'tolist') else list(predictions)
                else:
                    predictions_list = ["Model doesn't have predict method"]
                
                # Update usage count
                models_db[model_id]["usage_count"] += 1
                
                response = {
                    "status": "success",
                    "model_id": model_id,
                    "model_name": models_db[model_id]["name"],
                    "predictions": predictions_list,
                    "timestamp": datetime.now().isoformat()
                }
                self._set_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Prediction failed: {str(e)}"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"🚀 ML Deployment Platform (Windows) running on http://localhost:{port}")
    print("📚 Documentation: http://localhost:8000")
    print("💡 Windows-compatible version using basic Python modules")
    print("\nEndpoints:")
    print("  GET  /                    - Platform info")
    print("  GET  /models             - List all models")
    print("  POST /models/upload      - Upload a model")
    print("  POST /predict/{model_id} - Make predictions")
    print("  GET  /models/{model_id}/stats - Get model stats")
    print("\nPress Ctrl+C to stop the server")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()