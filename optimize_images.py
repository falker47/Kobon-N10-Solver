import os
import shutil
from PIL import Image

# Disable decompression bomb error
Image.MAX_IMAGE_PIXELS = None

IMAGE_DIR = r"c:\Users\Falker\Desktop\Code\Kobon Triangle\images"
BACKUP_DIR = os.path.join(IMAGE_DIR, "originals")

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def optimize_images():
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg')) and 'originals' not in filename:
            src_path = os.path.join(IMAGE_DIR, filename)
            # Backup exists from previous run, that's fine.
            
            try:
                with Image.open(src_path) as img:
                    # Resize logic
                    max_size = (1600, 1600) # Ensure it's large enough to be readable but small file
                    if img.width > max_size[0] or img.height > max_size[1]:
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    img.save(src_path, "JPEG", quality=75, optimize=True)
                    print(f"Optimized JPEG: {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    optimize_images()
