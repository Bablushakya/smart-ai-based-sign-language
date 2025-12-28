# Website Packages Installation Guide

This file contains all Python packages installed in the `website/.venv` virtual environment.

## 📦 Total Packages: 66

## 🚀 Quick Installation

### Method 1: Install from requirements file (Recommended)
```bash
cd website
pip install -r requirements.txt
```

### Method 2: Install minimal packages only
```bash
cd website
pip install -r requirements-minimal.txt
```

### Method 3: Install all at once
```bash
pip install absl-py==2.3.1 astunparse==1.6.3 attrs==25.4.0 blinker==1.9.0 cachetools==6.2.1 certifi==2025.10.5 cffi==2.0.0 charset-normalizer==3.4.4 click==8.1.8 colorama==0.4.6 contourpy==1.3.2 cycler==0.12.1 Flask==2.3.3 flatbuffers==25.9.23 fonttools==4.60.1 gast==0.4.0 google-auth==2.43.0 google-auth-oauthlib==1.0.0 google-pasta==0.2.0 grpcio==1.74.0 gTTS==2.5.4 gunicorn==21.2.0 h5py==3.15.1 idna==3.11 itsdangerous==2.2.0 jax==0.4.38 jaxlib==0.4.38 Jinja2==3.1.6 keras==2.13.1 kiwisolver==1.4.9 libclang==18.1.1 Markdown==3.10 MarkupSafe==3.0.3 matplotlib==3.10.7 mediapipe==0.10.14 ml_dtypes==0.5.3 numpy==1.24.3 oauthlib==3.3.1 opencv-contrib-python==4.11.0.86 opencv-python==4.8.1.78 opt_einsum==3.4.0 packaging==25.0 pillow==12.0.0 protobuf==4.25.8 pyasn1==0.6.1 pyasn1_modules==0.4.2 pycparser==2.23 pygame==2.6.1 pyparsing==3.2.5 python-dateutil==2.9.0.post0 requests==2.32.5 requests-oauthlib==2.0.0 rsa==4.9.1 scipy==1.15.3 sounddevice==0.5.3 tensorboard==2.13.0 tensorboard-data-server==0.7.2 tensorflow==2.13.0 tensorflow-estimator==2.13.0 tensorflow-intel==2.13.0 tensorflow-io-gcs-filesystem==0.31.0 termcolor==3.2.0 typing_extensions==4.5.0 urllib3==2.5.0 Werkzeug==3.1.3 wrapt==2.0.0
```

## 📋 Core Packages by Category

### Web Framework
- **Flask==2.3.3** - Main web framework
- **gunicorn==21.2.0** - Production WSGI server
- **Werkzeug==3.1.3** - WSGI utility library
- **Jinja2==3.1.6** - Template engine

### Machine Learning & AI
- **tensorflow==2.13.0** - Main ML framework
- **tensorflow-intel==2.13.0** - Intel-optimized TensorFlow
- **keras==2.13.1** - High-level neural networks API
- **mediapipe==0.10.14** - Hand tracking and pose detection
- **tensorboard==2.13.0** - ML visualization toolkit

### Computer Vision
- **opencv-python==4.8.1.78** - Computer vision library
- **opencv-contrib-python==4.11.0.86** - OpenCV extra modules
- **pillow==12.0.0** - Image processing

### Data Processing
- **numpy==1.24.3** - Numerical computing
- **scipy==1.15.3** - Scientific computing
- **pandas** (via dependencies) - Data manipulation

### Audio & Text-to-Speech
- **gTTS==2.5.4** - Google Text-to-Speech
- **sounddevice==0.5.3** - Audio playback/recording
- **pygame==2.6.1** - Audio and game development

### Visualization
- **matplotlib==3.10.7** - Plotting library
- **tensorboard==2.13.0** - ML metrics visualization

### Utilities
- **requests==2.32.5** - HTTP library
- **python-dateutil==2.9.0.post0** - Date utilities
- **click==8.1.8** - CLI creation
- **colorama==0.4.6** - Terminal colors

## 🔧 Installation Steps

