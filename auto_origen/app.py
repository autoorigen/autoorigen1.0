import os

from autoorigen import create_app
from autoorigen.extensions import socketio

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("DEBUG", "0") == "1"
    socketio.run(app, host="0.0.0.0", port=5000, debug=debug, allow_unsafe_werkzeug=True)
