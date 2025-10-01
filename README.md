# read4me

A tiny macOS utility that lets you **select any text**, hit a hotkey, and hear it read out loud. Great for long emails, docs, or web articles when your eyes need a break.

## Why I built this

I don’t enjoy reading long text on my computer. It slows me down and I lose focus. I follow better when I hear the words. I wanted something simple that turns any selected text into speech on demand, without switching apps or pasting into a reader. That’s all read4me does: I select, press a shortcut, and it talks to me. It keeps me moving and makes long passages easier to digest.

## What it does

- **System‑wide**: Works anywhere on macOS with selected text
- **Menu bar app**: Enable/disable hotkeys and open documentation from the menu bar
- **Hotkeys**: Speak selection (Cmd+Shift+S) and Stop (Cmd+Shift+X)
- **Offline TTS**: Uses macOS `say` (fast, built‑in)
- **Clipboard‑friendly**: Temporarily copies selection and restores your clipboard
- **Single‑file MVP**: Simple codebase, easy to hack

## Requirements

- macOS (Apple Silicon or Intel): Tested on macOS 26.0.1
- Python 3.10+
- Python packages: `rumps`, `pynput`, `pyperclip`, `pyobjc`
- Permissions: **Accessibility** and **Input Monitoring** (details below)

## Install

### Option A: Download the app (recommended)

From the GitHub [Releases](https://github.com/codewithbro95/read4me/releases/tag/beta) page, download `read4me.app` (or `.dmg`: coming later), move it to **Applications**, and open it.

On first launch, macOS will prompt you for permissions (see **Permissions** below). After enabling, quit and relaunch if macOS asks you to.

### Option B: Run from source (developer mode)

```bash
pip install --upgrade pip wheel setuptools
pip install rumps pynput pyperclip pyobjc

python speak_selection.py
```

> First run from Terminal will ask for **Accessibility** (to send Cmd+C) and may ask for **Input Monitoring** (to listen for global hotkeys).

---

## Usage

- Select any text in any app.
- Press **Cmd + Shift + S** to hear it.
- Press **Cmd + Shift + X** to stop.

There’s a menu bar item called **r4me** where you can toggle hotkeys and open the documentation.

---

## Permissions (macOS)

read4me needs two macOS privacy permissions to work everywhere:

1. **Accessibility:** lets read4me send **Cmd+C** to copy your selection from the foreground app.
2. **Input Monitoring:** lets read4me listen for your global hotkeys.

## Configuration

Open `speak_selection.py` and tweak:

```python
speaker = TextSpeaker(rate_wpm=190, voice=None)  # e.g., "Samantha" or "Alex"
reader = SelectionReader(copy_delay_sec=0.30)    # bump to 0.40–0.50 if an app is slow
```

- `rate_wpm`: speaking speed
- `voice`: choose a macOS voice
- `copy_delay_sec`: extra time for slower apps to update the clipboard

## How it works

- Clears the clipboard (temporarily)
- Sends **Cmd+C** to copy your current selection
- Waits briefly for the app to write to the clipboard
- Streams that text to macOS `say`
- Restores your original clipboard

## Troubleshooting

- **No speech**: Ensure both **Accessibility** and **Input Monitoring** are enabled for read4me. Also verify that text is actually selected.
- **Reads the wrong thing**: Some apps are slower. Increase `copy_delay_sec` to `0.40–0.50`.
- **Hotkey doesn’t trigger**: Shortcut clash. Change the combo in the global hotkey map in `speak_selection.py`.

## Roadmap

- Pause/Resume
- Quick voice switcher
- Menu bar icon + preferences
- Cross‑platform TTS (while keeping high quality on macOS)

## Contributing

PRs and issues are welcome. Keep it small, focused, and readable.

## License

MIT
