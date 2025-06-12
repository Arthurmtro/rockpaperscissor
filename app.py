from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid

app = Flask(__name__)

# In-memory store for sessions and choices
sessions = {}


def create_session_id():
    return uuid.uuid4().hex[:8]


def calculate_winner(choices):
    # choices: dict of name->choice
    signs = set(choices.values())
    if len(signs) == 1 or len(signs) == 3:
        return None  # tie
    if signs == {"rock", "scissors"}:
        return "rock"
    if signs == {"rock", "paper"}:
        return "paper"
    if signs == {"scissors", "paper"}:
        return "scissors"
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create", methods=["POST"])
def create():
    session_id = create_session_id()
    sessions[session_id] = {}
    return redirect(url_for("session_page", session_id=session_id))


@app.route("/session/<session_id>", methods=["GET"])
def session_page(session_id):
    if session_id not in sessions:
        return "Session not found", 404
    return render_template("session.html", session_id=session_id)


@app.route("/session/<session_id>/choose", methods=["POST"])
def choose(session_id):
    if session_id not in sessions:
        return "Session not found", 404
    name = request.form.get("name", "Anonymous")
    choice = request.form.get("choice")
    if choice not in ("rock", "paper", "scissors"):
        return "Invalid choice", 400
    sessions[session_id][name] = choice
    return redirect(url_for("results", session_id=session_id))


@app.route("/session/<session_id>/results")
def results(session_id):
    if session_id not in sessions:
        return "Session not found", 404
    choices = sessions[session_id]
    winner_sign = calculate_winner(choices)
    winners = [name for name, c in choices.items() if c == winner_sign] if winner_sign else []
    return render_template(
        "results.html",
        session_id=session_id,
        choices=choices,
        winner_sign=winner_sign,
        winners=winners,
    )


@app.route("/session/<session_id>/status")
def status(session_id):
    if session_id not in sessions:
        return jsonify({"error": "not found"}), 404
    choices = sessions[session_id]
    winner_sign = calculate_winner(choices)
    winners = [name for name, c in choices.items() if c == winner_sign] if winner_sign else []
    return jsonify({"choices": choices, "winner_sign": winner_sign, "winners": winners})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
