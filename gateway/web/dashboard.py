from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

from gateway.api.redfish import bp as redfish_bp
app.register_blueprint(redfish_bp)


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config['SECRET_KEY'] = 'replace-with-secure-key'
    socketio = SocketIO(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"status":"ok"})

    @socketio.on("connect")
    def handle_connect():
        print("Client connected")

    app.socketio = socketio
    return app
