#!/usr/bin/env python3
"""
Atmosphere Arcade - Safety API
==============================

REST API endpoints for safety monitoring and user reporting.
Provides interfaces for:
- User safety reports
- Safety dashboard access
- Human oversight queue
- Safety configuration management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any
from safety_monitor import safety_monitor
from api.chatgpt_manager import ChatGPTManager

logger = logging.getLogger(__name__)

class SafetyAPI:
    """REST API for safety monitoring and reporting."""

    def __init__(self, app: Flask = None):
        self.app = app or Flask(__name__)
        CORS(self.app)  # Enable CORS for web interface

        # Initialize safety components
        self.chatgpt_manager = ChatGPTManager()
        self.monitor = safety_monitor

        self._register_routes()

    def _register_routes(self):
        """Register API routes."""

        @self.app.route('/api/safety/report', methods=['POST'])
        def submit_report():
            """Submit a user safety report."""
            try:
                data = request.get_json()

                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                user_id = data.get('user_id', 'anonymous')
                report_type = data.get('report_type', 'general')
                content = data.get('content', '')
                context = data.get('context', {})

                if not content.strip():
                    return jsonify({'error': 'Report content is required'}), 400

                result = self.monitor.submit_user_report(user_id, report_type, content, context)

                logger.info(f"User report submitted: {user_id} - {report_type}")

                return jsonify(result), 201

            except Exception as e:
                logger.error(f"Safety report submission failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/safety/dashboard', methods=['GET'])
        def get_dashboard():
            """Get safety dashboard data."""
            try:
                # Basic authentication check (in production, use proper auth)
                api_key = request.headers.get('X-API-Key')
                if not self._validate_api_key(api_key):
                    return jsonify({'error': 'Unauthorized'}), 401

                dashboard = self.monitor.get_safety_dashboard()
                return jsonify(dashboard), 200

            except Exception as e:
                logger.error(f"Dashboard access failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/safety/review-queue', methods=['GET'])
        def get_review_queue():
            """Get pending items for human review."""
            try:
                api_key = request.headers.get('X-API-Key')
                if not self._validate_api_key(api_key):
                    return jsonify({'error': 'Unauthorized'}), 401

                limit = int(request.args.get('limit', 50))
                queue = self.monitor.get_pending_reviews(limit)
                return jsonify({'queue': queue, 'count': len(queue)}), 200

            except Exception as e:
                logger.error(f"Review queue access failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/safety/feedback', methods=['POST'])
        def submit_feedback():
            """Submit human reviewer feedback."""
            try:
                api_key = request.headers.get('X-API-Key')
                if not self._validate_api_key(api_key):
                    return jsonify({'error': 'Unauthorized'}), 401

                data = request.get_json()

                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                reviewer_id = data.get('reviewer_id', 'unknown')
                content_id = data.get('content_id', '')
                feedback_type = data.get('feedback_type', 'general')
                comments = data.get('comments', '')
                approved = data.get('approved')

                if not content_id or not comments.strip():
                    return jsonify({'error': 'Content ID and comments are required'}), 400

                result = self.monitor.submit_human_feedback(
                    reviewer_id, content_id, feedback_type, comments, approved
                )

                logger.info(f"Human feedback submitted: {reviewer_id} - {content_id}")

                return jsonify(result), 201

            except Exception as e:
                logger.error(f"Feedback submission failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/safety/check-content', methods=['POST'])
        def check_content():
            """Check content for safety violations."""
            try:
                data = request.get_json()

                if not data or 'content' not in data:
                    return jsonify({'error': 'Content is required'}), 400

                content = data['content']
                user_context = data.get('user_context', {})

                # Validate input
                validation = self.chatgpt_manager.validate_input(content)

                # Check moderation
                moderation_result = None
                if validation['is_valid']:
                    # Note: In async context, this would need proper handling
                    # For now, return validation only
                    pass

                # Check if needs human review
                review_decision = self.monitor.should_flag_for_human_review(content, user_context)

                result = {
                    'validation': validation,
                    'moderation': moderation_result,
                    'human_review_required': review_decision['should_review'],
                    'risk_level': review_decision['risk_level'],
                    'review_reasons': review_decision['reasons']
                }

                return jsonify(result), 200

            except Exception as e:
                logger.error(f"Content check failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/safety/config', methods=['GET'])
        def get_safety_config():
            """Get current safety configuration."""
            try:
                api_key = request.headers.get('X-API-Key')
                if not self._validate_api_key(api_key):
                    return jsonify({'error': 'Unauthorized'}), 401

                config = {
                    'moderation_enabled': self.chatgpt_manager.moderation_enabled,
                    'input_limits': self.chatgpt_manager.get_safety_report()['input_limits'],
                    'moderation_thresholds': self.chatgpt_manager.moderation_thresholds,
                    'human_review_thresholds': self.monitor.human_review_thresholds,
                    'suspicious_patterns_count': len(self.chatgpt_manager.suspicious_patterns)
                }

                return jsonify(config), 200

            except Exception as e:
                logger.error(f"Config access failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

        @self.app.route('/api/safety/status', methods=['GET'])
        def get_safety_status():
            """Get overall safety system status."""
            try:
                status = {
                    'system_health': 'operational',
                    'chatgpt_manager': 'available' if self.chatgpt_manager else 'unavailable',
                    'moderation_api': 'enabled' if self.chatgpt_manager and self.chatgpt_manager.moderation_enabled else 'disabled',
                    'safety_monitoring': 'active',
                    'last_updated': self.monitor.get_safety_dashboard()['last_updated']
                }

                return jsonify(status), 200

            except Exception as e:
                logger.error(f"Status check failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500

    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key for admin endpoints."""
        # In production, this should check against a secure key store
        # For now, accept any key or check environment variable
        expected_key = os.getenv('SAFETY_API_KEY')
        if expected_key:
            return api_key == expected_key
        else:
            # For development, allow any key
            return bool(api_key)

    def run(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = False):
        """Run the safety API server."""
        print("🛡️ Atmosphere Arcade - Safety API")
        print("=" * 40)
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {debug}")
        print("\nEndpoints:")
        print("  POST /api/safety/report       - Submit user reports")
        print("  GET  /api/safety/dashboard    - Safety dashboard (admin)")
        print("  GET  /api/safety/review-queue - Human review queue (admin)")
        print("  POST /api/safety/feedback     - Human feedback (admin)")
        print("  POST /api/safety/check-content- Content safety check")
        print("  GET  /api/safety/config       - Safety config (admin)")
        print("  GET  /api/safety/status       - System status")
        print("\n🚀 Starting Safety API server...")

        self.app.run(host=host, port=port, debug=debug)

# Create global safety API instance
def create_safety_api(app=None):
    """Create and return a SafetyAPI instance."""
    return SafetyAPI(app)

if __name__ == "__main__":
    # Run standalone safety API server
    safety_api = SafetyAPI()
    safety_api.run()
