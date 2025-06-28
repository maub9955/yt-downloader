from flask import Flask, request, send_file, render_template_string
import subprocess, os
from datetime import datetime

app = Flask(__name__)

@app.route('/robots.txt')
def robots():
    return send_file('robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    return send_file('sitemap.xml', mimetype='application/xml')
    
# Google site verification file 제공
@app.route('/googlec2c80d80434062e7.html')
def google_verify():
    return send_file('googlec2c80d80434062e7.html', mimetype='text/html')

# 간단한 HTML 템플릿
TEMPLATE = '''
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>YouTube Audio Downloader</title>
  <!-- Bootstrap CSS -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-ENjdO4Dr2bkBIFxQpeoghbPvzkgIJ6q+...省略..." crossorigin="anonymous">
  <!-- Custom Styles -->
  <style>
    body { background: #f8f9fa; }
    .card { max-width: 540px; margin: 4rem auto; border: none; border-radius: .75rem; }
    .btn-download { width: 100%; }
    footer { text-align: center; padding: 2rem 0; color: #6c757d; }
  </style>
</head>
<body>
  <div class="card shadow-sm">
    <div class="card-body">
      <h1 class="card-title text-center mb-4">YouTube Audio Downloader</h1>
      <form method="post" class="d-flex gap-2 mb-3">
        <input name="url" type="url" class="form-control" placeholder="https://youtu.be/…" required>
        <button type="submit" class="btn btn-primary btn-download">다운로드</button>
      </form>
      <p class="text-muted small mb-4 text-center">
        🙏 파일명은 영문·숫자·ID 기반으로 표시됩니다.
      </p>
      {% if filename %}
        <div class="alert alert-success text-center" role="alert">
          다운로드 준비 완료!
        </div>
        <div class="d-grid">
          <a href="/download/{{filename}}" class="btn btn-success">📥 {{filename}} 받기</a>
        </div>
      {% endif %}
    </div>
  </div>
  <footer>
    &copy; {{current_year}} YourCompany. All rights reserved.
  </footer>
  <!-- Optional Bootstrap JS (for future) -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
          integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+…省略…" crossorigin="anonymous"></script>
</body>
</html>
'''


@app.route('/', methods=['GET','POST'])
def index():
    filename = None
    if request.method == 'POST':
        url = request.form['url']
        os.makedirs('downloads', exist_ok=True)
        # yt-dlp 호출: 오디오만 wav 포맷으로 저장, ID 기반 파일명
        cmd = [
            'yt-dlp',
            '-x', '--audio-format', 'wav',
            '-o', 'downloads/%(id)s.%(ext)s',
            url
        ]
        subprocess.run(cmd, check=True)
        video_id = subprocess.check_output(['yt-dlp','--get-id', url]).decode().strip()
        filename = f"{video_id}.wav"
    return render_template_string(
        TEMPLATE,
        filename=filename,
        current_year=datetime.now().year
    )
@app.route('/download/<path:fname>')
def download(fname):
    path = os.path.join('downloads', fname)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
