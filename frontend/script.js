document.addEventListener('DOMContentLoaded', () => {

    // --- TOAST SYSTEM ---
    const toastContainer = document.getElementById('toast-container');
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-exclamation-triangle';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        toastContainer.appendChild(toast);

        // Remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.4s forwards';
            setTimeout(() => {
                if(toast.parentElement) toast.parentElement.removeChild(toast);
            }, 400);
        }, 5000);
    }

    // --- NO LONGER NEEDED: DASHBOARD & NAVIGATION ---
    // (Removed to streamline for external users)




    // --- BRAIN ANIMATION ---
    function initBrain() {
        const brain = document.getElementById('neural-brain');
        if (!brain) return;

        // Clear existing nodes except core
        const core = brain.querySelector('.brain-core');
        brain.innerHTML = '';
        brain.appendChild(core);

        const nodeCount = 12;
        const radius = 60;

        for (let i = 0; i < nodeCount; i++) {
            const angle = (i / nodeCount) * Math.PI * 2;
            const x = Math.cos(angle) * radius + 60;
            const y = Math.sin(angle) * radius + 60;

            const node = document.createElement('div');
            node.className = 'neuron-node';
            node.style.left = `${x}px`;
            node.style.top = `${y}px`;
            node.style.animation = `pulseBrain ${1.5 + Math.random()}s infinite ease-in-out`;
            node.style.animationDelay = `${Math.random()}s`;
            brain.appendChild(node);

            // Create synapse to core
            const line = document.createElement('div');
            line.className = 'synapse-line';
            line.style.left = `60px`;
            line.style.top = `60px`;
            line.style.width = `${radius}px`;
            line.style.transform = `rotate(${angle}rad)`;
            brain.appendChild(line);
        }
    }



    // --- NEURAL ORACLE UPLOAD ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.querySelector('.upload-section');
    const processingState = document.getElementById('processing-state');
    const resultSection = document.getElementById('result-section');
    const resetBtn = document.getElementById('reset-btn');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => dropZone.addEventListener(eventName, e => {e.preventDefault(); e.stopPropagation();}, false));
    ['dragenter', 'dragover'].forEach(eventName => dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false));
    ['dragleave', 'drop'].forEach(eventName => dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false));

    dropZone.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', function() { handleFiles(this.files); });
    
    resetBtn.addEventListener('click', () => {
        resultSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        fileInput.value = '';
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        const file = files[0];
        if (!file.name.endsWith('.csv')) {
            showToast('Please upload a valid .csv file.', 'error');
            return;
        }
        uploadDataset(file);
    }

    async function uploadDataset(file) {
        uploadSection.classList.add('hidden');
        processingState.classList.remove('hidden');
        initBrain(); // Start the brain!

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', { method: 'POST', body: formData });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Upload failed');
            displayResults(data);
            showToast('Oracle prediction successful', 'success');
        } catch (error) {
            showToast('Error analyzing dataset: ' + error.message, 'error');
            processingState.classList.add('hidden');
            uploadSection.classList.remove('hidden');
        }
    }

    function displayResults(data) {
        processingState.classList.add('hidden');
        resultSection.classList.remove('hidden');

        document.getElementById('res-filename').textContent = data.filename;
        document.getElementById('res-algorithm').textContent = data.predicted_algorithm;
        
        const confPercent = (data.confidence_score * 100).toFixed(2);
        document.getElementById('res-confidence').textContent = confPercent + '%';
        
        setTimeout(() => { document.getElementById('confidence-bar').style.width = confPercent + '%'; }, 100);

        if (data.metrics) {
            document.getElementById('m-rows').textContent = data.metrics.n_rows ? Math.round(data.metrics.n_rows).toLocaleString() : '0';
            document.getElementById('m-cols').textContent = data.metrics.n_cols ? Math.round(data.metrics.n_cols).toLocaleString() : '0';
            document.getElementById('m-entropy').textContent = data.metrics.entropy ? data.metrics.entropy.toFixed(3) : '0.000';
            document.getElementById('m-imbalance').textContent = data.metrics.imbalance ? data.metrics.imbalance.toFixed(3) : '0.000';
            document.getElementById('m-skew').textContent = data.metrics.skew ? data.metrics.skew.toFixed(3) : '0.000';
            document.getElementById('m-nulls').textContent = (data.metrics.null_density !== undefined) ? (data.metrics.null_density * 100).toFixed(2) + '%' : '0.00%';
        }
    }




});
