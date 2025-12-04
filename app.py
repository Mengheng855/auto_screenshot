from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import base64
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Create output directory
output_dir = Path('face_captures')
output_dir.mkdir(exist_ok=True)

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
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(photo_bytes)
        
        print(f"✓ Photo saved: {filepath}")
        return jsonify({'status': 'ok', 'filename': filename}), 200
    
    except Exception as e:
        print(f"✗ Error saving photo: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)