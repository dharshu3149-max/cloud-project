/**
 * main.js - Client-Side Interactive Engine for Cloud Backup Tracker
 * Handles AJAX file uploads, real-time table filtering, modals, toasts, and cloud actions.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    initUploadDropzone();
    initHistoryTableFilters();
    initBackupModals();
    initSettingsActions();
});

/* ==========================================================================
   1. Toast Notification Manager
   ========================================================================== */
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = `<svg width="20" height="20" fill="none" stroke="#10b981" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`;
    } else if (type === 'danger') {
        iconSvg = `<svg width="20" height="20" fill="none" stroke="#ef4444" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`;
    } else {
        iconSvg = `<svg width="20" height="20" fill="none" stroke="#f59e0b" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    }

    toast.innerHTML = `
        <div style="flex-shrink:0;">${iconSvg}</div>
        <div class="toast-message">${message}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/* ==========================================================================
   2. Mobile Responsive Navigation
   ========================================================================== */
function initMobileNav() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (mobileMenuBtn && sidebar && overlay) {
        const toggleSidebar = () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        };

        mobileMenuBtn.addEventListener('click', toggleSidebar);
        overlay.addEventListener('click', toggleSidebar);
    }
}

/* ==========================================================================
   3. File Upload & Drag-and-Drop Handling
   ========================================================================== */
function initUploadDropzone() {
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('fileInput');
    const previewBox = document.getElementById('selectedFilePreview');
    const uploadForm = document.getElementById('backupUploadForm');
    const uploadBtn = document.getElementById('submitUploadBtn');
    const progressWrapper = document.getElementById('uploadProgressWrapper');
    const progressBar = document.getElementById('uploadProgressBar');
    const progressText = document.getElementById('uploadProgressText');

    if (!dropzone || !fileInput) return;

    // Trigger file dialog on dropzone click
    dropzone.addEventListener('click', (e) => {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    // Drag-over styling
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
        });
    });

    // Drop handler
    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            fileInput.files = files;
            displayFilePreview(files[0]);
        }
    });

    // Input change handler
    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
            displayFilePreview(fileInput.files[0]);
        }
    });

    function displayFilePreview(file) {
        if (!previewBox) return;
        const nameEl = document.getElementById('previewFileName');
        const sizeEl = document.getElementById('previewFileSize');
        if (nameEl) nameEl.textContent = file.name;
        if (sizeEl) sizeEl.textContent = formatBytes(file.size);
        previewBox.style.display = 'flex';
    }

    // Clear file selection
    const clearBtn = document.getElementById('clearSelectedFile');
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.value = '';
            if (previewBox) previewBox.style.display = 'none';
        });
    }

    // Submit via AJAX with simulated progress
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!fileInput.files || fileInput.files.length === 0) {
                showToast('Please select a file to upload.', 'warning');
                return;
            }

            const formData = new FormData(uploadForm);
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = `
                <svg class="animate-spin" width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke-width="4" stroke="currentColor" stroke-dasharray="32" stroke-linecap="round"/>
                </svg>
                Encrypting & Syncing...
            `;

            if (progressWrapper && progressBar) {
                progressWrapper.style.display = 'block';
                progressBar.style.width = '15%';
                if (progressText) progressText.textContent = 'Preparing payload and calculating SHA-256...';
            }

            try {
                // Simulate progressive upload visually
                setTimeout(() => { if (progressBar) progressBar.style.width = '45%'; }, 300);
                setTimeout(() => { if (progressBar) progressBar.style.width = '80%'; }, 600);

                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (progressBar) progressBar.style.width = '100%';
                if (progressText) progressText.textContent = 'Backup successfully synced to cloud!';

                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => {
                        window.location.href = '/history';
                    }, 1200);
                } else {
                    showToast(data.message || 'Upload failed', 'danger');
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = `Start Cloud Backup`;
                }
            } catch (err) {
                showToast(`Upload error: ${err.message}`, 'danger');
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `Start Cloud Backup`;
            }
        });
    }
}

/* ==========================================================================
   4. Real-time Backup History Filters & Search
   ========================================================================== */
