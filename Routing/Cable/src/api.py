"""
Ultra-Lightweight Web API for Smart Search
"""
from functools import wraps
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from .search_engine import SmartSearchOrchestrator

def validate_search_query(query: str) -> bool:
    """Validate search query to prevent injection attacks"""
    if not query or len(query) > 200:  # Reasonable length limit
        return False
    # Allow alphanumeric, spaces, and some special characters.
    if not re.match(r'^[\w\s\-\.\?]+$', query):
        return False
    return True

def create_web_interface(config_path: str = "config/settings.yaml"):
    """Create and configure the Flask app"""
    app = Flask(__name__)

    # Initialize extensions
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )
    Talisman(app)

    search_engine = SmartSearchOrchestrator(config_path)

    api_key = search_engine.config.get('api', {}).get('secret_key')

    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.headers.get('X-Api-Key') != api_key:
                abort(401, description='Invalid or missing API key.')
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/search', methods=['GET'])
    @require_api_key
    @limiter.limit("10 per minute")
    def search():
        """Search endpoint"""
        query = request.args.get('q', '')
        if not validate_search_query(query):
            abort(400, description="Invalid search query.")
        
        results = search_engine.search(query)
        return jsonify({
            'query': query,
            'results': results
        })

    @app.route('/stats', methods=['GET'])
    @require_api_key
    @limiter.limit("5 per minute")
    def stats():
        """Get search engine statistics"""
        return jsonify(search_engine.get_stats())

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy'})

    return app
