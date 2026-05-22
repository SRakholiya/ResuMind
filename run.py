"""Entry point for the ResuMind Flask app.

Run with:  python run.py
Then open: http://127.0.0.1:2500
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Port 2500 to avoid macOS AirPlay Receiver conflict on 5050
    app.run(host="127.0.0.1", port=2500, debug=True)
