# read4me

A tiny macOS utility that lets you **select any text**, hit a hotkey, and hear it read out loud. Great for long emails, docs, or web articles when your eyes need a break.

## Why I built this

I don’t enjoy reading long text on my computer. It slows me down and I lose focus. I follow better when I hear the words. I wanted something simple that turns any selected text into speech on demand, without switching apps or pasting into a reader. That’s all read4me does: I select, press a shortcut, and it talks to me. It keeps me moving and makes long passages easier to digest.

## What it does

* Works **anywhere on macOS** with selected text
* **Hotkey to speak** the current selection
* **Hotkey to stop** speaking
* Uses macOS built-in TTS (`say`) so it’s fast and offline
* Restores your clipboard after speaking

## Requirements

* macOS
* Python 3.10+
* `pynput` and `pyperclip` Python packages
* Accessibility permission for your terminal or IDE

## Install

```bash
git clone <your-repo-url>
cd read4me
pip install pynput pyperclip
```

## Run

```bash
python speak_selection.py
```

On first run, macOS will likely ask you to allow Accessibility access:

**System Settings → Privacy & Security → Accessibility → enable** your terminal or IDE.

## Hotkeys

* **Cmd + Shift + S** → Copy current selection and speak it
* **Cmd + Shift + X** → Stop speaking

Select any text in any app, press **Cmd + Shift + S**, and it will read just that selection.

## Configuration

Open `speak_selection.py` and adjust:

```python
speaker = TextSpeaker(rate_wpm=190, voice=None)  # e.g. voice="Samantha" or "Alex"
reader = SelectionReader(copy_delay_sec=0.30)    # bump to 0.40–0.50 if an app is slow
```

* `rate_wpm`: speaking speed
* `voice`: choose a macOS voice
* `copy_delay_sec`: wait time for apps to update the clipboard

## How it works

* Temporarily clears the clipboard
* Sends Cmd+C to copy your current selection
* Waits a short moment for the app to place text on the clipboard
* Reads that fresh text through `say`
* Restores your original clipboard

## Troubleshooting

* **Nothing is spoken**: Make sure you actually have text selected, and that Accessibility is enabled for your terminal/IDE. Try increasing `copy_delay_sec`.
* **Reads the wrong thing**: Some apps are slower to update the clipboard. Increase `copy_delay_sec` to 0.40–0.50.
* **Hotkey doesn’t trigger**: Another tool may be using the same shortcut. Change the combo in the `GlobalHotKeys` map.

## Roadmap

* Menu bar toggle and status
* Quick voice switcher
* Pause and resume
* Optional on-screen toast when nothing is selected
* Cross-platform TTS (e.g., `pyttsx3`) while keeping macOS quality where available

## Contributing

PRs and issues are welcome. Keep it simple and readable. This project aims to stay a small utility.

## License

MIT
