/**
 * main.js
 * --------
 * Handles: drag-and-drop upload, file selection display,
 * form submission loading state, and general UI interactions.
 */

document.addEventListener('DOMContentLoaded', function () {

    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const dropZoneContent = document.getElementById('dropZoneContent');
    const fileSelected = document.getElementById('fileSelected');
    const selectedFileName = document.getElementById('selectedFileName');
    const selectedFileSize = document.getElementById('selectedFileSize');
    const uploadForm = document.getElementById('uploadForm');

    // Only run upload logic on the index page
    if (!dropZone || !fileInput) return;

    /* ──────────────────────────────────────────
       Drag and Drop Events
    ────────────────────────────────────────── */
    ['dragenter', 'dragover'].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            // Manually set files on the file input
            const dt = new DataTransfer();
            dt.items.add(files[0]);
            fileInput.files = dt.files;
            handleFileSelection(files[0]);
        }
    });

    /* ──────────────────────────────────────────
       File Input Change
    ────────────────────────────────────────── */
    fileInput.addEventListener('change', function () {
        if (fileInput.files.length > 0) {
            handleFileSelection(fileInput.files[0]);
        }
    });

    /* ──────────────────────────────────────────
       Handle file selected: show preview
    ────────────────────────────────────────── */
    function handleFileSelection(file) {
        const allowedExts = ['csv', 'xlsx', 'xls'];
        const ext = file.name.split('.').pop().toLowerCase();

        if (!allowedExts.includes(ext)) {
            showToast('Invalid file type. Please upload a CSV or Excel file.', 'error');
            resetUpload();
            return;
        }

        // Show file info
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatFileSize(file.size);
        dropZoneContent.style.display = 'none';
        fileSelected.style.display = 'flex';

        // Enable analyze button
        analyzeBtn.disabled = false;
    }

    /* ──────────────────────────────────────────
       Form submit: show loading spinner
    ────────────────────────────────────────── */
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            if (!fileInput.files.length) {
                e.preventDefault();
                showToast('Please select a file first.', 'error');
                return;
            }
            // Show loading state
            const btnText = analyzeBtn.querySelector('.btn-text');
            const btnLoading = analyzeBtn.querySelector('.btn-loading');
            if (btnText && btnLoading) {
                btnText.style.display = 'none';
                btnLoading.style.display = 'flex';
                analyzeBtn.disabled = true;
            }
        });
    }

    /* ──────────────────────────────────────────
       Utility: Format bytes to human-readable
    ────────────────────────────────────────── */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /* ──────────────────────────────────────────
       Utility: Simple toast notification
    ────────────────────────────────────────── */
    function showToast(message, type = 'error') {
        const container = document.querySelector('.flash-container') || createFlashContainer();
        const flash = document.createElement('div');
        flash.className = `flash flash-${type}`;
        flash.innerHTML = `
            <span class="flash-icon">${type === 'error' ? '✗' : '✓'}</span>
            <span>${message}</span>
            <button class="flash-close" onclick="this.parentElement.remove()">×</button>
        `;
        container.appendChild(flash);
        setTimeout(() => flash.remove(), 5000);
    }

    function createFlashContainer() {
        const div = document.createElement('div');
        div.className = 'flash-container';
        document.body.appendChild(div);
        return div;
    }
});

/**
 * resetUpload()
 * Resets the upload form to its initial state.
 * Called by the "remove" button on the file preview.
 */
function resetUpload() {
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const dropZoneContent = document.getElementById('dropZoneContent');
    const fileSelected = document.getElementById('fileSelected');

    if (fileInput) fileInput.value = '';
    if (analyzeBtn) analyzeBtn.disabled = true;
    if (dropZoneContent) dropZoneContent.style.display = '';
    if (fileSelected) fileSelected.style.display = 'none';
}
