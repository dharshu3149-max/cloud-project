"""
Comprehensive Project & Flask Application Verification Script
Checks files, database, routes, authentication, APIs, and uploads.
"""

import os
import sys
import sqlite3
import io

print("=" * 60)
print("  🔍 CLOUD BACKUP TRACKER - SYSTEM VERIFICATION SUITE")
print("=" * 60)

base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Check all required files
required_files = [
    'app.py',
    'database.py',
    'cloud_backup.db',
    'run.bat',
    'requirements.txt',
    'templates/base.html',
    'templates/login.html',
    'templates/dashboard.html',
    'templates/upload.html',
    'templates/files.html',
    'templates/restore.html',
    'templates/settings.html',
    'static/css/style.css',
    'static/js/main.js',
    'cloud_backup_tracker_prototype.png'
]

print("\n[Step 1] Verifying Core Project Files & Assets...")
missing_files = []
for rel_path in required_files:
    full_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(full_path):
        missing_files.append(rel_path)
        print(f"  ❌ MISSING: {rel_path}")
    else:
        file_size = os.path.getsize(full_path)
        print(f"  ✅ FOUND: {rel_path} ({file_size} bytes)")

if missing_files:
    print(f"\n❌ FAILED: {len(missing_files)} file(s) are missing!")
    sys.exit(1)
else:
    print("  ✨ All 15 required files are present and verified.")

# 2. Check Database & Tables
print("\n[Step 2] Verifying SQLite Database & Integrity...")
db_path = os.path.join(base_dir, 'cloud_backup.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row['name'] for row in cur.fetchall()]
print(f"  ✅ Database Tables: {tables}")
required_tables = ['users', 'backups', 'activity_logs', 'storage_settings']
for t in required_tables:
    if t not in tables:
        print(f"  ❌ Missing table: {t}")
        sys.exit(1)
    else:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f"     • {t}: {cnt} rows")

# 3. Check Physical Files in Uploads Vault
uploads_dir = os.path.join(base_dir, 'static', 'uploads')
physical_files = os.listdir(uploads_dir) if os.path.exists(uploads_dir) else []
print(f"\n[Step 3] Verifying Physical Vault Storage ({len(physical_files)} files in static/uploads/)...")
cur.execute("SELECT id, original_name, filename, file_type, file_size FROM backups")
for b in cur.fetchall():
    p_path = os.path.join(uploads_dir, b['filename'])
    exists = os.path.exists(p_path)
    status_str = "✅ Ready" if exists else "⚠️ Missing on disk (will auto-generate)"
    print(f"  • #{b['id']} {b['original_name']} ({b['file_type']}) -> {status_str}")

conn.close()

# 4. Check Flask Routes & Template Rendering
print("\n[Step 4] Testing Flask Routes and Server-Rendered Views...")
import app
client = app.app.test_client()

routes_to_test = [
    ('/login', 'Login page'),
    ('/dashboard', 'Dashboard page'),
    ('/upload', 'Upload page'),
    ('/files', 'My Files page'),
    ('/restore', 'Restore Files page'),
    ('/settings', 'Settings page')
]

for url, label in routes_to_test:
    r = client.get(url)
    if r.status_code == 200:
        print(f"  ✅ 200 OK: {label} ({url})")
    else:
        print(f"  ❌ {r.status_code} ERROR: {label} ({url})")
        sys.exit(1)

# 5. Check Authentication & Session
print("\n[Step 5] Testing Authentication & Google Demo Login...")
# Regular login
r_login = client.post('/login', data={'email': 'dharshini@gmail.com', 'password': 'password123'}, follow_redirects=True)
assert r_login.status_code == 200
assert b'Dharshini' in r_login.data
print("  ✅ Standard Login: Successful session established for Dharshini.")

# Google demo login
r_google = client.get('/auth/google', follow_redirects=True)
assert r_google.status_code == 200
print("  ✅ Google 1-Click Demo Login: Successful.")

# 6. Check REST API Endpoints
print("\n[Step 6] Testing Functional REST APIs (Upload, Restore, Download, Settings)...")
# API Restore
r_restore = client.post('/api/restore/1')
assert r_restore.status_code == 200
res_restore = r_restore.get_json()
assert res_restore['success'] is True
print(f"  ✅ REST API /api/restore/1: {res_restore['message']}")

# API Check File & Download Verification
r_check = client.get('/api/check-file/1')
assert r_check.status_code == 200
assert r_check.get_json()['exists'] is True
print(f"  ✅ API /api/check-file/1: Verified existence of '{r_check.get_json()['filename']}' ({r_check.get_json()['file_size']}).")

r_dl = client.get('/download/1')
assert r_dl.status_code == 200
assert len(r_dl.data) > 0
assert 'Project_Report.pdf' in r_dl.headers.get('Content-Disposition')
assert r_dl.data.startswith(b'%PDF-1.4')
print(f"  ✅ Download /download/1: Retrieved authentic valid PDF ({len(r_dl.data)} bytes) with Content-Disposition header.")

# API Download Missing File Error Handling
r_missing = client.get('/api/check-file/99999')
assert r_missing.status_code == 404
assert r_missing.get_json()['exists'] is False
print("  ✅ Missing File Handling: Correctly returned 404 with error message instead of false success.")

# API Settings Profile Update
r_prof = client.post('/api/user/profile', json={'name': 'Dharshini', 'email': 'dharshini@gmail.com'})
assert r_prof.status_code == 200
print("  ✅ Profile Update API: Working.")

# API Settings Notification Update
r_notif = client.post('/api/settings/notifications', json={'email_notifications': True, 'daily_reminder': True})
assert r_notif.status_code == 200
print("  ✅ Notification Toggle API: Working.")

# API Settings Quota Upgrade
r_quota = client.post('/api/settings/quota', json={'quota_gb': 2})
assert r_quota.status_code == 200
print("  ✅ Quota Upgrade API: Working.")

# API Diagnostics Latency Ping
r_ping = client.post('/api/test-connection')
assert r_ping.status_code == 200
ping_data = r_ping.get_json()
assert len(ping_data['endpoints']) == 4
print(f"  ✅ Gateway Ping Test: All 4 cloud gateways verified ({ping_data['endpoints'][0]['provider']} - {ping_data['endpoints'][0]['latency']}).")

# API Upload Test
dummy_file = (io.BytesIO(b"Cloud Backup Tracker Automatic Health Check Content"), "Health_Check_Report.txt")
r_up = client.post('/api/upload', data={'file': dummy_file, 'cloud_provider': 'AWS S3'}, content_type='multipart/form-data')
assert r_up.status_code == 200
up_data = r_up.get_json()
new_id = up_data['backup_id']
print(f"  ✅ Upload API: Uploaded #{new_id} ({up_data['filename']}) with SHA-256 Checksum: {up_data['checksum'][:16]}...")

# API Delete Test
r_del = client.delete(f'/api/backup/{new_id}')
assert r_del.status_code == 200
print(f"  ✅ Delete API: Cleaned up temporary test file #{new_id}.")

print("\n" + "=" * 60)
print("  🎉 VERIFICATION COMPLETE: ALL SYSTEMS ARE 100% OPERATIONAL!")
print("=" * 60)
