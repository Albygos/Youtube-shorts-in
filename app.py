import os
from flask import Flask, request, send_file, jsonify
from processor import process_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # send_file grabs the HTML directly from the same folder as app.py
    return send_file('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    start_time = int(request.form.get('start_time', 0))
    duration = int(request.form.get('duration', 30))

    if not url:
        return jsonify({"error": "Please provide a YouTube URL"}), 400

    try:
        output_path = process_video(url, start_time, duration, app.config['UPLOAD_FOLDER'])
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
