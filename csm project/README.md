# ☁️ Cloud Backup Tracker - Full-Stack College Mini Project

A modern, responsive, and fully functional **Cloud Backup Tracker** web application developed for college project submissions, coursework evaluations, expo displays, and viva presentations.

Built using **HTML5, CSS3, Vanilla JavaScript, Python Flask, and SQLite3**.

---

## 🖼️ Prototype & UI Design Board

The project includes an ultra-high-definition 16:9 presentation board image displaying all 6 application screens in a clean 3×2 grid layout:
- **`cloud_backup_tracker_prototype.png`** (2560×1440 resolution, located in the project root folder)

---

## 🌟 The 6 Core Website Screens

### 1. Login / Sign Up Page (`/login`, `/signup`)
- **Branding**: Cloud Backup Tracker logo with cloud upload icon and tagline *"Your files. Safe in the cloud. Track • Backup • Restore"*.
- **Interactive Tabs**: Toggle between **Login** and **Sign Up**.
- **Form Controls**: Email address and password input fields with inline icons and visibility indicators.
- **Options**: Remember me checkbox and working "Forgot password?" prompt.
- **Google Sign-In**: 1-Click "Continue with Google" button for instant demo evaluation.
- **Security Badge**: SHA-256 Vault Encryption indicator.

### 2. Dashboard Overview (`/dashboard`)
- **Welcome Banner**: Personalized greeting: *"Hello, Dharshini! 👋 Here's your real-time cloud backup summary"*.
- **4 Key Stat Cards**:
  1. **Total Backups**: Real-time count of files safely stored in the cloud.
  2. **Total Storage Used**: Total storage consumed (e.g. 248 MB).
  3. **Last Backup Date**: Date and timestamp of most recent backup (e.g. Oct 25, 2025).
  4. **Storage Quota Usage**: Progress bar showing consumed capacity versus total quota (e.g. 12% of 2 GB).
- **Recent Backups Table**: Displays latest file name, category badge, size, backup timestamp, and green *"● Backed up"* status badge.
- **Cloud Audit Ledger**: Chronological timeline of file syncs, downloads, and system configurations.

### 3. Upload Backup (`/upload`)
- **Drag-and-Drop Area**: Dashed border zone with cloud upload icon and *"Choose Files"* button.
- **Target Selection**: Deploy backups to AWS S3, Google Cloud, Azure Blob, or Local Cloud Vault.
- **Security Options**: AES-256 GCM encryption and automated SHA-256 integrity hash verification.
- **Upload Progress Tracker**: Live progress bar displaying percentage (e.g. 70%), transfer speed, file size, and status feedback.
- **Backend Persistence**: Files are stored in `static/uploads/` and recorded in SQLite.

### 4. My Files (`/files`)
- **Complete Inventory**: Full list of backed-up documents, archives, images, presentations, and code files.
- **Real-Time Client Search**: Instant search filtering as you type without page reloads.
- **File Details**: File name with categorized icons (PDF, Text, Zip, PPT, Image), size, and backup timestamp.
- **Action Buttons**: Direct file download and permanent delete option with confirmation.

### 5. Restore Files (`/restore`)
- **Point-in-Time Recovery**: Dedicated screen to recover files from the cloud vault.
- **Search & Filter**: Find any backed-up version quickly.
- **Working Restore Button**: Bright blue **"[Restore]"** button on each row that verifies file integrity, logs a "File Restored" activity in SQLite, and triggers browser file download.

### 6. Settings & Preferences (`/settings`)
- **Account Profile**: Displays user profile name (*Dharshini*), email (*dharshini@gmail.com*), and working modals to update profile details or change password.
- **Cloud Storage Allocation**: Visual gauge of used storage vs. quota limit, plus an **"Upgrade Plan"** modal to change storage quotas (2 GB, 10 GB, 50 GB) with instant SQLite updates.
- **Notification Preferences**: Interactive toggles for *"Email notifications"* and *"Daily backup reminder"*, persisted directly into the SQLite database.
- **Cloud Diagnostics**: Latency ping test simulator for AWS, GCP, Azure, and Local Vault.
- **Reset Demo Data**: 1-click button to reset the database to the original 6 prototype records.

---

## 📂 Project Architecture

```text
csm project/
│
├── app.py                            # Flask server (routes, auth sessions, REST APIs)
├── database.py                       # SQLite database layer (queries, stats, migrations)
├── cloud_backup.db                   # SQLite database file
├── requirements.txt                  # Python dependencies (Flask, Werkzeug)
├── run.bat                           # 1-Click launcher script for Windows
├── README.md                         # Documentation and Viva preparation guide
├── prototype_board.html              # HTML source of 3x2 UI prototype board
├── cloud_backup_tracker_prototype.png # 2560x1440 16:9 UI prototype image
│
├── static/
│   ├── css/
│   │   └── style.css                 # Responsive stylesheet & design system
│   ├── js/
│   │   └── main.js                   # AJAX file upload, real-time search, toasts, modals
│   └── uploads/                      # Local cloud vault storage folder
│
└── templates/
    ├── base.html                     # Base layout with navy sidebar, topbar, and toasts
    ├── login.html                    # Screen 1: Login / Sign Up page
    ├── dashboard.html                # Screen 2: Dashboard metrics and recent backups
    ├── upload.html                   # Screen 3: Drag-and-drop file upload interface
    ├── files.html                    # Screen 4: My Files inventory with search
    ├── restore.html                  # Screen 5: Restore files page with restore buttons
    └── settings.html                 # Screen 6: Account profile, quota upgrade, alerts
```

---

## 🚀 How to Run the Website

### Method 1: 1-Click Launcher (Windows)
1. Double-click **`run.bat`** in the project folder.
2. It will automatically verify Python and Flask, launch the server, and open `http://127.0.0.1:5000` in Google Chrome!

### Method 2: Command Line
```powershell
pip install -r requirements.txt
python app.py
```
Open **`http://127.0.0.1:5000`** in your web browser.

**Default Login Credentials:**
- **Email:** `dharshini@gmail.com`
- **Password:** `password123`
*(Or simply click "Continue with Google" for instant demo evaluation)*

---

## 🎓 Viva Questions & Answers for College Expo

**Q1: What is the purpose of this project?**
> **A:** The Cloud Backup Tracker provides centralized tracking, secure AES-256 cloud vault storage, real-time synchronization monitoring, SHA-256 integrity verification, and point-in-time restoration for enterprise or personal files across multi-cloud destinations (AWS S3, Google Cloud, Azure Blob, and Local Vault).

**Q2: How does the application verify that a restored file is authentic and uncorrupted?**
> **A:** Every file uploaded generates a 256-bit cryptographic SHA-256 checksum stored in the SQLite database. When the file is restored or inspected, the hash is matched against the original checksum to guarantee that no bit rot, tampering, or data corruption occurred during transfer.

**Q3: Which database is used and why?**
> **A:** SQLite3 is used because it is lightweight, serverless, ACID-compliant, self-contained, and requires zero external database installation, making it ideal for self-hosted applications and viva demonstrations.
