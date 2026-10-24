"""
app.py - Main Flask Application for Cloud Backup Tracker
Provides routes, RESTful APIs, file upload handlers, and server-rendered templates.
Designed for College CSM Mini Project Expo & Viva Evaluation.
"""

import os
import io
import csv
import time
import random
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for, 
    jsonify, send_from_directory, Response, flash, session
)
import database

# Initialize Flask app
app = Flask(__name__)
# Use environment variable for secret key in production, with fallback for local development
app.secret_key = os.environ.get('SECRET_KEY', 'cloud-backup-tracker-secret-key-csm-expo-2026')
app.config['UPLOAD_FOLDER'] = database.UPLOADS_DIR
# Configurable upload limit (default 50 MB for safe cloud deployment)
max_upload_mb = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 50))
app.config['MAX_CONTENT_LENGTH'] = max_upload_mb * 1024 * 1024

# Ensure database is initialized on startup
with app.app_context():
    database.init_db(seed_sample_data=True)

# -------------------------------------------------------------
# Template Filters & Context Processors
# -------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Inject basic system status and current user info into all templates."""
    stats = database.get_stats()
    
    # Current user session or configurable demo user
    default_name = os.environ.get('DEMO_USER_NAME', 'Dharshini')
    default_email = os.environ.get('DEMO_USER_EMAIL', 'dharshini@gmail.com')
    user_name = session.get('user_name', default_name)
    user_email = session.get('user_email', default_email)
    is_logged_in = session.get('user_id') is not None
    
    notif_prefs = database.get_notification_preferences()

    return dict(
        system_stats=stats,
        current_user_name=user_name,
        current_user_email=user_email,
        is_logged_in=is_logged_in,
        notif_prefs=notif_prefs,
        current_year=2026
    )