### Step 1: Navigate to Website Folder
```bash
cd website
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Step 4: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Step 5: Install Packages
```bash
pip install -r requirements.txt
```

## 📝 Minimal Installation (Recommended)

For just running the ASL Translator website:

```bash
cd website
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-minimal.txt
```

This installs only 20 essential packages (~1.2GB).

## 🎯 Core Packages Only

For absolute minimal setup:

```bash
pip install Flask tensorflow-intel mediapipe opencv-python numpy pillow gTTS requests
```

This installs only 8 core packages (~800MB).

## 🐛 Troubleshooting

### Issue: TensorFlow installation fails
**Solution:** 
```bash
pip install tensorflow-intel==2.13.0 --no-cache-dir
```

### Issue: OpenCV installation error
**Solution:**
```bash
pip install opencv-python==4.8.1.78 --no-cache-dir
```

### Issue: MediaPipe installation error
**Solution:**
```bash
pip install mediapipe==0.10.14 --no-cache-dir
```

### Issue: gTTS not working
**Solution:**
```bash
pip install gTTS==2.5.4 --upgrade
```

### Issue: Pygame audio issues
**Solution:**
```bash
pip install pygame==2.6.1 --upgrade
```

## 💾 Export Current Packages

To export your current packages:
```bash
cd website
pip freeze > requirements.txt
```

Or with versions:
```bash
pip list --format=freeze > packages.txt
```

## 🔄 Update All Packages

To update all packages to latest versions:
```bash
pip list --outdated
pip install --upgrade package_name
```

## 📊 Package Statistics

- **Total Packages**: 66
- **Core ML/AI**: 9
- **Web Framework**: 4
- **Computer Vision**: 3
- **Audio/TTS**: 3
- **Data Science**: 3
- **Utilities**: 10
- **Dependencies**: 34

## 📦 Package Sizes (Approximate)

- TensorFlow: ~500MB
- OpenCV: ~100MB
- MediaPipe: ~50MB
- NumPy: ~20MB
- Matplotlib: ~30MB
- Others: ~100MB

**Total Size: ~1.2-1.5GB**

## ⚠️ Important Notes

1. **Python Version**: Requires Python 3.11 or compatible
2. **Windows Specific**: Optimized for Windows with Intel CPU
3. **TensorFlow Intel**: Uses Intel-optimized version for better performance
4. **MediaPipe**: Version 0.10.14 for hand tracking
5. **Audio Support**: Includes gTTS and pygame for text-to-speech

## 🚀 Quick Start Commands

```bash
# Navigate to website folder
cd website

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install all packages
pip install -r requirements.txt

# Or install minimal packages
pip install -r requirements-minimal.txt

# Run the Flask application
python app.py
```

## 🎯 Production Deployment

For production deployment with Gunicorn:

```bash
# Install production requirements
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📋 Package Comparison

### Website Folder vs Root Folder

**Website Folder (66 packages):**
- Focused on web application
- Includes Flask and Gunicorn
- Has gTTS for text-to-speech
- Includes pygame for audio
- Smaller and faster to install

**Root Folder (200+ packages):**
- Includes Jupyter notebooks
- Has PyTorch in addition to TensorFlow
- More data science tools
- Development and testing tools
- Larger installation

## 🔒 Security Notes

- Keep packages updated regularly
- Use virtual environment to isolate dependencies
- Check for security vulnerabilities: `pip audit`
- Update pip regularly: `python -m pip install --upgrade pip`

## 📞 Support

If you encounter issues:
1. Check Python version: `python --version`
2. Ensure pip is updated: `python -m pip install --upgrade pip`
3. Try installing with `--no-cache-dir` flag
4. Check system requirements for TensorFlow
5. Verify virtual environment is activated

## 🎨 Features Enabled by Packages

- **Flask**: Web server and routing
- **TensorFlow + MediaPipe**: ASL sign recognition
- **OpenCV**: Camera feed processing
- **gTTS**: Text-to-speech functionality
- **NumPy**: Fast numerical operations
- **Pillow**: Image processing
- **Gunicorn**: Production server
- **Pygame**: Audio playback

## 📈 Performance Tips

1. Use TensorFlow-Intel for better CPU performance
2. Enable GPU support if available
3. Use Gunicorn with multiple workers in production
4. Cache model predictions when possible
5. Optimize image quality vs processing speed

## 🔄 Upgrade Guide

To upgrade to latest versions:

```bash
# Backup current requirements
cp requirements.txt requirements.backup.txt

# Upgrade all packages
pip list --outdated
pip install --upgrade package_name

# Export new requirements
pip freeze > requirements.txt
```

## ✅ Verification

After installation, verify key packages:

```bash
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import tensorflow; print('TensorFlow:', tensorflow.__version__)"
python -c "import mediapipe; print('MediaPipe:', mediapipe.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
```

All packages should import without errors.
