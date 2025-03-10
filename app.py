from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from gtts import gTTS
import os
import random
from datetime import timedelta

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/word_files"
app.secret_key = "your_secret_key_here"  # Required for session management
app.permanent_session_lifetime = timedelta(minutes=30)  # Session expires after 30 minutes

# Ensure the word_files directory exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

def load_word_list() -> list[str]:
    """Load the word list from file."""
    with open("words.txt", "r") as fp:
        data = fp.read()
    return data.split("\n")

def create_sound_file(word: str) -> str:
    """Turn a word into a sound file."""
    myobj = gTTS(text=word, lang="en", slow=False)
    fname = os.path.join(app.config["UPLOAD_FOLDER"], f"{word}.mp3")
    myobj.save(fname)
    return fname

@app.route("/")
def index():
    """Render the main game page."""
    # Initialize session variables if they don't exist
    if "score" not in session:
        session["score"] = 0
        session["correct_words"] = []
        session["wrong_words"] = []
    return render_template("index.html", score=session["score"], correct_words=session["correct_words"], wrong_words=session["wrong_words"])

@app.route("/play", methods=["POST"])
def play():
    """Handle word playback and user input."""
    words = load_word_list()
    word = random.choice(words)
    fname = create_sound_file(word)
    return render_template("play.html", word=word, audio_file=fname)

@app.route("/check", methods=["POST"])
def check():
    """Check the user's spelling and update the score."""
    user_input = request.form.get("user_input")
    word = request.form.get("word")
    audio_file = request.form.get("audio_file")

    if user_input == "?":
        return render_template("play.html", word=word, audio_file=audio_file, replay=True)
    elif user_input == word:
        # Update session data for correct answer
        session["score"] += 1
        session["correct_words"].append(word)
        session.modified = True  # Ensure the session is saved
        return render_template("result.html", result="Correct!", word=word, score=session["score"], correct_words=session["correct_words"], wrong_words=session["wrong_words"])
    else:
        # Update session data for wrong answer
        session["wrong_words"].append(word)
        session.modified = True  # Ensure the session is saved
        return render_template("result.html", result="Wrong!", word=word, user_input=user_input, score=session["score"], correct_words=session["correct_words"], wrong_words=session["wrong_words"])

@app.route("/reset", methods=["POST"])
def reset():
    """Reset the session data."""
    session.clear()
    return redirect(url_for("index"))

@app.route("/static/word_files/<filename>")
def serve_audio(filename):
    """Serve audio files from the word_files directory."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)