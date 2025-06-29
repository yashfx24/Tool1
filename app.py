from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from utils.video_processor import process_video
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    # Get form data
    youtube_url = request.form.get('youtube_url')
    languages = request.form.getlist('languages')
    generate_subtitles = 'subtitles' in request.form
    generate_dubbed = 'dubbed-audio' in request.form
    preserve_original = 'preserve-original' in request.form

    # Validate input
    if not youtube_url:
        return jsonify({'error': 'Please enter a YouTube URL'}), 400
    if not languages:
        return jsonify({'error': 'Please select at least one language'}), 400

    # Create unique job ID
    job_id = str(uuid.uuid4())
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    os.makedirs(output_dir, exist_ok=True)

    # Start processing (in a real app, this would be a background task)
    try:
        results = process_video(
            youtube_url,
            languages,
            output_dir,
            generate_subtitles,
            generate_dubbed,
            preserve_original
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'job_id': job_id,
        'results': results
    })

@app.route('/download/<job_id>/<filename>')
def download(job_id, filename):
    directory = os.path.join(app.config['OUTPUT_FOLDER'], job_id)
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
