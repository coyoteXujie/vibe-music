import json
import os
import platform
import subprocess
import sys
import threading
import time
import webview
from flask import Flask, jsonify, request, send_from_directory

from music_api import MusicAPI
from player import Player


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def external_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


NCM_DIR = external_path("ncm-api")
ncm_process = None


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


def find_node():
    system = platform.system()
    if system == "Windows":
        for p in ["D:\\nodejs\\node.exe", "C:\\Program Files\\nodejs\\node.exe"]:
            if os.path.isfile(p):
                return p
        try:
            result = subprocess.run(["where", "node"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
    else:
        try:
            result = subprocess.run(["which", "node"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
    return None


def start_ncm_api():
    global ncm_process
    node_path = find_node()
    if not node_path:
        print("[WARN] 未找到 Node.js，NCM API 无法启动")
        return False
    server_js = os.path.join(NCM_DIR, "server.js")
    if not os.path.isfile(server_js):
        print("[WARN] 未找到 ncm-api/server.js")
        return False
    try:
        ncm_process = subprocess.Popen(
            [node_path, server_js],
            cwd=NCM_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[INFO] NCM API 正在启动...")
        for _ in range(15):
            time.sleep(1)
            try:
                import requests
                r = requests.get("http://127.0.0.1:52401/search", params={"keywords": "test", "limit": 1}, timeout=3)
                if r.status_code == 200:
                    print("[INFO] NCM API 已就绪 (port 52401)")
                    return True
            except Exception:
                pass
        print("[WARN] NCM API 启动超时")
        return False
    except Exception as e:
        print(f"[WARN] NCM API 启动失败: {e}")
        return False

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
    page = data.get("page", 1)
    limit = data.get("limit", 30)
    if not keyword:
        return jsonify({"code": 400, "msg": "关键词不能为空"})
    result = music_api.search(keyword, page=page, limit=limit)
    return jsonify(result)


@app.route("/api/song_url", methods=["POST"])
def song_url():
    data = request.json or {}
    song_id = data.get("id")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID"})
    result = music_api.get_song_url(song_id)
    return jsonify(result)


@app.route("/api/song_detail", methods=["POST"])
def song_detail():
    data = request.json or {}
    song_id = data.get("id")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID"})
    result = music_api.get_song_detail(song_id)
    return jsonify(result)


@app.route("/api/lyric", methods=["POST"])
def lyric():
    data = request.json or {}
    song_id = data.get("id")
    if not song_id:
        return jsonify({"code": 400, "msg": "缺少歌曲ID"})
    result = music_api.get_lyric(song_id)
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
    if url:
        player.play_url(url, {
            "id": song_id, "title": title, "artist": artist,
            "album": album, "duration": duration
        })
        return jsonify({"code": 200, "msg": "播放中"})
    if song_id:
        result = music_api.get_song_url(song_id)
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


@app.route("/api/playlist/recommend", methods=["GET"])
def playlist_recommend():
    result = music_api.get_recommend_playlists()
    return jsonify(result)


@app.route("/api/playlist/detail", methods=["POST"])
def playlist_detail():
    data = request.json or {}
    playlist_id = data.get("id")
    if not playlist_id:
        return jsonify({"code": 400, "msg": "缺少歌单ID"})
    result = music_api.get_playlist_detail(playlist_id)
    return jsonify(result)


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


def run_server():
    app.run(host="127.0.0.1", port=52400, threaded=True)


def main():
    start_ncm_api()
    music_api._check_ncm()
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
    if ncm_process:
        ncm_process.terminate()


if __name__ == "__main__":
    main()