function initHistoryTableFilters() {
    const searchInput = document.getElementById('historySearchInput');
    const statusSelect = document.getElementById('statusFilterSelect');
    const providerSelect = document.getElementById('providerFilterSelect');
    const tableBody = document.getElementById('historyTableBody');

    if (!tableBody) return;

    function applyClientFilters() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const status = statusSelect ? statusSelect.value : 'All';
        const provider = providerSelect ? providerSelect.value : 'All';

        const rows = tableBody.querySelectorAll('tr[data-filename]');
        let visibleCount = 0;

        rows.forEach(row => {
            const rowFilename = (row.getAttribute('data-filename') || '').toLowerCase();
            const rowStatus = row.getAttribute('data-status') || '';
            const rowProvider = row.getAttribute('data-provider') || '';
            const rowChecksum = (row.getAttribute('data-checksum') || '').toLowerCase();
            const rowNotes = (row.getAttribute('data-notes') || '').toLowerCase();
            const rowCategory = (row.getAttribute('data-category') || '').toLowerCase();

            const matchesSearch = !query || 
                                  rowFilename.includes(query) || 
                                  rowChecksum.includes(query) || 
                                  rowNotes.includes(query) || 
                                  rowCategory.includes(query);

            const matchesStatus = status === 'All' || rowStatus === status;
            const matchesProvider = provider === 'All' || rowProvider === provider;

            if (matchesSearch && matchesStatus && matchesProvider) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        // Update count badge dynamically
        const badgeEl = document.getElementById('totalBackupsBadge');
        if (badgeEl) {
            if (query || status !== 'All' || provider !== 'All') {
                badgeEl.textContent = `Showing ${visibleCount} of ${rows.length} Backups`;
            } else {
                badgeEl.textContent = `${rows.length} Backups`;
            }
        }

        // Toggle "no matching records" placeholder
        let noRecordsRow = document.getElementById('noMatchingRecordsRow');
        if (visibleCount === 0) {
            if (!noRecordsRow) {
                noRecordsRow = document.createElement('tr');
                noRecordsRow.id = 'noMatchingRecordsRow';
                noRecordsRow.innerHTML = `
                    <td colspan="7" style="text-align: center; padding: 2.5rem; color: #64748b;">
                        <svg width="40" height="40" fill="none" stroke="#94a3b8" viewBox="0 0 24 24" style="margin-bottom:0.5rem; display:inline-block;">
                            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                        </svg>
                        <div style="font-weight: 600; font-size: 1rem; color: #1e293b;">No matching backup records found</div>
                        <div style="font-size: 0.85rem;">Try adjusting your search query or filter criteria.</div>
                    </td>
                `;
                tableBody.appendChild(noRecordsRow);
            } else {
                noRecordsRow.style.display = '';
            }
        } else if (noRecordsRow) {
            noRecordsRow.style.display = 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyClientFilters);
    }
    if (statusSelect) {
        statusSelect.addEventListener('change', applyClientFilters);
    }
    if (providerSelect) {
        providerSelect.addEventListener('change', applyClientFilters);
    }
}

/* ==========================================================================
   5. Backup Item Actions: View Details, Sync, Delete
   ========================================================================== */
function initBackupModals() {
    // Details Modal
    const detailsModal = document.getElementById('detailsModal');
    const deleteModal = document.getElementById('deleteModal');

    // Close buttons for modals
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            if (detailsModal) detailsModal.classList.remove('open');
            if (deleteModal) deleteModal.classList.remove('open');
        });
    });

    // Close on backdrop click
    [detailsModal, deleteModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.classList.remove('open');
            });
        }
    });

    // Delegate row actions
    document.addEventListener('click', async (e) => {
        // A) View Details
        const viewBtn = e.target.closest('[data-view-id]');
        if (viewBtn) {
            const backupId = viewBtn.getAttribute('data-view-id');
            await openBackupDetails(backupId);
            return;
        }

        // B) Sync / Re-try
        const syncBtn = e.target.closest('[data-sync-id]');
        if (syncBtn) {
            const backupId = syncBtn.getAttribute('data-sync-id');
            await triggerSyncBackup(backupId, syncBtn);
            return;
        }

        // C) Delete Backup
        const delBtn = e.target.closest('[data-delete-id]');
        if (delBtn) {
            const backupId = delBtn.getAttribute('data-delete-id');
            const backupName = delBtn.getAttribute('data-name') || 'this backup';
            openDeleteConfirmation(backupId, backupName);
            return;
        }
    });
}

