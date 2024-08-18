from flask import Flask
from .routes import main

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'  # Change this to a real secret key

    from .routes import main
    from .oauth import oauth_blueprint

    # Register Blueprints (modularized routes)
    app.register_blueprint(main)
    app.register_blueprint(oauth_blueprint)

    return app
