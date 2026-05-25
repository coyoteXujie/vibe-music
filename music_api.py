import ast
import json
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_NODE_DIRS = ["D:\\nodejs", "C:\\Program Files\\nodejs", "/usr/local/bin", "/usr/bin"]
for _d in _NODE_DIRS:
    _node_exe = os.path.join(_d, "node.exe" if sys.platform == "win32" else "node")
    if os.path.isfile(_node_exe):
        os.environ["PATH"] = _d + os.pathsep + os.environ.get("PATH", "")
        break

from musicapi.musicapi import MusicApi_kugou, MusicApi_wyy

HAS_KUWO = False
try:
    from musicapi.musicapi import MusicApi_kuwo
    MusicApi_kuwo("")
    HAS_KUWO = True
except Exception:
    pass

HAS_QQ = False
try:
    from musicapi.musicapi import MusicApi_qq
    HAS_QQ = True
except Exception:
    pass

DEFAULT_HOST = "http://127.0.0.1:52400"

_KUWO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.kuwo.cn/",
}

_KUGOU_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}


class MusicAPI:
    def __init__(self):
        self.source = "kugou"

    def search(self, keyword, limit=10):
        try:
            url = f"http://mobilecdn.kugou.com/api/v3/search/song?keyword={keyword}&page=1&pagesize={limit}"
            ret = requests.get(url, headers=_KUGOU_HEADERS, timeout=10).json()
            songs = []
            for i in ret.get("data", {}).get("info", []):
                song_id = i.get("hash", "")
                songs.append({
                    "id": song_id,
                    "title": i.get("songname", ""),
                    "artist": i.get("singername", ""),
                    "album": i.get("album_name", ""),
                    "duration": i.get("duration", 0),
                    "source": "kugou",
                    "cover": "",
                })
            if songs:
                return {"code": 200, "songs": songs}
        except Exception:
            pass

        return {"code": 404, "msg": "未找到相关歌曲"}

    def _get_kuwo_url_simple(self, song_id):
        try:
            url = f"https://mobi.kuwo.cn/mobi.s?f=web&source=jiakong&type=convert_url_with_sign&rid={song_id}&br=320kmp3"
            ret = requests.get(url, headers=_KUWO_HEADERS, timeout=10).json()
            play_url = ret.get("data", {}).get("url", "")
            if play_url and play_url.startswith("http"):
                return play_url
        except Exception:
            pass
        return None

    def _search_kuwo_by_name(self, title, artist, limit=3):
        try:
            import urllib.parse
            query = urllib.parse.quote(f"{title} {artist}")
            url = f"https://search.kuwo.cn/r.s?all={query}&ft=music&pn=0&rn={limit}&rformat=json&encoding=utf8"
            ret = requests.get(url, headers=_KUWO_HEADERS, timeout=10)
            data = ast.literal_eval(ret.text)
            songs = []
            for i in data.get("abslist", []):
                sid = i.get("MUSICRID", "").replace("MUSIC_", "")
                name = i.get("SONGNAME", "").replace("&nbsp;", " ")
                art = i.get("ARTIST", "").replace("&nbsp;", " ")
                dur = int(i.get("DURATION", 0))
                pic = i.get("hts_MVPIC", "").replace("&nbsp;", " ")
                songs.append({"id": sid, "title": name, "artist": art, "duration": dur, "cover": pic})
            return songs
        except Exception:
            return []

    def get_song_url(self, song_id, source=None):
        source = source or self.source

        if source == "kugou":
            try:
                api = MusicApi_kugou(song_id, HOST=DEFAULT_HOST)
                url = api.get_kugou_url(song_id)
                if url and isinstance(url, str) and url.startswith("http"):
                    return {"code": 200, "url": url}
            except Exception:
                pass

            title, artist = self._get_kugou_song_name(song_id)
            kuwo_songs = self._search_kuwo_by_name(title, artist)
            if kuwo_songs:
                kuwo_url = self._get_kuwo_url_simple(kuwo_songs[0]["id"])
                if kuwo_url:
                    return {"code": 200, "url": kuwo_url, "source": "kuwo", "kuwo_id": kuwo_songs[0]["id"]}

        elif source == "kuwo":
            url = self._get_kuwo_url_simple(song_id)
            if url:
                return {"code": 200, "url": url}
            if HAS_KUWO:
                try:
                    api = MusicApi_kuwo("")
                    url = api.get_kuwo_url(song_id)
                    if url and isinstance(url, str) and url.startswith("http"):
                        return {"code": 200, "url": url}
                except Exception:
                    pass

        elif source == "wyy":
            try:
                api = MusicApi_wyy("")
                url = api.get_wyy_url(song_id)
                if url and isinstance(url, str) and url.startswith("http"):
                    return {"code": 200, "url": url}
            except Exception:
                pass

        elif source == "qq" and HAS_QQ:
            try:
                api = MusicApi_qq("")
                url = api.get_qq_url(song_id)
                if url and isinstance(url, str) and url.startswith("http"):
                    return {"code": 200, "url": url}
            except Exception:
                pass

        return {"code": 404, "msg": "无法获取播放链接，可能需要VIP"}

    def _get_kugou_song_name(self, kugou_hash):
        try:
            url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={kugou_hash}"
            ret = requests.get(url, headers=_KUGOU_HEADERS, timeout=10).json()
            title = ret.get("songName", "")
            artist = ret.get("author_name", "")
            if title:
                return title, artist
        except Exception:
            pass
        return "", ""

    def get_song_detail(self, song_id, source=None):
        source = source or self.source
        try:
            if source == "kugou":
                url = f"http://m.kugou.com/app/i/getSongInfo.php?cmd=playInfo&hash={song_id}"
                ret = requests.get(url, headers=_KUGOU_HEADERS, timeout=10).json()
                cover = ret.get("album_img", "").replace("/{size}", "")
                if cover:
                    return {"code": 200, "cover": cover}
            elif source == "kuwo":
                url = f"https://mobi.kuwo.cn/mobi.s?f=web&source=jiakong&type=convert_url_with_sign&rid={song_id}&br=128kmp3"
                ret = requests.get(url, headers=_KUWO_HEADERS, timeout=10).json()
                pic = ret.get("data", {}).get("pic", "")
                if pic:
                    return {"code": 200, "cover": pic}
            elif source == "wyy":
                url = f"https://music.163.com/api/song/detail/?id={song_id}&ids=%5B{song_id}%5D"
                ret = requests.get(url, headers=_KUGOU_HEADERS, timeout=10).json()
                if ret.get("songs"):
                    cover = ret["songs"][0].get("album", {}).get("picUrl", "")
                    if cover:
                        return {"code": 200, "cover": cover}
        except Exception:
            pass
        return {"code": 200, "cover": ""}

    def get_lyric(self, song_id, source=None):
        source = source or self.source
        try:
            if source == "kugou":
                api = MusicApi_kugou(song_id, HOST=DEFAULT_HOST)
                lrc = api.get_kugou_lrc(song_id)
                if lrc and "error" not in lrc:
                    return {"code": 200, "lyric": lrc}
            elif source == "kuwo":
                url = f"https://www.kuwo.cn/api/v1/www/music/playInfo?mid={song_id}&type=music&httpsStatus=1"
                ret = requests.get(url, headers=_KUWO_HEADERS, timeout=10).json()
                lrc_url = ret.get("data", {}).get("lrcUrl", "")
                if lrc_url:
                    lrc_text = requests.get(lrc_url, timeout=10).text
                    return {"code": 200, "lyric": lrc_text}
                if HAS_KUWO:
                    api = MusicApi_kuwo("")
                    lrc = api.get_kuwo_lrc(song_id)
                    if lrc and "error" not in lrc:
                        return {"code": 200, "lyric": lrc}
            elif source == "wyy":
                api = MusicApi_wyy("")
                lrc = api.get_wyy_lrc(song_id)
                if lrc:
                    return {"code": 200, "lyric": lrc}
            elif source == "qq" and HAS_QQ:
                api = MusicApi_qq("")
                lrc = api.get_qq_lrc(song_id)
                if lrc:
                    return {"code": 200, "lyric": lrc}
        except Exception:
            pass
        return {"code": 200, "lyric": ""}

    def get_comments(self, song_id, limit=20):
        return {"code": 200, "comments": []}

    def get_top_songs(self):
        try:
            url = "http://mobilecdn.kugou.com/api/v3/rank/song?rankid=8888&page=1&pagesize=30"
            ret = requests.get(url, headers=_KUGOU_HEADERS, timeout=10).json()
            songs = []
            for i in ret.get("data", {}).get("info", []):
                songs.append({
                    "id": i.get("hash", ""),
                    "title": i.get("songname", ""),
                    "artist": i.get("singername", ""),
                    "album": i.get("album_name", ""),
                    "duration": i.get("duration", 0),
                    "source": "kugou",
                    "cover": "",
                })
            if songs:
                return {"code": 200, "songs": songs}
        except Exception:
            pass

        return {"code": 404, "songs": []}
