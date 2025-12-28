import importlib.util
import sys

def check_package(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ {package_name} is not installed")
        return False
    else:
        print(f"✅ {package_name} is installed")
        return True

def main():
    required_packages = [
        'cv2',
        'numpy',
        'mediapipe',
        'tensorflow',
        'keras'
    ]
    
    print("Checking required packages...")
    all_installed = True
    
    for package in required_packages:
        if not check_package(package):
            all_installed = False
    
    if all_installed:
        print("\n🎉 All required packages are installed!")
        print("\nYou can now run:")
        print("1. data_collection_raw.py - for raw images")
        print("2. data_collection_mediapipe.py - for MediaPipe images")
    else:
        print("\n❌ Some packages are missing. Please install them using:")
        print("pip install opencv-python numpy mediapipe tensorflow")

if __name__ == "__main__":
    main()