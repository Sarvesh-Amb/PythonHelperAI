# Python Tutor Agent

A friendly AI tutor that teaches Python to beginners, running **entirely on your own computer** with [Ollama](https://ollama.com). It never hands over the answer: it gives hints and asks guiding questions. Built for the Hacktoberfest 2026 "Build for a Friend" challenge, for my little brother.

**Features**
- 19 beginner lessons, from `print()` and variables to loops and a final project
- Progress tracking saved in `progress.json`
- `/submit` runs your code and gives feedback from the tutor
- `/flow` makes a flowchart of a lesson or one of your own programs
- Works offline, and your data stays on your computer

## Requirements

- **Python 3.10 or newer** (lesson 15 uses `match`/`case`). Check with `py --version` (Windows) or `python3 --version` (Mac/Linux).
- **[Ollama](https://ollama.com/download)** installed
- About **8GB of free RAM** for the 7B model (16GB total is more comfortable). A graphics card helps but isn't required.
- About 5GB of free disk space

## Setup

**1. Install the Python library**

```
py -m pip install ollama
```
(Mac/Linux: `pip3 install ollama`)

**2. Download the recommended model**

```
ollama pull qwen2.5-coder:7b
```

This is a code-focused model, so it is good at checking and explaining code. The download is about 4-5GB.

**3. Open the project in VS Code (recommended)**

[VS Code](https://code.visualstudio.com) is the easiest way to run this. Go to File > Open Folder and choose this project folder. Installing the Microsoft **Python** extension is also a good idea.

**4. Run the tutor**

Open VS Code's terminal with `` Ctrl + ` `` and run:

```
py tutor.py
```
(Mac/Linux: `python3 tutor.py`)

Make sure Ollama is running first. On Windows it normally starts automatically and sits in the system tray. **The first reply can be slow** (a few minutes on weaker computers) because the model has to load into memory. Later replies are faster.

> The tutor needs you to type into it, so run it in a **terminal**. Run buttons and output panels (such as Code Runner) usually can't accept typed input.

## How to use it

| Command | What it does |
|---|---|
| `/next` | Start the next lesson (or restart the current one if it isn't finished) |
| `/lesson` | Show the current lesson again |
| `/submit myfile.py` | Run your solution and get feedback |
| `/done` | Finish a chat lesson (lessons with no code) |
| `/flow` | Flowchart of the current lesson (or `/flow your idea`) |
| `/flowfile myfile.py` | Flowchart of one of your own programs |
| `/progress` | See your progress |
| `/help` | Show the commands |
| `/quit` | Exit |

Anything you type without a `/` is treated as a question for the tutor.

**Typical flow:** type `/next`, read the lesson, write your solution in a `.py` file, then run `/submit myfile.py`. When the tutor says you passed, the lesson is marked complete.

## Using a different model

You can swap the model whenever you like.

**1. Download it.** Browse [ollama.com/library](https://ollama.com/library) and pull the one you want:

```
ollama pull llama3.1:8b
```

**2. Change one line in `tutor.py`.** Near the top of the file, find:

```python
MODEL = "qwen2.5-coder:7b"
```

and replace the name with the exact name you pulled, for example:

```python
MODEL = "llama3.1:8b"
```

**3. Save and run again.** Check `ollama list` to confirm the exact model name.

**Suggestions**

| Model | Good for | Notes |
|---|---|---|
| `qwen2.5-coder:7b` | Reading and checking code (recommended) | Can sound more technical |
| `llama3.1:8b` | Friendly, chatty explanations | Weaker at spotting subtle bugs |
| `llama3.2` | Computers with little RAM or no GPU | Smaller (3B) and faster, but less accurate |

Any model that works with Ollama should work here. If answers come out strange, try changing the wording of the `SYSTEM` prompt in `tutor.py`, because different models respond differently to the same instructions.

## Optional: store models on another drive (Windows)

Ollama saves models to your user folder on C: by default. To use another drive, quit Ollama, then run:

```
setx OLLAMA_MODELS "D:\ollama\models"
```

Restart Ollama and your terminal, then pull the models again.

## Changing the lessons

Lessons live in `lessons.json`. Each lesson looks like this:

```json
{"id": 2, "level": "beginner", "title": "Print", "exercise": "Print your name and age."}
```

- Keep `id` values unique and in order (1, 2, 3...).
- Add `"type": "chat"` for lessons with no code to check. These are finished with `/done` instead of `/submit`.
- The tutor's personality is the `SYSTEM` prompt at the top of `tutor.py`.

## Troubleshooting

- **`py install ollama` says "Failed to find a suitable install":** use `py -m pip install ollama` instead.
- **"Python was not found" (Microsoft Store message):** use `py` instead of `python`, or turn off the Python App execution aliases in Windows Settings > Apps > Advanced app settings.
- **Connection refused error:** Ollama isn't running. Start it from the Start menu.
- **"model not found":** the `MODEL` name doesn't match what `ollama list` shows, or the download isn't finished.
- **Very slow replies:** try `llama3.2`, close other heavy programs, and run `ollama ps` to see whether it is using the GPU.
- **Flowchart is blank or broken:** small models sometimes write invalid diagram code. Run `/flow` again.
- **Starting over:** delete `progress.json`.

## Project files

- `tutor.py` is the main program
- `lessons.json` holds the lessons
- `requirements.txt` lists the Python library to install
- `progress.json` is created automatically to save your progress

## AI assistance

The starter code for this project was generated with Claude (by Anthropic) in a chat session. I then modified it: [**EDIT THIS: list what you changed, such as writing the lessons, rewriting the system prompt, testing with different models**]. The idea, lesson content, and testing were mine.

## Built with

- [Ollama](https://ollama.com) for running open-weight models locally
- [Qwen2.5-Coder](https://ollama.com/library/qwen2.5-coder) as the default model
- [Mermaid](https://mermaid.js.org) for flowcharts
