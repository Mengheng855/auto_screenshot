from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import base64
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

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
        filepath = output_dir / filename
        
        # Save file to your folder
        with open(filepath, 'wb') as f:
            f.write(photo_bytes)
        
        # Create photo URL
        photo_url = f"/photos/{filename}"
        
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
        
        print(f"✓ Photo saved: {filepath}")
        print(f"✓ Photo URL: {photo_url}")
        
        return jsonify({
            'status': 'ok', 
            'filename': filename,
            'url': photo_url
        }), 200
    
    except Exception as e:
        print(f"✗ Error saving photo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/photos/<filename>')
def get_photo(filename):
    try:
        filepath = output_dir / filename
        if filepath.exists():
            return send_file(filepath, mimetype='image/png')
        return jsonify({'error': 'Photo not found'}), 404
    except Exception as e:
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