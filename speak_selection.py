# speak_selection.py
"""
read4me — Menu bar "select and speak" app for macOS.

Features
  - Global hotkeys to speak the current selection and stop speaking
  - Menu bar toggle to enable/disable hotkeys
  - Menu item linking to documentation/how-to-use

Hotkeys
  - Cmd+Shift+S : Copy current selection and speak it
  - Cmd+Shift+X : Stop speaking

Requirements
  pip install rumps pynput pyperclip

macOS Setup
  - Allow your terminal/IDE in System Settings → Privacy & Security → Accessibility
  - First run will trigger permission prompts

Notes
  - Speaking is triggered by hotkeys. (Using the menu item to speak would steal focus
    from the current app and may not capture the selection reliably.)
"""

from __future__ import annotations

import subprocess
import sys
import time
import threading
import webbrowser
from typing import Optional

import pyperclip
import rumps
from pynput import keyboard
from pynput.keyboard import Key, Controller

# ---- Config ----
DEFAULT_RATE_WPM: int = 190
DEFAULT_VOICE: Optional[str] = None  # e.g., "Samantha", "Alex"
COPY_DELAY_SEC: float = 0.30
DOCS_URL: str = "https://github.com/codewithbro95/read4me"  # Update to your repo
APP_TITLE_ENABLED = "🗣️ r4me"
APP_TITLE_DISABLED = "r4me"


class TextSpeaker:
    """Handles reading text with macOS 'say' and managing the speaking process."""

    def __init__(self, rate_wpm: int = DEFAULT_RATE_WPM, voice: Optional[str] = DEFAULT_VOICE):
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
            self._stop_locked()

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
            self._stop_locked()

    def _stop_locked(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass
        self._proc = None
        print("[stop] Stopped.")


class SelectionReader:
    """Copies current selection via Cmd+C and returns clipboard contents."""

    def __init__(self, copy_delay_sec: float = COPY_DELAY_SEC):
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


class HotkeyService:
    """Manages a background GlobalHotKeys listener that can be toggled on/off."""

    def __init__(self, on_speak, on_stop, debouncer: HotkeyDebouncer):
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._on_speak = on_speak
        self._on_stop = on_stop
        self._debouncer = debouncer

    def start(self) -> None:
        if self._listener is not None:
            return
        self._listener = keyboard.GlobalHotKeys({
            '<cmd>+<shift>+s': self._wrapped_speak,
            '<cmd>+<shift>+x': self._on_stop,
        })
        self._listener.start()
        print('[hotkeys] Enabled')

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
            print('[hotkeys] Disabled')

    def _wrapped_speak(self):
        if self._debouncer.ok():
            self._on_speak()


class Read4MeMenuApp(rumps.App):
    """Menu bar controller for read4me."""

    def __init__(self) -> None:
        super().__init__(APP_TITLE_ENABLED)
        self.speaker = TextSpeaker(rate_wpm=DEFAULT_RATE_WPM, voice=DEFAULT_VOICE)
        self.reader = SelectionReader(copy_delay_sec=COPY_DELAY_SEC)
        self.debounce = HotkeyDebouncer(0.5)
        self.hotkeys = HotkeyService(self._speak_selection, self._stop_speaking, self.debounce)

        # Menu items
        self.enable_item = rumps.MenuItem("Enable hotkeys", callback=self._toggle_hotkeys)
        self.docs_item = rumps.MenuItem("Documentation / How to use", callback=self._open_docs)

        self.menu = [
            self.enable_item,
            None,
            self.docs_item,
        ]

        # Start enabled by default for continuity with the CLI version
        self.enabled = True
        self.enable_item.state = 1
        self.hotkeys.start()
        self.title = APP_TITLE_ENABLED

    # ---- Actions ----
    def _speak_selection(self, *_):
        text = self.reader.copy_selection_to_clipboard()
        if not text.strip():
            rumps.notification("read4me", "Nothing selected", "Select text and press Cmd+Shift+S")
            return
        self.speaker.speak(text)

    def _stop_speaking(self, *_):
        self.speaker.stop()

    def _toggle_hotkeys(self, _: rumps.MenuItem):
        self.enabled = not self.enabled
        if self.enabled:
            self.hotkeys.start()
            self.enable_item.state = 1
            self.title = APP_TITLE_ENABLED
        else:
            self.hotkeys.stop()
            self.enable_item.state = 0
            self.title = APP_TITLE_DISABLED

    def _open_docs(self, *_):
        try:
            webbrowser.open(DOCS_URL)
        except Exception as e:
            print(f"[error] Could not open docs: {e}")


def main() -> None:
    Read4MeMenuApp().run()


if __name__ == "__main__":
    main()
