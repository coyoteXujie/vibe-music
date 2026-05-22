import subprocess
import threading
import time
import os
import platform
import json


class Player:
    def __init__(self):
        self.process = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 80
        self.current_song = None
        self.position = 0.0
        self.duration = 0.0
        self.start_time = 0.0
        self.paused_position = 0.0
        self._lock = threading.Lock()
        self._monitor_thread = None
        self._stop_event = threading.Event()
        self.queue = []
        self.queue_index = -1
        self.play_mode = "list_loop"
        self.ffplay_path = self._find_ffplay()

    def _find_ffplay(self):
        system = platform.system()
        if system == "Windows":
            paths = [
                os.path.join(os.path.dirname(__file__), "bin", "ffplay.exe"),
                "ffplay.exe",
            ]
            for p in paths:
                if os.path.isfile(p):
                    return p
            try:
                result = subprocess.run(["where", "ffplay"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip().split("\n")[0]
            except Exception:
                pass
        else:
            try:
                result = subprocess.run(["which", "ffplay"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass
        return None

    def play_url(self, url, song_info=None):
        with self._lock:
            self._stop_internal()
            if not self.ffplay_path:
                self._play_with_system(url, song_info)
                return
            try:
                cmd = [
                    self.ffplay_path,
                    "-nodisp",
                    "-autoexit",
                    "-volume", str(self.volume),
                    "-i", url,
                ]
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.PIPE,
                )
                self.is_playing = True
                self.is_paused = False
                self.current_song = song_info
                self.duration = song_info.get("duration", 0) if song_info else 0
                self.position = 0.0
                self.start_time = time.time()
                self.paused_position = 0.0
                self._stop_event.clear()
                if self._monitor_thread and self._monitor_thread.is_alive():
                    self._stop_event.set()
                    self._monitor_thread.join(timeout=2)
                self._stop_event.clear()
                self._monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
                self._monitor_thread.start()
            except Exception as e:
                print(f"播放失败: {e}")

    def _play_with_system(self, url, song_info=None):
        self.is_playing = True
        self.is_paused = False
        self.current_song = song_info
        self.duration = song_info.get("duration", 0) if song_info else 0
        self.position = 0.0
        self.start_time = time.time()
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(url)
            elif system == "Linux":
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def _monitor_playback(self):
        while not self._stop_event.is_set():
            if self.process and self.is_playing and not self.is_paused:
                ret = self.process.poll()
                if ret is not None:
                    self.is_playing = False
                    self.position = self.duration
                    return
                elapsed = time.time() - self.start_time
                self.position = min(elapsed, self.duration) if self.duration > 0 else elapsed
            self._stop_event.wait(0.5)

    def _stop_internal(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        self.is_playing = False
        self.is_paused = False
        self._stop_event.set()

    def stop(self):
        with self._lock:
            self._stop_internal()
            self.position = 0.0
            self.current_song = None

    def pause(self):
        with self._lock:
            if self.process and self.is_playing and not self.is_paused:
                try:
                    self.process.stdin.write(b"p")
                    self.process.stdin.flush()
                except Exception:
                    pass
                self.is_paused = True
                self.paused_position = self.position

    def resume(self):
        with self._lock:
            if self.process and self.is_paused:
                try:
                    self.process.stdin.write(b"p")
                    self.process.stdin.flush()
                except Exception:
                    pass
                self.is_paused = False
                self.start_time = time.time() - self.paused_position

    def set_volume(self, volume):
        self.volume = max(0, min(100, volume))

    def seek(self, position):
        with self._lock:
            if self.current_song and self.current_song.get("url"):
                url = self.current_song["url"]
                song_info = self.current_song.copy()
                song_info["duration"] = self.duration
                self._stop_internal()
                if self.ffplay_path:
                    try:
                        cmd = [
                            self.ffplay_path,
                            "-nodisp",
                            "-autoexit",
                            "-volume", str(self.volume),
                            "-ss", str(position),
                            "-i", url,
                        ]
                        self.process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            stdin=subprocess.PIPE,
                        )
                        self.is_playing = True
                        self.is_paused = False
                        self.start_time = time.time() - position
                        self.position = position
                        self._stop_event.clear()
                        self._monitor_thread = threading.Thread(target=self._monitor_playback, daemon=True)
                        self._monitor_thread.start()
                    except Exception:
                        pass

    def get_status(self):
        return {
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "volume": self.volume,
            "position": round(self.position, 1),
            "duration": self.duration,
            "current_song": self.current_song,
            "queue": self.queue,
            "queue_index": self.queue_index,
            "play_mode": self.play_mode,
            "ffplay_available": self.ffplay_path is not None,
        }

    def set_queue(self, songs, start_index=0):
        self.queue = songs
        self.queue_index = start_index

    def next(self):
        if not self.queue:
            return None
        if self.play_mode == "single_loop":
            return self.queue[self.queue_index] if 0 <= self.queue_index < len(self.queue) else None
        if self.play_mode == "shuffle":
            self.queue_index = random.randint(0, len(self.queue) - 1)
        else:
            self.queue_index = (self.queue_index + 1) % len(self.queue)
        return self.queue[self.queue_index]

    def prev(self):
        if not self.queue:
            return None
        if self.play_mode == "single_loop":
            return self.queue[self.queue_index] if 0 <= self.queue_index < len(self.queue) else None
        self.queue_index = (self.queue_index - 1) % len(self.queue)
        return self.queue[self.queue_index]

    def set_play_mode(self, mode):
        if mode in ("list_loop", "single_loop", "shuffle"):
            self.play_mode = mode


import random
