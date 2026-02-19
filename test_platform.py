"""
Test script for the ML Deployment Platform
Run this to verify everything is working correctly
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_dependencies():
    """Test if all dependencies are installed"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "scikit-learn",
        "joblib",
        "pandas",
        "numpy"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def test_sample_model():
    """Test creating the sample model"""
    print("\n🔍 Testing sample model creation...")
    
    success, stdout, stderr = run_command(
        "python sample_model.py",
        cwd="models"
    )
    
    if success:
        print("✅ Sample model created successfully!")
        print(f"   {stdout.strip()}")
        
        # Check if model file exists
        model_path = Path("models/sample_iris_model.joblib")
        if model_path.exists():
            print(f"✅ Model file exists: {model_path}")
            return True
        else:
            print("❌ Model file not found")
            return False
    else:
        print("❌ Failed to create sample model")
        print(f"   Error: {stderr}")
        return False

def test_api_server():
    """Test starting the API server"""
    print("\n🔍 Testing API server...")
    
    # Start the server in background
    print("   Starting server (this may take a moment)...")
    proc = subprocess.Popen(
        [sys.executable, "app/main.py"],
        cwd=".",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test if server is running
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            print("✅ API server is running!")
            print(f"   Response: {response.json()['message']}")
            return True, proc
        else:
            print("❌ API server not responding correctly")
            return False, proc
    except Exception as e:
        print("❌ Failed to connect to API server")
        print(f"   Error: {e}")
        return False, proc

def test_api_endpoints(proc):
    """Test the API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    model_file = "models/sample_iris_model.joblib"
    
    # Test 1: Root endpoint
    print("   Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Root endpoint works")
        else:
            print("   ❌ Root endpoint failed")
            return False
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
        return False
    
    # Test 2: Upload model
    print("   Testing model upload...")
    try:
        with open(model_file, "rb") as f:
            files = {"file": ("iris_model.joblib", f)}
            data = {
                "name": "Test Iris Model",
                "framework": "scikit-learn",
                "description": "Test model for platform"
            }
            response = requests.post(
                f"{base_url}/models/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            print("   ✅ Model upload successful")
            model_info = response.json()["model_info"]
            model_id = model_info["model_id"]
            print(f"   Model ID: {model_id}")
        else:
            print(f"   ❌ Model upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Model upload error: {e}")
        return False
    
    # Test 3: List models
    print("   Testing list models...")
    try:
        response = requests.get(f"{base_url}/models")
        if response.status_code == 200:
            models = response.json()["models"]
            print(f"   ✅ Found {len(models)} model(s)")
        else:
            print("   ❌ List models failed")
            return False
    except Exception as e:
        print(f"   ❌ List models error: {e}")
        return False
    
    # Test 4: Make prediction
    print("   Testing prediction...")
    try:
        # Use the model_id from upload
        prediction_data = {
            "input_data": [[5.1, 3.5, 1.4, 0.2]]  # Sample iris features
        }
        response = requests.post(
            f"{base_url}/predict/{model_id}",
            json=prediction_data
        )
        
        if response.status_code == 200:
            prediction = response.json()["predictions"][0]
            print(f"   ✅ Prediction successful: {prediction}")
        else:
            print(f"   ❌ Prediction failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Prediction error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 ML Deployment Platform - Test Suite")
    print("=" * 50)
    
    # Change to project directory
    os.chdir("ml_deployment_platform")
    
    # Run tests
    tests = [
        ("Dependencies", test_dependencies),
        ("Sample Model", test_sample_model),
    ]
    
    results = []
    server_proc = None
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Test API server and endpoints
    try:
        server_ok, server_proc = test_api_server()
        results.append(("API Server", server_ok))
        
        if server_ok:
            endpoints_ok = test_api_endpoints(server_proc)
            results.append(("API Endpoints", endpoints_ok))
    except Exception as e:
        print(f"❌ API test crashed: {e}")
        results.append(("API Server", False))
        results.append(("API Endpoints", False))
    finally:
        if server_proc:
            server_proc.terminate()
            server_proc.wait()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your platform is working correctly.")
        print("\n🚀 Next steps:")
        print("1. Run: python app/main.py")
        print("2. Open: http://localhost:8000/docs")
        print("3. Upload your own models and test predictions!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Try:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check error messages for specific issues")
        print("3. Run tests again after fixing issues")

if __name__ == "__main__":
    main()