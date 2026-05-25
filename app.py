import json
import os
import sys
import threading
import time
import webview
from flask import Flask, jsonify, request, send_from_directory, Response
import requests as http_requests

from music_api import MusicAPI
from player import Player

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


class WindowAPI:
    def minimize(self):
        webview.windows()[0].minimize()

    def maximize(self):
        w = webview.windows()[0]
        if not w.maximized:
            w.maximize()
        else:
            w.restore()

    def toggle_fullscreen(self):
        webview.windows()[0].toggle_fullscreen()

    def close(self):
        webview.windows()[0].destroy()

    def _drag_delta(self, dx, dy):
        w = webview.windows()[0]
        x, y = w.x + dx, w.y + dy
        w.move(x, y)


app = Flask(__name__, static_folder=resource_path("ui"), static_url_path="")

music_api = MusicAPI()
player = Player()


@app.route("/")
def index():
    return send_from_directory(resource_path("ui"), "index.html")


@app.route("/api/search", methods=["POST"])
def search():
    data = request.json or {}
    keyword = data.get("keyword", "")
    limit = data.get("limit", 30)
    if not keyword:
        return jsonify({"code": 400, "msg": "关键词不能为空"})
    result = music_api.search(keyword, limit=limit)
    return jsonify(result)


@app.route("/api/song_url", methods=["POST"])
def song_url():
    data = request.json or {}
    song_id = data.get("id")
    source = data.get("source")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID"})
    result = music_api.get_song_url(song_id, source=source)
    return jsonify(result)


@app.route("/api/song_detail", methods=["POST"])
def song_detail():
    data = request.json or {}
    song_id = data.get("id")
    source = data.get("source")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID"})
    result = music_api.get_song_detail(song_id, source=source)
    return jsonify(result)


@app.route("/api/lyric", methods=["POST"])
def lyric():
    data = request.json or {}
    song_id = data.get("id")
    source = data.get("source")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID"})
    result = music_api.get_lyric(song_id, source=source)
    return jsonify(result)


@app.route("/api/play", methods=["POST"])
def play():
    data = request.json or {}
    song_id = data.get("id")
    url = data.get("url")
    title = data.get("title", "")
    artist = data.get("artist", "")
    album = data.get("album", "")
    duration = data.get("duration", 0)
    source = data.get("source")
    if url:
        player.play_url(url, {
            "id": song_id, "title": title, "artist": artist,
            "album": album, "duration": duration
        })
        return jsonify({"code": 200, "msg": "播放中"})
    if song_id:
        result = music_api.get_song_url(song_id, source=source)
        if result.get("code") == 200 and result.get("url"):
            player.play_url(result["url"], {
                "id": song_id, "title": title, "artist": artist,
                "album": album, "duration": duration
            })
            return jsonify({"code": 200, "msg": "播放中"})
    return jsonify({"code": 400, "msg": "无法获取播放链接"})


@app.route("/api/pause", methods=["POST"])
def pause():
    player.pause()
    return jsonify({"code": 200, "msg": "已暂停"})


@app.route("/api/resume", methods=["POST"])
def resume():
    player.resume()
    return jsonify({"code": 200, "msg": "已恢复"})


@app.route("/api/stop", methods=["POST"])
def stop():
    player.stop()
    return jsonify({"code": 200, "msg": "已停止"})


@app.route("/api/set_volume", methods=["POST"])
def set_volume():
    data = request.json or {}
    volume = data.get("volume", 80)
    player.set_volume(int(volume))
    return jsonify({"code": 200, "msg": f"音量设为 {volume}%"})


@app.route("/api/seek", methods=["POST"])
def seek():
    data = request.json or {}
    position = data.get("position", 0)
    player.seek(float(position))
    return jsonify({"code": 200, "msg": f"跳转到 {position}s"})


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(player.get_status())


@app.route("/api/proxy_audio", methods=["GET"])
def proxy_audio():
    url = request.args.get("url", "")
    if not url or not url.startswith("http"):
        return jsonify({"code": 400, "msg": "无效的音频URL"})
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": url.split("/")[0] + "//" + url.split("/")[2] + "/",
        }
        resp = http_requests.get(url, headers=headers, stream=True, timeout=30)
        content_type = resp.headers.get("Content-Type", "audio/mpeg")
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        return Response(generate(), content_type=content_type, headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=300",
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})


@app.route("/api/danmaku", methods=["POST"])
def danmaku():
    data = request.json or {}
    song_id = data.get("id")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID", "comments": []})
    result = music_api.get_comments(song_id, limit=30)
    return jsonify(result)


@app.route("/api/top_songs", methods=["GET"])
def top_songs():
    result = music_api.get_top_songs()
    return jsonify(result)


@app.route("/api/system_info", methods=["GET"])
def system_info():
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0)
        return jsonify({
            "code": 200,
            "mem_total": round(mem.total / (1024**3), 1),
            "mem_used": round(mem.used / (1024**3), 1),
            "mem_pct": mem.percent,
            "cpu_pct": cpu,
        })
    return jsonify({"code": 200, "mem_total": 0, "mem_used": 0, "mem_pct": 0, "cpu_pct": 0})


def run_server():
    app.run(host="127.0.0.1", port=52400, threaded=True)


def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    window = webview.create_window(
        "氛围音乐 // 像素终端",
        "http://127.0.0.1:52400",
        width=1280,
        height=760,
        min_size=(1024, 680),
        resizable=True,
        frameless=True,
        js_api=WindowAPI(),
        text_select=False,
    )
    webview.start(debug=False, http_server=True)


if __name__ == "__main__":
    main()
