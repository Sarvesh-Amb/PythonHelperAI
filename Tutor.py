"""Python Tutor Agent - a local AI teacher built on Ollama.

Needs Python 3.10+ (lesson 15 uses match/case).
Setup:  pip install ollama   |   ollama pull llama3.2   |   python tutor.py
"""
import json
import re
import subprocess
import sys
import webbrowser
from pathlib import Path

import ollama

MODEL = "qwen2.5-coder:7b"        
HERE = Path(__file__).parent
LESSONS = json.loads((HERE / "lessons.json").read_text())
PROGRESS_FILE = HERE / "progress.json"

SYSTEM = """You are a friendly, patient Python tutor for a young beginner.
Rules: use examples to explain concepts, at first make it short and simple,
before starting a lesson, explain its objective and what functions
the user would have to use to complete it,
i.e. explain the learning outcomes and their concepts.
Be generous with your hints. If a user has not used a function or concept previously,
explain it using an example.
Ask the user if they understood the concept. If not, explain the concept again,
more simply, even if it takes longer.
Keep replies under about 150 words (a re-explanation may be longer)
and ask only one question at a time.
When the user reaches the final project, don't suggest a simple calculator;
offer 3 different project ideas and let the user choose one.
NEVER hand over the full solution to an exercise - give hints and
ask guiding questions. Celebrate small wins. Use Python 3."""


# ---------- progress tracking ----------
def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed": [], "attempts": {}, "current": 1}


def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p, indent=2))


def get_lesson(lesson_id):
    return next((l for l in LESSONS if l["id"] == lesson_id), None)


def show_progress(p):
    done = len(p["completed"])
    bar = "#" * done + "-" * (len(LESSONS) - done)
    print(f"\nProgress: [{bar}] {done}/{len(LESSONS)} lessons")
    for l in LESSONS:
        mark = "done" if l["id"] in p["completed"] else "    "
        print(f"  [{mark}] {l['id']:>2}. ({l['level']}) {l['title']}"
              f"  - attempts: {p['attempts'].get(str(l['id']), 0)}")
    print()


# ---------- talking to the model ----------
def ask(messages, show=True):
    reply = ""
    for chunk in ollama.chat(model=MODEL, messages=messages, stream=True):
        piece = chunk["message"]["content"]
        reply += piece
        if show:
            print(piece, end="", flush=True)
    if show:
        print()
    return reply


# ---------- flowcharts ----------
HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Flowchart</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js"></script>
</head><body style="font-family:sans-serif;padding:2rem">
<h2>{title}</h2><pre class="mermaid">
{code}
</pre><script>mermaid.initialize({{startOnLoad:true}});</script></body></html>"""


def make_flowchart(topic_text, title):
    prompt = ("Create a simple Mermaid flowchart (use 'flowchart TD') for this "
              "Python program or idea. Short labels, wrap labels containing "
              "symbols in double quotes. Reply with ONLY the Mermaid code, "
              f"no explanation, no code fences.\n\n{topic_text}")
    code = ask([{"role": "user", "content": prompt}], show=False)
    code = re.sub(r"```(?:mermaid)?", "", code).strip()
    out = HERE / "flowchart.html"
    out.write_text(HTML.format(title=title, code=code))
    webbrowser.open(out.as_uri())
    print(f"Flowchart saved to {out} (opened in your browser).")


# ---------- checking his code ----------
def run_code(path):
    try:
        r = subprocess.run([sys.executable, path], capture_output=True, text=True,
                           timeout=5, input="5\n3\n7\n")  # sample inputs
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "(program ran longer than 5 seconds - maybe an endless loop?)"


def submit(path, lesson, progress, history):
    if lesson.get("type") == "chat":
        print("This lesson is a chat lesson - there is no code to check. Type /done when you finish.")
        return
    if not Path(path).exists():
        print("I can't find that file. Try: /submit myfile.py")
        return
    code = Path(path).read_text()
    output = run_code(path)
    key = str(lesson["id"])
    progress["attempts"][key] = progress["attempts"].get(key, 0) + 1
    prompt = (f"Exercise: {lesson['exercise']}\n\nStudent code:\n{code}\n\n"
              f"Program output:\n{output}\n\nGive kind, short feedback with hints "
              "(no full solution). On the LAST line write exactly "
              "VERDICT: PASS if the exercise is solved, otherwise VERDICT: RETRY.")
    history.append({"role": "user", "content": prompt})
    reply = ask([{"role": "system", "content": SYSTEM}] + history[-10:])
    history.append({"role": "assistant", "content": reply})
    if "VERDICT: PASS" in reply:
        if lesson["id"] not in progress["completed"]:
            progress["completed"].append(lesson["id"])
        print("\n*** Lesson complete! Type /next for the next one. ***")
    save_progress(progress)


def mark_done(lesson, progress):
    if lesson["id"] not in progress["completed"]:
        progress["completed"].append(lesson["id"])
    save_progress(progress)
    print("*** Lesson complete! Type /next for the next one. ***")


# ---------- main loop ----------
HELP = """Commands:
  /next            start the next lesson
  /lesson          show the current lesson again
  /flow            flowchart of the current lesson (or: /flow <your idea>)
  /flowfile x.py   flowchart of one of your own programs
  /submit x.py     run your solution and get feedback
  /done            finish a chat lesson (lessons with no code)
  /progress        see your progress
  /quit            exit
Or just type a question!"""


def start_lesson(lesson, history):
    print(f"\n=== Lesson {lesson['id']}: {lesson['title']} ({lesson['level']}) ===")
    print(f"Exercise: {lesson['exercise']}\n")
    history.append({"role": "user", "content":
        f"Teach me '{lesson['title']}' in Python. Explain briefly with one small "
        f"example, then remind me of my exercise: {lesson['exercise']}"})
    reply = ask([{"role": "system", "content": SYSTEM}] + history[-10:])
    history.append({"role": "assistant", "content": reply})


def main():
    progress = load_progress()
    history = []
    print("Hi! I'm your Python tutor.\n" + HELP)
    show_progress(progress)
    while True:
        lesson = get_lesson(progress["current"])
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        cmd, _, arg = text.partition(" ")
        if cmd == "/quit":
            break
        elif cmd == "/progress":
            show_progress(progress)
        elif cmd == "/next":
            nxt = get_lesson(lesson["id"] + 1) if lesson["id"] in progress["completed"] else lesson
            if nxt is None:
                print("You finished every lesson - amazing!")
                continue
            progress["current"] = nxt["id"]
            save_progress(progress)
            start_lesson(nxt, history)
        elif cmd == "/done":
            if lesson.get("type") == "chat":
                mark_done(lesson, progress)
            else:
                print("This lesson needs code - use /submit yourfile.py")
        elif cmd == "/lesson":
            start_lesson(lesson, history)
        elif cmd == "/flow":
            topic = arg or f"{lesson['title']}: {lesson['exercise']}"
            make_flowchart(topic, topic[:60])
        elif cmd == "/flowfile":
            make_flowchart(Path(arg).read_text(), arg)
        elif cmd == "/submit":
            submit(arg, lesson, progress, history)
        elif cmd == "/help":
            print(HELP)
        else:
            history.append({"role": "user", "content": text})
            reply = ask([{"role": "system", "content": SYSTEM}] + history[-10:])
            history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()