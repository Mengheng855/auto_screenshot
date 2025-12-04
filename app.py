from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import base64
from pathlib import Path
from datetime import datetime
import json
import cloudinary
import cloudinary.uploader
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Cloudinary
cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
api_secret = os.getenv('CLOUDINARY_API_SECRET')

if not cloud_name or not api_key or not api_secret:
    print("⚠️  WARNING: Cloudinary credentials not found!")
    print(f"CLOUDINARY_CLOUD_NAME: {cloud_name}")
    print(f"CLOUDINARY_API_KEY: {api_key}")
    print(f"CLOUDINARY_API_SECRET: {api_secret}")

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

# Create output directory
output_dir = Path('face_captures')
output_dir.mkdir(exist_ok=True)

# Photos list file
photos_list_file = Path('photos.json')

@app.route('/')
def index():
    return render_template('photo.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/save-photo', methods=['POST'])
def save_photo():
    try:
        data = request.json
        photo_data = data.get('photo')
        
        if not photo_data:
            return jsonify({'error': 'No photo data'}), 400
        
        # Remove data:image/png;base64, prefix
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        # Decode base64
        photo_bytes = base64.b64decode(photo_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.png"
        
        # Upload to Cloudinary
        print(f"⏳ Uploading to Cloudinary...")
        
        result = cloudinary.uploader.upload(
            BytesIO(photo_bytes),
            resource_type='image',
            public_id=f"photos/{timestamp}",
            overwrite=True
        )
        
        # Get the secure URL
        photo_url = result['secure_url']
        
        print(f"✓ Photo uploaded to Cloudinary: {photo_url}")
        
        # Add to photos list
        try:
            if photos_list_file.exists():
                with open(photos_list_file, 'r') as f:
                    photos = json.load(f)
            else:
                photos = []
        except:
            photos = []
        
        photos.append({
            'filename': filename,
            'url': photo_url,
            'timestamp': timestamp
        })
        
        # Save updated list
        with open(photos_list_file, 'w') as f:
            json.dump(photos, f, indent=2)
        
        print(f"✓ Photo saved to gallery: {filename}")
        
        return jsonify({
            'status': 'ok', 
            'filename': filename,
            'url': photo_url
        }), 200
    
    except Exception as e:
        print(f"✗ Error saving photo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/photos')
def list_photos():
    try:
        if photos_list_file.exists():
            with open(photos_list_file, 'r') as f:
                photos = json.load(f)
        else:
            photos = []
        return jsonify({'photos': photos}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)