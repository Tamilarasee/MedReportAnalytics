import os
import logging
from flask import Flask
from routes.main_routes import main_bp

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Register blueprints
app.register_blueprint(main_bp)

logger.info("Medical Report Processing App initialized")
