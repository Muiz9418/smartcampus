import os
from flask import Blueprint, send_from_directory, jsonify, current_app

frontend_bp = Blueprint('frontend', __name__)


def _frontend_dir():
    return os.path.join(current_app.root_path, 'frontend')


@frontend_bp.route('/')
def index():
    return send_from_directory(_frontend_dir(), 'index.html')


@frontend_bp.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(_frontend_dir(), 'css'), filename)


@frontend_bp.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(_frontend_dir(), 'js'), filename)


@frontend_bp.route('/components/<path:filename>')
def serve_components(filename):
    return send_from_directory(os.path.join(_frontend_dir(), 'components'), filename)


@frontend_bp.route('/pages/<path:filename>')
def serve_pages(filename):
    return send_from_directory(os.path.join(_frontend_dir(), 'pages'), filename)


@frontend_bp.route('/<path:path>')
def serve_spa(path):
    if path.startswith('api/'):
        return jsonify(error="Not found"), 404
    return send_from_directory(_frontend_dir(), 'index.html')
