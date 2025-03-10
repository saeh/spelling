from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify
from gtts import gTTS
import os
import random
import json
from datetime import timedelta

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/word_files"
app.secret_key = "your_secret_key_here"  # Required for session management
app.permanent_session_lifetime = timedelta(minutes=30)  # Session expires after 30 minutes

# Leaderboard file path
LEADERBOARD_FILE = "leaderboard.json"

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

def calculate_correct_percentage(correct_words, wrong_words):
    """Calculate the percentage of correct words."""
    total_words = len(correct_words) + len(wrong_words)
    if total_words == 0:
        return 0
    return (len(correct_words) / total_words) * 100

def load_leaderboard():
    """Load the leaderboard from the JSON file."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as fp:
            return json.load(fp)
    return []

def save_leaderboard(leaderboard):
    """Save the leaderboard to the JSON file."""
    with open(LEADERBOARD_FILE, "w") as fp:
        json.dump(leaderboard, fp, indent=4)

# Load the leaderboard when the app starts
leaderboard = load_leaderboard()

@app.route("/", methods=["GET", "POST"])
def index():
    """Render the main game page or handle name submission."""
    if request.method == "POST":
        # Save the user's name in the session
        session["name"] = request.form.get("name")
        return redirect(url_for("game"))
    return render_template("index.html")

@app.route("/set_name", methods=["POST"])
def set_name():
    """Set the user's name in the session from localStorage."""
    data = request.get_json()
    session["name"] = data.get("name")
    return jsonify({"status": "success"}), 200

@app.route("/game")
def game():
    """Render the game page."""
    if "name" not in session:
        return redirect(url_for("index"))
    # Initialize session variables if they don't exist
    if "score" not in session:
        session["score"] = 0
        session["correct_words"] = []
        session["wrong_words"] = []
    correct_percentage = calculate_correct_percentage(session["correct_words"], session["wrong_words"])
    return render_template("game.html", score=session["score"], correct_words=session["correct_words"], wrong_words=session["wrong_words"], correct_percentage=correct_percentage, leaderboard=leaderboard)

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
    else:
        # Update session data for wrong answer
        session["wrong_words"].append(word)
        session.modified = True  # Ensure the session is saved

    # Calculate correct percentage
    correct_percentage = calculate_correct_percentage(session["correct_words"], session["wrong_words"])
    return render_template("result.html", result="Correct!" if user_input == word else "Wrong!", word=word, user_input=user_input, score=session["score"], correct_words=session["correct_words"], wrong_words=session["wrong_words"], correct_percentage=correct_percentage)

@app.route("/reset", methods=["POST"])
def reset():
    """Reset the session data and add the user's score to the leaderboard."""
    if "name" in session and "score" in session:
        leaderboard.append({
            "name": session["name"],
            "score": session["score"],
            "correct_percentage": calculate_correct_percentage(session["correct_words"], session["wrong_words"])
        })
        # Sort leaderboard by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        # Save the updated leaderboard to the file
        save_leaderboard(leaderboard)
    session.clear()
    return redirect(url_for("index"))

@app.route("/static/word_files/<filename>")
def serve_audio(filename):
    """Serve audio files from the word_files directory."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)