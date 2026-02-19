"""
Simplified version of the ML Deployment Platform using only built-in modules
This allows you to test the platform without installing additional packages
"""
import os
import uuid
import json
import pickle
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

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
                "message": "ML Model Deployment Platform (Simplified)",
                "status": "running",
                "endpoints": {
                    "upload_model": "POST /models/upload",
                    "list_models": "GET /models",
                    "predict": "POST /predict/{model_id}",
                    "model_stats": "GET /models/{model_id}/stats",
                },
            }
            self._set_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())

        elif parsed_path.path == "/models":
            response = {
                "status": "success",
                "count": len(models_db),
                "models": list(models_db.values()),
            }
            self._set_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())

        elif parsed_path.path.startswith("/models/"):
            # Extract model_id from path
            model_id = parsed_path.path.split("/")[-2]
            if model_id in models_db:
                model_info = models_db[model_id]
                response = {
                    "status": "success",
                    "model_info": model_info,
                    "statistics": {
                        "usage_count": model_info.get("usage_count", 0),
                        "upload_date": model_info["upload_date"],
                    },
                }
                self._set_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Model not found"}).encode())
        elif parsed_path.path == "/favicon.ico":
            self._set_headers(204, "text/plain")
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/models/upload":
            try:
                # Read raw body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                # Parse multipart form data
                content_type = self.headers.get("Content-Type", "")
                boundary = _extract_multipart_boundary(content_type)
                if not boundary:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid Content-Type"}).encode())
                    return

                fields, files = _parse_multipart(body, boundary)

                file_item = files.get("file")
                if file_item and file_item.get("filename"):
                    # Generate model ID
                    model_id = str(uuid.uuid4())

                    # Save file
                    model_path = os.path.join(MODELS_DIR, f"{model_id}.pkl")
                    with open(model_path, "wb") as f:
                        f.write(file_item["content"])

                    # Get other form data
                    name = fields.get("name", "Unnamed Model")
                    framework = fields.get("framework", "scikit-learn")
                    description = fields.get("description", "")

                    # Store model info
                    upload_date = datetime.now().isoformat()
                    models_db[model_id] = {
                        "model_id": model_id,
                        "name": name,
                        "framework": framework,
                        "upload_date": upload_date,
                        "description": description,
                        "file_path": model_path,
                        "usage_count": 0,
                    }

                    response = {
                        "status": "success",
                        "message": "Model uploaded successfully",
                        "model_info": models_db[model_id],
                    }
                    self._set_headers()
                    self.wfile.write(json.dumps(response, indent=2).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "No file uploaded"}).encode())

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
                    content_length = int(self.headers.get("Content-Length", 0))
                    post_data = self.rfile.read(content_length)
                    request_data = json.loads(post_data.decode())
                    input_data = request_data.get("input_data", [])
                except Exception:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                    return

                # Load model and make prediction
                model_path = models_db[model_id]["file_path"]
                with open(model_path, "rb") as f:
                    model = pickle.load(f)

                # Simple prediction - this is a simplified version
                # In production, you'd have proper input validation
                if hasattr(model, "predict"):
                    predictions = model.predict(input_data)
                    predictions_list = (
                        predictions.tolist()
                        if hasattr(predictions, "tolist")
                        else list(predictions)
                    )
                else:
                    predictions_list = ["Model doesn't have predict method"]

                # Update usage count
                models_db[model_id]["usage_count"] += 1

                response = {
                    "status": "success",
                    "model_id": model_id,
                    "model_name": models_db[model_id]["name"],
                    "predictions": predictions_list,
                    "timestamp": datetime.now().isoformat(),
                }
                self._set_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())

            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": f"Prediction failed: {str(e)}"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())


def _extract_multipart_boundary(content_type):
    # Example: "multipart/form-data; boundary=----WebKitFormBoundaryXYZ"
    if "multipart/form-data" not in content_type:
        return None
    parts = content_type.split("boundary=")
    if len(parts) < 2:
        return None
    boundary = parts[-1].strip().strip('"')
    return boundary if boundary else None


def _parse_multipart(body, boundary):
    boundary_bytes = ("--" + boundary).encode()
    parts = body.split(boundary_bytes)
    fields = {}
    files = {}

    for part in parts:
        if not part or part in (b"--\r\n", b"--", b"\r\n"):
            continue

        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if part.endswith(b"--"):
            part = part[:-2]

        header_blob, _, content = part.partition(b"\r\n\r\n")
        if not header_blob:
            continue
        headers = header_blob.decode(errors="ignore").split("\r\n")
        disposition = next(
            (h for h in headers if h.lower().startswith("content-disposition:")), ""
        )
        if "name=" not in disposition:
            continue

        name = _get_disposition_param(disposition, "name")
        filename = _get_disposition_param(disposition, "filename")

        if filename:
            files[name] = {"filename": filename, "content": content}
        else:
            fields[name] = content.decode(errors="ignore")

    return fields, files


def _get_disposition_param(disposition, key):
    # Extract key="value" from Content-Disposition header
    marker = f'{key}="'
    start = disposition.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = disposition.find('"', start)
    if end == -1:
        return None
    return disposition[start:end]


def run_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"ML Deployment Platform (Simplified) running on http://localhost:{port}")
    print("Documentation: http://localhost:8000")
    print("Use this simplified version to test the platform without additional dependencies")
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
