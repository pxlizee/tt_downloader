import os
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Vercel hanya mengizinkan tulis file di folder /tmp
DOWNLOAD_FOLDER = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    data = request.json
    tiktok_url = data.get('url')
    if not tiktok_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # Hindari butuh FFmpeg karena Vercel tidak punya FFmpeg bawaan
        'format': 'best[ext=mp4]/best', 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tiktok_url, download=False)
            return jsonify({
                'status': 'success',
                'title': info.get('title', 'Tiktok Video'),
                'thumbnail': info.get('thumbnail'),
                'original_url': tiktok_url 
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
def download_video():
    tiktok_url = request.args.get('url')
    
    if not tiktok_url:
        return "Error: URL missing", 400

    try:
        # Konfigurasi yt-dlp simpan ke /tmp
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(tiktok_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Pastikan path absolut
            abs_path = os.path.abspath(filename)
            
            # Kirim file lalu Vercel akan menghapusnya otomatis nanti
            return send_file(abs_path, as_attachment=True)

    except Exception as e:
        return f"Gagal (Mungkin Timeout Vercel 10s): {str(e)}", 500

# app.run() TIDAK PERLU DIJALANKAN DI VERCEL
# Vercel akan menjalankan 'app' secara otomatis
if __name__ == '__main__':
    app.run(debug=True)