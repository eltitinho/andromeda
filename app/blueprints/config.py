from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.mailgun import load_config, save_config

config_bp = Blueprint('config', __name__)

@config_bp.route('/mailgun')
@login_required
def mailgun_config():
    """Display Mailgun configuration form"""
    config = load_config()
    subdomain = config.get('mailgun_subdomain', 'noreply')
    return render_template('config/mailgun.html', subdomain=subdomain)

@config_bp.route('/mailgun', methods=['POST'])
@login_required
def mailgun_config_save():
    """Save Mailgun subdomain configuration"""
    subdomain = request.form.get('subdomain', '').strip().lower()
    
    if not subdomain:
        flash('Subdomain cannot be empty', 'error')
        return redirect(url_for('config.mailgun_config'))
    
    # Validate subdomain format (alphanumeric and hyphens only)
    if not all(c.isalnum() or c == '-' for c in subdomain):
        flash('Subdomain can only contain letters, numbers, and hyphens', 'error')
        return redirect(url_for('config.mailgun_config'))
    
    # Save configuration
    config = load_config()
    config['mailgun_subdomain'] = subdomain
    
    if save_config(config):
        flash(f'Mailgun subdomain "{subdomain}" saved successfully!', 'success')
    else:
        flash('Failed to save configuration. Please check file permissions.', 'error')
    
    return redirect(url_for('config.mailgun_config'))
