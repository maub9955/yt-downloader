from flask import Flask, request, send_file, render_template_string
import subprocess, os
from datetime import datetime, timedelta
# 마지막 다운로드 처리 시각 (컨테이너 전체 공유)
last_download_time: datetime = datetime.min
# 요청 간 최소 간격 (예: 60초)
DOWNLOAD_INTERVAL = timedelta(seconds=60)
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
      {% if error %}
  <div class="alert alert-warning text-center" role="alert">
    {{ error }}
  </div>
{% endif %}
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
    global last_download_time
    now = datetime.now()

    # 1분 이내 중복 요청 방지
    if now - last_download_time < DOWNLOAD_INTERVAL:
        wait = int((DOWNLOAD_INTERVAL - (now - last_download_time)).total_seconds())
        error = f"🙏 너무 빠른 요청입니다. {wait}초 후에 다시 시도해 주세요."
        return render_template_string(
            TEMPLATE,
            filename=None,
            error=error,
            current_year=datetime.now().year
        )

    filename = None
    error = None

    if request.method == 'POST':
        # 요청 허용, 타임스탬프 업데이트
        last_download_time = now

        url = request.form['url']
        os.makedirs('downloads', exist_ok=True)
        cmd = [
            'yt-dlp',
            '-x', '--audio-format', 'wav',
            '-o', 'downloads/%(id)s.%(ext)s',
            url
        ]
        try:
            subprocess.run(cmd, check=True)
            video_id = subprocess.check_output(
                ['yt-dlp', '--get-id', url]
            ).decode().strip()
            filename = f"{video_id}.wav"
        except subprocess.CalledProcessError:
            error = "😢 현재 다운로드가 불가능합니다. 잠시 후 다시 시도해주세요."

    return render_template_string(
        TEMPLATE,
        filename=filename,
        error=error,
        current_year=datetime.now().year
    )

@app.route('/download/<path:fname>')
def download(fname):
    path = os.path.join('downloads', fname)
    return send_file(path, as_attachment=True)
