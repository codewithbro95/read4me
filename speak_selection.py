# speak_selection.py
"""
System-wide "select and speak" MVP for macOS.

Hotkeys:
  - Cmd+Shift+S : Copy current selection and speak it
  - Cmd+Shift+X : Stop speaking

Requirements:
  pip install pynput pyperclip

macOS:
  - Allow your terminal/IDE in System Settings → Privacy & Security → Accessibility.
"""

from __future__ import annotations

import subprocess
import sys
import time
import threading
from typing import Optional

import pyperclip
from pynput import keyboard
from pynput.keyboard import Key, Controller


class TextSpeaker:
    """Handles reading text with macOS 'say' and managing the speaking process."""
    def __init__(self, rate_wpm: int = 190, voice: Optional[str] = None):
        self._proc: Optional[subprocess.Popen] = None
        self.rate_wpm = rate_wpm
        self.voice = voice
        self._lock = threading.Lock()

    def speak(self, text: str) -> None:
        """Start speaking the given text, stopping any existing speech."""
        text = (text or "").strip()
        if not text:
            print("[info] No text selected.")
            return

        with self._lock:
            self.stop_locked()

            cmd = ["say", "-r", str(self.rate_wpm)]
            if self.voice:
                cmd += ["-v", self.voice]

            # Use stdin to avoid shell quoting limits
            self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            assert self._proc.stdin is not None
            self._proc.stdin.write(text.encode("utf-8", errors="ignore"))
            self._proc.stdin.close()

        print("[speak] Reading selection...")

    def stop(self) -> None:
        with self._lock:
            self.stop_locked()

    def stop_locked(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self._proc = None
        print("[stop] Stopped.")


class SelectionReader:
    """Copies current selection via Cmd+C and returns clipboard contents."""
    def __init__(self, copy_delay_sec: float = 0.30):
        self.kbd = Controller()
        self.copy_delay_sec = copy_delay_sec

    def copy_selection_to_clipboard(self) -> str:
        """
        Clear clipboard, issue Cmd+C to copy the current selection, wait,
        read clipboard, then restore previous clipboard.
        """
        # Save clipboard and clear it so we do not read stale content
        try:
            prev_clip = pyperclip.paste()
        except pyperclip.PyperclipException:
            prev_clip = ""
        try:
            pyperclip.copy("")  # clear
        except pyperclip.PyperclipException:
            pass

        # Small pause to let hotkey modifiers settle
        time.sleep(0.05)

        # Press Cmd+C to copy current selection
        with self._pressed(Key.cmd):
            self.kbd.press('c')
            self.kbd.release('c')

        # Wait for the app to place data on the clipboard
        time.sleep(self.copy_delay_sec)

        # Try read, retry once if still empty (some apps are slower)
        text = ""
        try:
            text = pyperclip.paste()
        except pyperclip.PyperclipException:
            text = ""

        if not text.strip():
            time.sleep(0.20)
            try:
                text = pyperclip.paste()
            except pyperclip.PyperclipException:
                text = ""

        # Restore previous clipboard content (do not disturb user's clipboard)
        try:
            pyperclip.copy(prev_clip)
        except pyperclip.PyperclipException:
            pass

        return text or ""

    from contextlib import contextmanager

    @contextmanager
    def _pressed(self, key):
        """Context manager to press and release a modifier key cleanly."""
        self.kbd.press(key)
        try:
            yield
        finally:
            self.kbd.release(key)


class HotkeyDebouncer:
    """Prevents multiple triggers from a single key press."""
    def __init__(self, min_interval_sec: float = 0.5):
        self.min_interval = min_interval_sec
        self._last = 0.0
        self._lock = threading.Lock()

    def ok(self) -> bool:
        now = time.time()
        with self._lock:
            if now - self._last < self.min_interval:
                return False
            self._last = now
            return True


def main() -> None:
    speaker = TextSpeaker(rate_wpm=190, voice=None)  # set voice like "Samantha" if you want
    reader = SelectionReader(copy_delay_sec=0.30)
    debounce = HotkeyDebouncer(0.5)

    def on_speak():
        if not debounce.ok():
            return
        text = reader.copy_selection_to_clipboard()
        if not text.strip():
            print("[info] No selection detected.")
            return
        speaker.speak(text)

    def on_stop():
        speaker.stop()

    print("Select text anywhere, then use:")
    print("  Cmd+Shift+S : Speak selection")
    print("  Cmd+Shift+X : Stop")
    print("Press Ctrl+C to exit.\n")

    # Global hotkeys
    with keyboard.GlobalHotKeys({
        '<cmd>+<shift>+s': on_speak,
        '<cmd>+<shift>+x': on_stop,
    }) as h:
        try:
            h.join()
        except KeyboardInterrupt:
            print("\n[exit] Bye.")
            speaker.stop()
            sys.exit(0)


if __name__ == "__main__":
    main()
