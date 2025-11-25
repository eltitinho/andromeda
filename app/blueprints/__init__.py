# app/blueprints/__init__.py
from flask import Blueprint
from .auth import public_bp, private_bp
from .invoicing import invoicing_bp
from .tracking import public_tracking_bp, tracking_bp

def init_app(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(private_bp, url_prefix='/private')
    app.register_blueprint(invoicing_bp, url_prefix='/invoicing')
    app.register_blueprint(public_tracking_bp, url_prefix='/public_tracking')
    app.register_blueprint(tracking_bp, url_prefix='/tracking')