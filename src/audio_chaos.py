"""Random 'Good Boy' chaotic audio engine with cross-platform WAV playback."""

import datetime
import os
import platform
import random
import shutil
import subprocess
import threading
from typing import Dict, List, Tuple

from persona_engine import get_base_path

try:
    import winsound  # Windows built-in zero-dependency WAV playback
except ImportError:
    winsound = None


ABSURD_TOASTS = [
    "Certified Good Boy Energy +1",
    "Unexplained Audio Event Triggered",
    "Why did that sound just play?",
    "Zero Context. Maximum Good Boy.",
    "The Audio Gremlin Approves",
    "Random Sound Dispensed Successfully",
    "Completely Unnecessary Audio Achieved",
    "100% Free-Range Good Boy Noise",
    "Your Persona Looked Confused By That",
    "Acoustic Chaos Level Increasing...",
    "That Sound Had No Business Playing",
    "Official Good Boy Verification Chime",
]


class GoodBoyAudioEngine:
    """Loads all WAV files in assets/audio and plays random clips on demand."""

    def __init__(self) -> None:
        self.audio_dir = os.path.join(get_base_path(), "assets", "audio")
        self.clips: List[str] = self._discover_clips()
        self._bag: List[str] = []
        self.press_count: int = 0
        self.history: List[Dict[str, str]] = []

    def _discover_clips(self) -> List[str]:
        if not os.path.isdir(self.audio_dir):
            return []
        return sorted(
            os.path.join(self.audio_dir, f)
            for f in os.listdir(self.audio_dir)
            if f.lower().endswith(".wav")
        )

    def _next_random_clip(self) -> str:
        if not self.clips:
            return ""
        if not self._bag:
            self._bag = list(self.clips)
            random.shuffle(self._bag)
        return self._bag.pop()

    def trigger_random_good_boy(self) -> Tuple[str, str, int]:
        """Play a random WAV clip asynchronously and return (clip_label, toast, count)."""
        self.press_count += 1
        clip_path = self._next_random_clip()
        toast = random.choice(ABSURD_TOASTS)

        if not clip_path:
            label = "No WAV files found"
            return label, toast, self.press_count

        label = os.path.splitext(os.path.basename(clip_path))[0].replace("_", " ").title()
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history.insert(0, {"time": timestamp, "clip": label, "toast": toast})
        self.history = self.history[:30]

        self._play_async(clip_path)
        return label, toast, self.press_count

    def _play_async(self, wav_path: str) -> None:
        system = platform.system()
        if system == "Windows" and winsound is not None:
            try:
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except Exception:
                pass

        def _worker():
            for player in ("afplay", "paplay", "aplay", "ffplay"):
                exe = shutil.which(player)
                if exe:
                    cmd = [exe, wav_path]
                    if player == "ffplay":
                        cmd = [exe, "-nodisp", "-autoexit", "-loglevel", "quiet", wav_path]
                    try:
                        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return
                    except Exception:
                        continue

        threading.Thread(target=_worker, daemon=True).start()
