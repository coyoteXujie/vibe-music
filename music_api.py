import json
import requests


class MusicAPI:
    NCM_URL = "http://127.0.0.1:52401"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        self._ncm_available = False
        self._check_ncm()

    def _check_ncm(self):
        try:
            resp = self.session.get(f"{self.NCM_URL}/search", params={"keywords": "test", "limit": 1}, timeout=3)
            if resp.status_code == 200:
                self._ncm_available = True
        except Exception:
            self._ncm_available = False

    def _ncm_get(self, endpoint, params=None):
        if not self._ncm_available:
            self._check_ncm()
        try:
            resp = self.session.get(f"{self.NCM_URL}{endpoint}", params=params, timeout=10)
            return resp.json()
        except Exception as e:
            self._ncm_available = False
            return {"code": 500, "msg": str(e)}

    def search(self, keyword, page=1, limit=30):
        offset = (page - 1) * limit
        result = self._ncm_get("/cloudsearch", params={"keywords": keyword, "offset": offset, "limit": limit, "type": 1})
        if result.get("code") == 200 or "result" in result:
            songs = []
            for s in result.get("result", {}).get("songs", []):
                artists = ", ".join(a.get("name", "") for a in s.get("ar", []))
                album = s.get("al", {}).get("name", "")
                songs.append({
                    "id": s.get("id"),
                    "title": s.get("name", ""),
                    "artist": artists,
                    "album": album,
                    "duration": s.get("dt", 0) // 1000 if s.get("dt") else 0,
                    "source": "网易云",
                })
            song_count = result.get("result", {}).get("songCount", len(songs))
            return {"code": 200, "songs": songs, "total": song_count}
        return {"code": result.get("code", 500), "msg": "搜索失败", "songs": []}

    def get_song_url(self, song_id):
        result = self._ncm_get("/song/url", params={"id": song_id})
        if result.get("code") == 200:
            data_list = result.get("data", [])
            if data_list and data_list[0].get("url"):
                return {"code": 200, "url": data_list[0]["url"]}
        result2 = self._ncm_get("/song/url/v1", params={"id": song_id, "level": "exhigh"})
        if result2.get("code") == 200:
            data_list = result2.get("data", [])
            if data_list and data_list[0].get("url"):
                return {"code": 200, "url": data_list[0]["url"]}
        return {"code": 404, "msg": "无法获取播放链接，歌曲可能需要VIP或已下架"}

    def get_song_detail(self, song_id):
        result = self._ncm_get("/song/detail", params={"ids": str(song_id)})
        if result.get("code") == 200:
            songs = result.get("songs", [])
            if songs:
                s = songs[0]
                artists = ", ".join(a.get("name", "") for a in s.get("ar", []))
                album = s.get("al", {}).get("name", "")
                cover = s.get("al", {}).get("picUrl", "")
                return {
                    "code": 200,
                    "id": s.get("id"),
                    "title": s.get("name", ""),
                    "artist": artists,
                    "album": album,
                    "cover": cover,
                    "duration": s.get("dt", 0) // 1000,
                }
        return {"code": 404, "msg": "歌曲详情获取失败"}

    def get_lyric(self, song_id):
        result = self._ncm_get("/lyric", params={"id": song_id})
        if result.get("code") == 200:
            lrc = result.get("lrc", {}).get("lyric", "")
            tlyric = result.get("tlyric", {}).get("lyric", "")
            return {"code": 200, "lyric": lrc, "tlyric": tlyric}
        return {"code": 404, "msg": "歌词获取失败"}

    def get_recommend_playlists(self):
        result = self._ncm_get("/personalized", params={"limit": 12})
        if result.get("code") == 200:
            playlists = []
            for p in result.get("result", []):
                playlists.append({
                    "id": p.get("id"),
                    "name": p.get("name", ""),
                    "cover": p.get("picUrl", ""),
                    "playcount": p.get("playCount", 0),
                })
            return {"code": 200, "playlists": playlists}
        return {"code": 500, "msg": "获取推荐歌单失败", "playlists": []}

    def get_playlist_detail(self, playlist_id):
        result = self._ncm_get("/playlist/detail", params={"id": playlist_id})
        if result.get("code") == 200:
            playlist = result.get("playlist", {})
            tracks = []
            for t in playlist.get("tracks", []):
                artists = ", ".join(a.get("name", "") for a in t.get("ar", []))
                album = t.get("al", {}).get("name", "")
                tracks.append({
                    "id": t.get("id"),
                    "title": t.get("name", ""),
                    "artist": artists,
                    "album": album,
                    "duration": t.get("dt", 0) // 1000,
                    "source": "网易云",
                })
            return {
                "code": 200,
                "name": playlist.get("name", ""),
                "tracks": tracks,
                "track_count": playlist.get("trackCount", 0),
            }
        return {"code": 500, "msg": "歌单详情获取失败", "tracks": []}

    def get_top_songs(self):
        result = self._ncm_get("/toplist/detail")
        if result.get("code") == 200:
            lists = result.get("list", [])
            if lists:
                first_list = lists[0]
                track_ids = [t.get("id") for t in first_list.get("tracks", [])[:30]]
                if track_ids:
                    detail = self._ncm_get("/song/detail", params={"ids": ",".join(str(i) for i in track_ids)})
                    if detail.get("code") == 200:
                        songs = []
                        for s in detail.get("songs", []):
                            artists = ", ".join(a.get("name", "") for a in s.get("ar", []))
                            album = s.get("al", {}).get("name", "")
                            songs.append({
                                "id": s.get("id"),
                                "title": s.get("name", ""),
                                "artist": artists,
                                "album": album,
                                "duration": s.get("dt", 0) // 1000,
                                "source": "网易云",
                            })
                        return {"code": 200, "songs": songs}
        result2 = self._ncm_get("/top/song", params={"type": 0})
        if result2.get("code") == 200:
            songs = []
            for s in result2.get("data", [])[:30]:
                artists = ", ".join(a.get("name", "") for a in s.get("artists", []))
                album = s.get("album", {}).get("name", "")
                songs.append({
                    "id": s.get("id"),
                    "title": s.get("name", ""),
                    "artist": artists,
                    "album": album,
                    "duration": s.get("duration", 0) // 1000,
                    "source": "网易云",
                })
            return {"code": 200, "songs": songs}
        return self._fallback_top_songs()

    def get_comments(self, song_id, limit=20):
        result = self._ncm_get("/comment/music", params={"id": song_id, "limit": limit})
        comments = []
        if result.get("code") == 200:
            for c in result.get("hotComments", []):
                content = c.get("content", "").strip()
                if content and len(content) <= 80:
                    nickname = c.get("user", {}).get("nickname", "")
                    comments.append({"text": content, "user": nickname, "liked": c.get("likedCount", 0)})
            for c in result.get("comments", []):
                if len(comments) >= limit:
                    break
                content = c.get("content", "").strip()
                if content and len(content) <= 80:
                    nickname = c.get("user", {}).get("nickname", "")
                    comments.append({"text": content, "user": nickname, "liked": c.get("likedCount", 0)})
        if not comments:
            result2 = self._ncm_get("/comment/hot", params={"id": song_id, "type": 0, "limit": limit})
            if result2.get("code") == 200:
                for c in result2.get("hotComments", []):
                    content = c.get("content", "").strip()
                    if content and len(content) <= 80:
                        nickname = c.get("user", {}).get("nickname", "")
                        comments.append({"text": content, "user": nickname, "liked": c.get("likedCount", 0)})
        return {"code": 200, "comments": comments}

    def _fallback_top_songs(self):
        fallback = [
            {"id": 186016, "title": "晴天", "artist": "周杰伦", "album": "叶惠美", "duration": 269, "source": "网易云"},
            {"id": 167876, "title": "稻香", "artist": "周杰伦", "album": "魔杰座", "duration": 223, "source": "网易云"},
            {"id": 139734, "title": "七里香", "artist": "周杰伦", "album": "七里香", "duration": 299, "source": "网易云"},
            {"id": 25706282, "title": "平凡之路", "artist": "朴树", "album": "猎户星座", "duration": 282, "source": "网易云"},
            {"id": 1353225528, "title": "起风了", "artist": "买辣椒也用券", "album": "起风了", "duration": 315, "source": "网易云"},
            {"id": 447925558, "title": "成都", "artist": "赵雷", "album": "无法长大", "duration": 329, "source": "网易云"},
            {"id": 441491828, "title": "南山南", "artist": "马頔", "album": "孤岛", "duration": 336, "source": "网易云"},
            {"id": 28285910, "title": "平凡之路", "artist": "朴树", "album": "猎户星座", "duration": 282, "source": "网易云"},
            {"id": 108242, "title": "倔强", "artist": "五月天", "album": "时光机", "duration": 261, "source": "网易云"},
            {"id": 383582, "title": "突然好想你", "artist": "五月天", "album": "后青春期的诗", "duration": 269, "source": "网易云"},
        ]
        return {"code": 200, "songs": fallback}
