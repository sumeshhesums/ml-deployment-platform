#!/bin/bash
# Commands to push to GitHub

# 1. Initialize git (if not already initialized)
git init

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "Initial commit: Production-ready ML Deployment Platform

Features:
- FastAPI backend with PostgreSQL
- JWT Authentication (register, login, refresh tokens)
- Role-based access (admin/user)
- Model versioning & prediction history
- React + Vite + Tailwind frontend
- Docker & Docker Compose
- GitHub Actions CI/CD
- Deployment guides (Render, Railway, AWS, GCP)"

# 4. Create main branch
git branch -M main

# 5. Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ml-deployment-platform.git

# 6. Push to GitHub
git push -u origin main

# For subsequent commits:
# git add .
# git commit -m "Your message"
# git push