async function openBackupDetails(backupId) {
    const modal = document.getElementById('detailsModal');
    if (!modal) return;

    try {
        const res = await fetch(`/api/backup/${backupId}`);
        const data = await res.json();
        if (data.success && data.backup) {
            const b = data.backup;
            document.getElementById('modalDetailName').textContent = b.original_name;
            document.getElementById('modalDetailSize').textContent = b.file_size_formatted;
            document.getElementById('modalDetailType').textContent = b.file_type;
            document.getElementById('modalDetailProvider').textContent = b.cloud_provider;
            document.getElementById('modalDetailTier').textContent = b.storage_tier;
            document.getElementById('modalDetailStatus').innerHTML = renderStatusBadge(b.status);
            document.getElementById('modalDetailChecksum').textContent = b.checksum || 'N/A';
            document.getElementById('modalDetailTime').textContent = b.upload_time;
            document.getElementById('modalDetailNotes').textContent = b.notes || 'None provided';
            
            const dlBtn = document.getElementById('modalDetailDownload');
            if (dlBtn) dlBtn.href = `/download/${b.id}`;

            modal.classList.add('open');
        }
    } catch (err) {
        showToast('Failed to load backup details', 'danger');
    }
}

function openDeleteConfirmation(backupId, backupName) {
    const modal = document.getElementById('deleteModal');
    if (!modal) return;

    const nameEl = document.getElementById('deleteTargetName');
    if (nameEl) nameEl.textContent = backupName;

    const confirmBtn = document.getElementById('confirmDeleteBtn');
    if (confirmBtn) {
        // Clear previous event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', async () => {
            newConfirmBtn.disabled = true;
            try {
                const res = await fetch(`/api/backup/${backupId}`, { method: 'DELETE' });
                const result = await res.json();

                if (result.success) {
                    modal.classList.remove('open');
                    showToast(result.message, 'success');
                    
                    // Animate row removal if present
                    const row = document.querySelector(`tr[data-backup-row-id="${backupId}"]`);
                    if (row) {
                        row.style.transition = 'all 0.3s ease';
                        row.style.opacity = '0';
                        row.style.transform = 'scale(0.95)';
                        setTimeout(() => row.remove(), 300);
                    } else {
                        setTimeout(() => location.reload(), 600);
                    }
                } else {
                    showToast(result.message || 'Failed to delete backup', 'danger');
                }
            } catch (err) {
                showToast(`Error: ${err.message}`, 'danger');
            } finally {
                newConfirmBtn.disabled = false;
            }
        });
    }

    modal.classList.add('open');
}

async function triggerSyncBackup(backupId, buttonElement) {
    if (buttonElement) {
        buttonElement.disabled = true;
        buttonElement.classList.add('animate-pulse');
    }

    try {
        const res = await fetch(`/api/backup/${backupId}/sync`, { method: 'POST' });
        const result = await res.json();

        if (result.success) {
            showToast(result.message, 'success');
            
            // Update the badge in the row
            const row = document.querySelector(`tr[data-backup-row-id="${backupId}"]`);
            if (row) {
                row.setAttribute('data-status', 'Success');
                const badgeContainer = row.querySelector('.status-badge-container');
                if (badgeContainer) {
                    badgeContainer.innerHTML = renderStatusBadge('Success');
                }
            }
        } else {
            showToast(result.message || 'Sync failed', 'danger');
        }
    } catch (err) {
        showToast(`Sync error: ${err.message}`, 'danger');
    } finally {
        if (buttonElement) {
            buttonElement.disabled = false;
            buttonElement.classList.remove('animate-pulse');
        }
    }
}

function renderStatusBadge(status) {
    if (status === 'Success') {
        return `<span class="badge badge-success"><svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg> Success</span>`;
    } else if (status === 'Pending' || status === 'In Progress') {
        return `<span class="badge badge-warning"><svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="3"/><polyline points="12 6 12 12 14 14" stroke-width="3"/></svg> Pending</span>`;
    } else {
        return `<span class="badge badge-danger"><svg width="12" height="12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18" stroke-width="3"/><line x1="6" y1="6" x2="18" y2="18" stroke-width="3"/></svg> Failed</span>`;
    }
}

/* ==========================================================================
   6. Cloud Settings & Diagnostics
   ========================================================================== */
