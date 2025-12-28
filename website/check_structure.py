import os

def check_project_structure():
    base_dir = "."
    
    required_dirs = [
        "static/css",
        "static/js", 
        "static/assets/images",
        "static/assets/videos/alphabet",
        "templates"
    ]
    
    required_files = [
        "app.py",
        "requirements.txt",
        "templates/base.html",
        "templates/home.html", 
        "templates/translate.html",
        "templates/learn.html",
        "templates/about.html",
        "templates/contact.html",
        "static/css/base.css",
        "static/css/animations.css",
        "static/css/home.css",
        "static/css/translate.css", 
        "static/css/learn.css",
        "static/css/about.css",
        "static/css/contact.css",
        "static/js/utils.js",
        "static/js/camera.js",
        "static/js/home.js",
        "static/js/translate.js",
        "static/js/learn.js",
        "static/js/about.js",
        "static/js/contact.js"
    ]
    
    print("🔍 Checking project structure...")
    
    # Check directories
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Missing directory: {dir_path}")
            os.makedirs(full_path, exist_ok=True)
            print(f"   Created: {dir_path}")
    
    # Check files
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
    
    print("\n📋 Structure check completed!")

if __name__ == "__main__":
    check_project_structure()