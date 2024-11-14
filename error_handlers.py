from flask_jwt_extended.exceptions import NoAuthorizationError
from flask import jsonify


def function_error_handler(app):
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(error):
        return jsonify({"message": "No autorizado"}), 401