function initSettingsActions() {
    // Quota Form
    const quotaForm = document.getElementById('quotaSettingsForm');
    if (quotaForm) {
        quotaForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const quotaInput = document.getElementById('quotaGbInput');
            const quotaVal = quotaInput ? quotaInput.value : 25;

            try {
                const res = await fetch('/api/settings/quota', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ quota_gb: quotaVal })
                });
                const result = await res.json();
                if (result.success) {
                    showToast(result.message, 'success');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast(result.message || 'Failed to update quota', 'danger');
                }
            } catch (err) {
                showToast(`Error: ${err.message}`, 'danger');
            }
        });
    }

    // Ping Test
    const testPingBtn = document.getElementById('testCloudEndpointsBtn');
    if (testPingBtn) {
        testPingBtn.addEventListener('click', async () => {
            testPingBtn.disabled = true;
            testPingBtn.textContent = 'Testing Cloud Gateways...';

            try {
                const res = await fetch('/api/test-connection', { method: 'POST' });
                const result = await res.json();

                if (result.success && result.endpoints) {
                    const listEl = document.getElementById('pingResultsList');
                    if (listEl) {
                        listEl.innerHTML = result.endpoints.map(ep => `
                            <div style="display:flex; justify-content:space-between; align-items:center; padding: 0.6rem 0; border-bottom: 1px solid #f1f5f9;">
                                <div>
                                    <div style="font-weight: 600; font-size: 0.88rem;">${ep.provider}</div>
                                    <div style="font-size: 0.75rem; color: #10b981;">Latency: ${ep.latency}</div>
                                </div>
                                <span class="badge badge-success">Online</span>
                            </div>
                        `).join('');
                    }
                    showToast('All Cloud Providers are reachable and active!', 'success');
                }
            } catch (err) {
                showToast('Failed to ping cloud endpoints', 'danger');
            } finally {
                testPingBtn.disabled = false;
                testPingBtn.textContent = 'Run Diagnostic Ping Test';
            }
        });
    }

    // Reset Demo Data
    const resetBtn = document.getElementById('resetDemoDataBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to reset all backups and restore default college project demo records?')) {
                try {
                    const res = await fetch('/api/reset-demo', { method: 'POST' });
                    const result = await res.json();
                    if (result.success) {
                        showToast(result.message, 'success');
                        setTimeout(() => location.href = '/dashboard', 1000);
                    }
                } catch (err) {
                    showToast(`Error: ${err.message}`, 'danger');
                }
            }
        });
    }
}

/* Helper to format bytes to KB, MB, GB */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Global restoreFile function for Dashboard and Restore Files pages
window.restoreFile = function(fileId, filename) {
    showToast(`Initiating cloud recovery for ${filename}...`, 'info');
    fetch(`/api/restore/${fileId}`, { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast(`Success: ${data.message}`, 'success');
            if (data.download_url) {
                setTimeout(() => {
                    window.location.href = data.download_url;
                }, 400);
            }
        } else {
            showToast(data.message, 'danger');
        }
    })
    .catch(err => {
        showToast("Restoration failed. Please check connection.", 'danger');
    });
};

// Global downloadBackup function for Recent Backups and My Files tables
window.downloadBackup = function(event, backupId, filename) {
    if (event) {
        event.preventDefault();
    }
    showToast(`Verifying '${filename}' from cloud vault...`, 'info');

    fetch(`/api/check-file/${backupId}`)
        .then(res => {
            if (!res.ok) {
                return res.json().then(errData => {
                    throw new Error(errData.message || `File '${filename}' is not available.`);
                });
            }
            return res.json();
        })
        .then(data => {
            if (data.exists) {
                showToast(`Downloading '${filename}' (${data.file_size}) — check your Downloads folder!`, 'success');
                // Trigger real browser download by creating and clicking a dynamic download anchor
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = data.download_url || `/download/${backupId}`;
                a.setAttribute('download', filename);
                document.body.appendChild(a);
                a.click();
                setTimeout(() => {
                    document.body.removeChild(a);
                }, 1000);
            } else {
                showToast(`Error: ${data.message || 'File not found on server.'}`, 'danger');
            }
        })
        .catch(err => {
            showToast(`Download Error: ${err.message}`, 'danger');
        });
};

window.showToast = showToast;