# -------------------------------------------------------------
# Authentication Routes (Screen 1: Login / Sign Up Page)
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and form handler."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'

        # If empty, default to demo credentials from environment
        default_email = os.environ.get('DEMO_USER_EMAIL', 'dharshini@gmail.com')
        default_pass = os.environ.get('DEMO_USER_PASSWORD', 'password123')
        if not email:
            email = default_email
            password = default_pass

        user = database.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session.permanent = remember
            flash(f"Welcome back, {user['name']}! Cloud sync is active.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash(f"Invalid email or password. Demo login: {default_email} / {default_pass}", "danger")

    return render_template('login.html', page_title="Login / Sign Up", tab='login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up page and registration handler."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash("Please fill in all registration fields.", "warning")
            return render_template('login.html', page_title="Login / Sign Up", tab='signup')

        user_id = database.create_user(name, email, password)
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash(f"Account created successfully! Welcome to Cloud Backup Tracker, {name}.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("An account with this email address already exists.", "danger")

    return render_template('login.html', page_title="Login / Sign Up", tab='signup')

@app.route('/auth/google')
def auth_google():
    """One-click simulated Google Sign-In for demo."""
    demo_email = os.environ.get('DEMO_USER_EMAIL', 'dharshini@gmail.com')
    demo_name = os.environ.get('DEMO_USER_NAME', 'Dharshini')
    user = database.get_user_by_email(demo_email)
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
    else:
        session['user_id'] = 1
        session['user_name'] = demo_name
        session['user_email'] = demo_email
    flash("Signed in with Google successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Clear session and log out."""
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for('login'))

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Simulated password reset email trigger."""
    data = request.get_json() or {}
    email = data.get('email', 'dharshini@gmail.com')
    return jsonify({
        'success': True,
        'message': f"Password reset instructions have been sent to {email}."
    })

# -------------------------------------------------------------
# Main Application Pages (Screens 2 to 6)
# -------------------------------------------------------------
@app.route('/')
def index():
    """Root redirect to dashboard."""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Screen 2: Dashboard Overview."""
    stats = database.get_stats()
    recent_backups = database.get_all_backups()[:5]
    recent_logs = database.get_recent_activity(limit=5)
    return render_template(
        'dashboard.html',
        page_title="Dashboard",
        active_page="dashboard",
        stats=stats,
        recent_backups=recent_backups,
        recent_logs=recent_logs
    )

@app.route('/upload')
def upload_page():
    """Screen 3: Upload Backup."""
    stats = database.get_stats()
    return render_template(
        'upload.html',
        page_title="Upload Backup",
        active_page="upload",
        stats=stats
    )

@app.route('/files')
def files_page():
    """Screen 4: My Files (All backed-up files)."""
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', 'All')
    files = database.get_all_backups(search=search_query, category=category)
    stats = database.get_stats()
    return render_template(
        'files.html',
        page_title="My Files",
        active_page="files",
        files=files,
        stats=stats,
        search_query=search_query
    )

@app.route('/restore')
def restore_page():
    """Screen 5: Restore Files."""
    search_query = request.args.get('search', '').strip()
    files = database.get_all_backups(search=search_query)
    stats = database.get_stats()
    return render_template(
        'restore.html',
        page_title="Restore Files",
        active_page="restore",
        files=files,
        stats=stats,
        search_query=search_query
    )

@app.route('/settings')
def settings_page():
    """Screen 6: Settings & Preferences."""
    stats = database.get_stats()
    user_id = session.get('user_id', 1)
    user = database.get_user_by_id(user_id) or {
        'name': 'Dharshini',
        'email': 'dharshini@gmail.com',
        'role': 'Student / Project Lead'
    }
    notif_prefs = database.get_notification_preferences()
    return render_template(
        'settings.html',
        page_title="Settings",
        active_page="settings",
        user=user,
        stats=stats,
        notif_prefs=notif_prefs
    )

# -------------------------------------------------------------
# RESTful API Endpoints (Dynamic Ajax Actions)
# -------------------------------------------------------------
@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle asynchronous file upload, SHA-256 calculation, and database record."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part found in request'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected for upload'}), 400

    original_filename = secure_filename(uploaded_file.filename)
    if not original_filename:
        original_filename = f"backup_{int(time.time())}.bin"

    cloud_provider = request.form.get('cloud_provider', 'AWS S3')
    storage_tier = request.form.get('storage_tier', 'Standard')
    notes = request.form.get('notes', 'Uploaded via Web Interface')

    # Save to disk
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
    try:
        uploaded_file.save(save_path)
        file_size = os.path.getsize(save_path)

        # SHA-256 Checksum
        checksum = database.calculate_checksum(save_path)

        # Database record
        backup_id = database.add_backup_record(
            filename=original_filename,
            original_name=original_filename,
            file_size=file_size,
            cloud_provider=cloud_provider,
            storage_tier=storage_tier,
            status='Backed up',
            checksum=checksum,
            notes=notes
        )

        return jsonify({
            'success': True,
            'message': f"Successfully backed up '{original_filename}' to {cloud_provider}!",
            'backup_id': backup_id,
            'filename': original_filename,
            'file_size': database.format_file_size(file_size),
            'checksum': checksum,
            'provider': cloud_provider,
            'status': 'Backed up'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f"Upload failed: {str(e)}"}), 500

@app.route('/api/check-file/<int:backup_id>')
def api_check_file(backup_id):
    """Verify that a backup record and its physical file exist before initiating download."""
    backup = database.get_backup_by_id(backup_id)
    if not backup:
        return jsonify({'exists': False, 'message': 'Backup record not found in database.'}), 404

    filename = backup['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        database.log_activity("File Check", "Failed", f"Vault file missing for '{backup['original_name']}'")
        return jsonify({'exists': False, 'message': f"File '{backup['original_name']}' was not found in vault storage."}), 404

    return jsonify({
        'exists': True,
        'filename': backup['original_name'],
        'file_size': backup['file_size_formatted'],
        'download_url': url_for('download_file', backup_id=backup_id)
    })

@app.route('/download/<int:backup_id>')
def download_file(backup_id):
    """Download backup file from vault with original filename and attachment headers."""
    backup = database.get_backup_by_id(backup_id)
    if not backup:
        flash("Requested backup record not found.", "danger")
        return redirect(request.referrer or url_for('dashboard')), 404

    filename = backup['filename']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # If file is missing on disk, report a clear error instead of pretending it succeeded
    if not os.path.exists(file_path):
        database.log_activity("File Download", "Failed", f"Download failed: '{backup['original_name']}' missing on disk")
        flash(f"Error: File '{backup['original_name']}' is not present in vault storage.", "danger")
        return redirect(request.referrer or url_for('dashboard')), 404

    database.log_activity("File Download", "Success", f"Downloaded {backup['original_name']} ({backup['file_size_formatted']})")

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name=backup['original_name']
    )

@app.route('/api/restore/<int:backup_id>', methods=['POST', 'GET'])
def api_restore(backup_id):
    """Trigger file restoration and audit logging."""
    success, message = database.restore_backup_record(backup_id)
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'download_url': url_for('download_file', backup_id=backup_id)
        })
    else:
        return jsonify({'success': False, 'message': message}), 404

@app.route('/api/backup/<int:backup_id>', methods=['DELETE', 'POST'])
def api_delete_backup(backup_id):
    """Delete a backup item permanently."""
    success = database.delete_backup_record(backup_id)
    if success:
        return jsonify({'success': True, 'message': 'Backup deleted successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to delete backup.'}), 404

@app.route('/api/user/profile', methods=['POST'])
def api_update_profile():
    """Update profile name and email."""
    data = request.get_json() or request.form
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()

    if not name or not email:
        return jsonify({'success': False, 'message': 'Name and Email cannot be empty.'}), 400

    user_id = session.get('user_id', 1)
    if database.update_user_profile(user_id, name, email):
        session['user_name'] = name
        session['user_email'] = email
        return jsonify({'success': True, 'message': 'Profile updated successfully!', 'name': name, 'email': email})
    else:
        return jsonify({'success': False, 'message': 'Email is already in use by another account.'}), 400

@app.route('/api/user/password', methods=['POST'])
def api_update_password():
    """Change password for user."""
    data = request.get_json() or request.form
    new_password = data.get('new_password', '').strip()

    if len(new_password) < 4:
        return jsonify({'success': False, 'message': 'Password must be at least 4 characters long.'}), 400

    user_id = session.get('user_id', 1)
    database.update_user_password(user_id, new_password)
    return jsonify({'success': True, 'message': 'Password updated successfully!'})

@app.route('/api/settings/notifications', methods=['POST'])
def api_update_notifications():
    """Toggle notification preferences."""
    data = request.get_json() or {}
    email_notif = bool(data.get('email_notifications', True))
    reminder_notif = bool(data.get('daily_reminder', True))

    database.update_notification_preferences(email_notif, reminder_notif)
    return jsonify({
        'success': True,
        'message': 'Notification preferences saved.',
        'email_notifications': email_notif,
        'daily_reminder': reminder_notif
    })

@app.route('/api/settings/quota', methods=['POST'])
def api_update_quota():
    """Update total storage quota."""
    data = request.get_json() or {}
    quota_val = data.get('quota_gb', 2)
    try:
        quota_num = float(quota_val)
        database.set_setting('total_quota_gb', str(quota_num))
        database.log_activity("Storage Upgrade", "Success", f"Upgraded storage quota to {quota_num} GB")
        stats = database.get_stats()
        return jsonify({
            'success': True,
            'message': f"Cloud storage quota successfully upgraded to {quota_num} GB!",
            'stats': stats
        })
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid quota value.'}), 400

@app.route('/api/test-connection', methods=['POST'])
def api_test_connection():
    """Simulate cloud ping latency diagnostic."""
    time.sleep(0.3)
    results = [
        {'provider': 'AWS S3 (us-east-1)', 'status': 'Connected', 'latency': f"{random.randint(24, 48)} ms", 'badge': 'success'},
        {'provider': 'Google Cloud (asia-south1)', 'status': 'Connected', 'latency': f"{random.randint(18, 38)} ms", 'badge': 'success'},
        {'provider': 'Azure Blob (centralindia)', 'status': 'Connected', 'latency': f"{random.randint(20, 42)} ms", 'badge': 'success'},
        {'provider': 'Local Vault (127.0.0.1:5000)', 'status': 'Active', 'latency': '< 1 ms', 'badge': 'success'}
    ]
    database.log_activity("Diagnostics", "Success", "Cloud provider ping latency test executed")
    return jsonify({'success': True, 'endpoints': results})

@app.route('/api/reset-demo', methods=['POST'])
def api_reset_demo():
    """Reset database to initial 6 prototype files."""
    database.reset_database_to_default()
    database.set_setting('total_quota_gb', '2')
    return jsonify({'success': True, 'message': 'Demo data restored to original prototype state.'})

# -------------------------------------------------------------
# Main Application Entrypoint & Browser Launcher
# -------------------------------------------------------------
def open_browser():
    """Wait briefly for server to bind socket, then open in Chrome or default browser."""
    time.sleep(1.2)
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    for p in chrome_paths:
        if os.path.exists(p):
            import subprocess
            subprocess.Popen([p, "http://127.0.0.1:5000"])
            return
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Cloud environments pass PORT dynamically; default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Auto-open browser only on local desktop development (not on Render/Linux cloud)
    is_cloud = os.environ.get('RENDER') or os.environ.get('DYNO') or os.environ.get('CI')
    if not is_cloud and (os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not debug_mode):
        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    demo_email = os.environ.get('DEMO_USER_EMAIL', 'dharshini@gmail.com')
    demo_pass = os.environ.get('DEMO_USER_PASSWORD', 'password123')

    print("=" * 60)
    print("  ☁️  Cloud Backup Tracker - Functional SaaS Web App")
    print(f"  📍 Server running at http://0.0.0.0:{port}")
    if not is_cloud:
        print("  🌐 Auto-launching in Google Chrome...")
    print(f"  👤 Default Login: {demo_email} / {demo_pass}")
    print("=" * 60)
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
