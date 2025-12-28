# Package Comparison: Root vs Website Folder

## 📊 Overview

| Aspect | Root Folder | Website Folder |
|--------|-------------|----------------|
| **Total Packages** | 200+ | 66 |
| **Installation Size** | ~2-3 GB | ~1.2-1.5 GB |
| **Purpose** | Development & Research | Production Web App |
| **Install Time** | ~15-20 min | ~8-10 min |

## 📦 Package Breakdown

### Root Folder (.venv) - 200+ Packages

**Includes:**
- ✅ Flask + FastAPI (dual web frameworks)
- ✅ TensorFlow + PyTorch (dual ML frameworks)
- ✅ Jupyter Lab + Notebooks (development environment)
- ✅ Extensive data science tools
- ✅ Multiple visualization libraries
- ✅ Development and testing tools
- ✅ Kaggle integration
- ✅ Comet ML for experiment tracking

**Best For:**
- Machine learning research
- Model development and training
- Data analysis and visualization
- Jupyter notebook experiments
- Testing multiple frameworks

### Website Folder (website/.venv) - 66 Packages

**Includes:**
- ✅ Flask (web framework)
- ✅ TensorFlow only (focused ML)
- ✅ MediaPipe (hand tracking)
- ✅ OpenCV (computer vision)
- ✅ gTTS (text-to-speech)
- ✅ Gunicorn (production server)
- ✅ Essential utilities only

**Best For:**
- Running the web application
- Production deployment
- Faster installation
- Minimal dependencies
- Focused functionality

## 🎯 Key Differences

### Machine Learning Frameworks

**Root Folder:**
```
- TensorFlow 2.13.0
- PyTorch 2.8.0
- TorchVision 0.23.0
- TorchAudio 2.8.0
- JAX 0.7.1
```

**Website Folder:**
```
- TensorFlow 2.13.0
- TensorFlow-Intel 2.13.0
- Keras 2.13.1
- JAX 0.4.38
```

### Web Frameworks

**Root Folder:**
```
- Flask 2.3.3
- FastAPI 0.116.1
- Uvicorn 0.35.0
```

**Website Folder:**
```
- Flask 2.3.3
- Gunicorn 21.2.0
```

### Development Tools

**Root Folder:**
```
- JupyterLab 4.4.7
- Notebook 7.4.5
- IPython 9.5.0
- Kaggle 1.7.4.5
- Comet ML 3.52.1
```

**Website Folder:**
```
- None (production-focused)
```

### Audio/TTS

**Root Folder:**
```
- pyttsx3 2.90
- sounddevice 0.5.2
```

**Website Folder:**
```
- gTTS 2.5.4
- sounddevice 0.5.3
- pygame 2.6.1
```

## 📋 Installation Commands

### Root Folder Installation
```bash
# Full installation (200+ packages)
pip install -r requirements.txt

# Minimal installation (core packages)
pip install -r requirements-minimal.txt
```

### Website Folder Installation
```bash
# Navigate to website folder
cd website

# Full installation (66 packages)
pip install -r requirements.txt

# Minimal installation (20 packages)
pip install -r requirements-minimal.txt
```

## 🚀 Quick Start Comparison

### Root Folder Quick Start
```bash
# Create environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Run Jupyter or development
jupyter lab
```

### Website Folder Quick Start
```bash
# Navigate and create environment
cd website
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt

# Run web application
python app.py
```

## 💡 Recommendations

### Use Root Folder When:
- Developing new ML models
- Training and experimenting
- Using Jupyter notebooks
- Comparing PyTorch vs TensorFlow
- Doing data analysis
- Need full development environment

### Use Website Folder When:
- Running the web application
- Production deployment
- Want faster installation
- Need minimal dependencies
- Deploying to server
- Limited disk space

## 📊 Detailed Package Lists

### Unique to Root Folder (Not in Website)
- PyTorch ecosystem (torch, torchvision, torchaudio)
- Jupyter ecosystem (jupyterlab, notebook, ipython)
- FastAPI and Uvicorn
- Kaggle integration
- Comet ML
- Extensive data science tools
- Development utilities

### Unique to Website Folder (Not in Root)
- Gunicorn (production server)
- pygame (audio playback)
- Newer versions of some packages

### Common to Both
- Flask
- TensorFlow
- MediaPipe
- OpenCV
- NumPy
- Pillow
- Requests
- Basic utilities

## 🎯 Which Should You Use?

### For Development:
```bash
# Use root folder
cd /path/to/project
.venv\Scripts\Activate.ps1
```

### For Production:
```bash
# Use website folder
cd /path/to/project/website
.venv\Scripts\Activate.ps1
```

### For Both:
You can maintain both environments:
- Root folder for development
- Website folder for production

## 📦 Installation Time Comparison

**Root Folder:**
- Download: ~10-15 minutes
- Install: ~5-10 minutes
- Total: ~15-25 minutes

**Website Folder:**
- Download: ~5-8 minutes
- Install: ~3-5 minutes
- Total: ~8-13 minutes

## 💾 Disk Space Comparison

**Root Folder:**
- Packages: ~2.5 GB
- Cache: ~500 MB
- Total: ~3 GB

**Website Folder:**
- Packages: ~1.2 GB
- Cache: ~300 MB
- Total: ~1.5 GB

## 🔄 Synchronization

To keep both environments in sync:

```bash
# Export from root
pip freeze > requirements-root.txt

# Export from website
cd website
pip freeze > requirements-website.txt

# Compare
diff requirements-root.txt website/requirements-website.txt
```

## ✅ Verification Commands

### Root Folder Verification
```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import jupyter; print('Jupyter installed')"
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
```

### Website Folder Verification
```bash
cd website
python -c "import gunicorn; print('Gunicorn installed')"
python -c "import gtts; print('gTTS installed')"
python -c "import pygame; print('Pygame installed')"
```

## 📞 Support

Choose the right environment for your needs:
- **Development**: Use root folder
- **Production**: Use website folder
- **Both**: Maintain separate environments

Both environments are fully documented and ready to use!
