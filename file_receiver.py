# server.py
from flask import Flask, request, send_from_directory, jsonify, render_template_string
from pathlib import Path
import werkzeug

app = Flask(__name__)

SAVE_DIR = Path.home() / "moment"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def index():
    return "Server OK. Try /files for listing.", 200

@app.get("/files")
def list_files():
    files = sorted([p.name for p in SAVE_DIR.iterdir() if p.is_file()])
    html = """
    <h2>Saved files in ~/moment</h2>
    <ul>
    {% for f in files %}
      <li><a href="/download/{{f}}">{{f}}</a></li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, files=files)

@app.get("/download/<path:filename>")
def download(filename):
    # 安全起见，只允许目录内文件
    safe_name = werkzeug.utils.secure_filename(filename)
    return send_from_directory(SAVE_DIR, safe_name, as_attachment=False)

@app.post("/upload")
def upload():
    # 取 ?name=xxx.ext
    name = request.args.get("name", "")
    if not name:
        return "missing ?name=...", 400
    safe_name = werkzeug.utils.secure_filename(name)

    data = request.get_data(cache=False, as_text=False)
    if not data:
        return "empty body", 400

    (SAVE_DIR / safe_name).write_bytes(data)
    return "OK", 200

if __name__ == "__main__":
    # 用 0.0.0.0 监听，别用 127.0.0.1
    app.run(host="0.0.0.0", port=8888, debug=False)
