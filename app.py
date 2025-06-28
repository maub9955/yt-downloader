from flask import Flask, request, send_file, render_template_string
import subprocess, os

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
<meta charset="UTF-8"><title>YouTube Downloader MVP</title>
 <!-- 기본 SEO 메타 태그 -->
 <meta name="description" content="YouTube URL만 입력하면 WAV 오디오로 변환·다운로드해 주는 무료 웹앱입니다.">
 <meta name="keywords"    content="YouTube, 오디오 다운로드, WAV 변환, 무료 서비스">

 <!-- Open Graph 태그 (SNS 공유용) -->
 <meta property="og:title"       content="YouTube Audio Downloader">
 <meta property="og:description" content="URL만 입력하면 간편하게 WAV 오디오 파일을 다운로드하세요!">
 <meta property="og:image"       content="https://yt-downloader-zn0z.onrender.com/og-image.png">
 <meta property="og:url"         content="https://yt-downloader-zn0z.onrender.com/">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8180253907611579"
     crossorigin="anonymous"></script>
</head>
<body>
  <h1>YouTube 오디오 다운로드</h1>
  <form method="post">
    YouTube URL: <input name="url" size="50" placeholder="https://youtu.be/..." required>
    <button type="submit">다운로드</button>
  </form>
  
  <p style="color:gray; font-size:0.9em;">
    🙏 다운로드된 파일명은 영문·숫자·ID 기반으로 표시되며,
    한글이나 원본 제목과 다를 수 있습니다.
  </p>
  
  {% if filename %}
    <p>✅ 다운로드 준비 완료:</p>
    <!-- 광고 시청 버튼 -->
    <button id="watchAd" style="margin-top:0.5em;">▶ 광고 시청 후 다운로드</button>
    <!-- 실제 다운로드 링크 (초기엔 숨김) -->
    <div id="downloadContainer" style="display:none; margin-top:0.5em;">
      <a id="downloadLink" href="/download/{{filename}}">
        📥 다운로드 받기 ({{filename}})
      </a>
    </div>
    <!-- 광고 시청 시뮬레이션 스크립트 -->
    <script>
      document.getElementById('watchAd').addEventListener('click', function(){
        this.disabled = true;
        this.innerText = '광고 재생 중…';
        // 실제 광고 SDK 연동 시 이 부분을 대체하세요
        setTimeout(() => {
          document.getElementById('downloadContainer').style.display = 'block';
          this.style.display = 'none';
        }, 5000);  // 5초 후 다운로드 링크 노출
      });
    </script>
  {% endif %}
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
    return render_template_string(TEMPLATE, filename=filename)

@app.route('/download/<path:fname>')
def download(fname):
    path = os.path.join('downloads', fname)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
