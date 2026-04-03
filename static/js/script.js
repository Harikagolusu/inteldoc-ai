document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const selectedFile = document.getElementById('selected-file');
    const fileName = document.getElementById('file-name');
    const removeBtn = document.getElementById('remove-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const uploadForm = document.getElementById('upload-form');
    const uploadSection = document.getElementById('upload-section');
    const feedback = document.getElementById('feedback');
    const loader = document.getElementById('loader');
    const loaderStatus = document.getElementById('loader-status');
    const progressFill = document.getElementById('progress-fill');
    const resultsSection = document.getElementById('results-section');
    const resetBtn = document.getElementById('reset-btn');

    let currentFile = null;

    // --- Drag and Drop Logic --- //

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });

    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            handleFiles(files[0]);
        }
    }

    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            handleFiles(this.files[0]);
        }
    });

    function handleFiles(file) {
        // Validate file type
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'image/png', 'image/jpeg', 'image/jpg'];
        
        let isValidExt = file.name.match(/\.(pdf|docx?|png|jpe?g)$/i);

        if (!validTypes.includes(file.type) && !isValidExt) {
            showError("Unsupported file type. Please upload PDF, DOCX, PNG, or JPG.");
            resetFile();
            return;
        }

        currentFile = file;
        fileName.textContent = file.name;
        dropArea.style.display = 'none';
        selectedFile.style.display = 'flex';
        analyzeBtn.disabled = false;
        feedback.textContent = '';
    }

    removeBtn.addEventListener('click', resetFile);

    function resetFile() {
        currentFile = null;
        fileInput.value = '';
        dropArea.style.display = 'block';
        selectedFile.style.display = 'none';
        analyzeBtn.disabled = true;
    }

    function showError(msg) {
        feedback.textContent = msg;
    }

    resetBtn.addEventListener('click', () => {
        resetFile();
        resultsSection.style.display = 'none';
        uploadSection.style.display = 'block';
        feedback.textContent = '';
    });

    // --- Loading Steps Simulator --- //
    let loadingInterval;
    function startLoadingSimulation() {
        progressFill.style.width = '0%';
        progressFill.style.transition = 'width 0.5s ease';
        
        const steps = [
            { text: "Extracting Text Contents...", progress: "20%" },
            { text: "Executing NLP Models (spaCy)...", progress: "45%" },
            { text: "Analyzing Context & Entities...", progress: "65%" },
            { text: "Generating Advanced AI Summary...", progress: "85%" }
        ];
        
        let currentStep = 0;
        loaderStatus.textContent = steps[currentStep].text;
        setTimeout(() => { progressFill.style.width = steps[currentStep].progress; }, 100);
        
        loadingInterval = setInterval(() => {
            currentStep++;
            if(currentStep < steps.length) {
                loaderStatus.textContent = steps[currentStep].text;
                progressFill.style.width = steps[currentStep].progress;
            } else {
                clearInterval(loadingInterval);
            }
        }, 1500); // Progress every 1.5 seconds roughly
    }

    // --- Form Submission --- //

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!currentFile) return;

        // UI State: Loading
        uploadSection.style.display = 'none';
        loader.style.display = 'block';
        feedback.textContent = '';
        resultsSection.style.display = 'none';
        
        startLoadingSimulation();

        try {
            // Updated to use true File Upload for FormData standard
            const formData = new FormData();
            formData.append('file', currentFile);
            
            const apiEndpoint = (window.location.protocol === 'file:' || window.location.port !== '8000') 
                ? 'http://127.0.0.1:8000/analyze' 
                : '/analyze';

            const response = await fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Authorization': 'Bearer sk_track2_987654321'
                    // Notice: no Content-Type header with FormData, fetch handles boundaries automatically
                },
                body: formData
            });

            let data;
            try {
                data = await response.json();
            } catch (err) {
                throw new Error("Invalid server response format. Check API Key or endpoint.");
            }

            if (!response.ok) {
                throw new Error(data.detail || "Failed to analyze document.");
            }

            // Complete progress bar forcefully
            clearInterval(loadingInterval);
            progressFill.style.width = '100%';
            loaderStatus.textContent = "Finalizing dashboard...";
            
            setTimeout(() => displayResults(data), 500); // brief pause to see 100%

        } catch (error) {
            handleError(error);
        }
    });

    function handleError(error) {
        clearInterval(loadingInterval);
        console.error("Analysis error:", error);
        // UI State: Error
        loader.style.display = 'none';
        uploadSection.style.display = 'block';
        showError(error.message || "An unexpected error occurred during processing.");
        resetFile(); 
    }

    function displayResults(data) {
        loader.style.display = 'none';
        resultsSection.style.display = 'block';

        // 1. Category
        document.getElementById('category-text').textContent = data.category || "General Document";

        // 2. Summary
        document.getElementById('summary-text').textContent = data.summary;

        // 3. Sentiment
        const sentimentBadge = document.getElementById('sentiment-badge');
        const sentimentIcon = document.getElementById('sentiment-icon');
        const sentimentText = document.getElementById('sentiment-text');
        
        // Reset classes
        sentimentBadge.className = 'sentiment-container';
        
        let sentiment = data.sentiment ? data.sentiment.toLowerCase() : 'neutral';
        if (sentiment.includes('positive')) {
            sentimentBadge.classList.add('sentiment-positive');
            sentimentIcon.innerHTML = '<i class="fa-solid fa-face-smile"></i>';
            sentimentText.textContent = 'Positive';
        } else if (sentiment.includes('negative')) {
            sentimentBadge.classList.add('sentiment-negative');
            sentimentIcon.innerHTML = '<i class="fa-solid fa-face-frown"></i>';
            sentimentText.textContent = 'Negative';
        } else {
            sentimentBadge.classList.add('sentiment-neutral');
            sentimentIcon.innerHTML = '<i class="fa-solid fa-face-meh"></i>';
            sentimentText.textContent = 'Neutral';
        }

        // 4. Keywords
        const keywordsList = document.getElementById('keywords-list');
        keywordsList.innerHTML = '';
        if (data.keywords && data.keywords.length > 0) {
            data.keywords.forEach(kw => {
                const span = document.createElement('span');
                span.className = 'keyword-chip';
                span.textContent = kw;
                keywordsList.appendChild(span);
            });
        } else {
            keywordsList.innerHTML = '<span class="no-entities">No keywords extracted</span>';
        }

        // 5. Entities
        const entitiesGrid = document.getElementById('entities-grid');
        entitiesGrid.innerHTML = ''; // Clear previous

        const entityMapping = [
            { key: 'persons', label: 'Names Detected', tagClass: 'tag-persons' },
            { key: 'organizations', label: 'Organizations & Companies', tagClass: 'tag-organizations' },
            { key: 'dates', label: 'Dates & Times', tagClass: 'tag-dates' },
            { key: 'money', label: 'Financial Amounts', tagClass: 'tag-money' },
            { key: 'locations', label: 'Locations', tagClass: 'tag-locations' }
        ];

        let hasAnyEntity = false;

        entityMapping.forEach(mapping => {
            const items = data.entities[mapping.key];
            if (items && items.length > 0) {
                hasAnyEntity = true;
                
                const groupDiv = document.createElement('div');
                groupDiv.className = 'entity-group';
                
                const titleDiv = document.createElement('div');
                titleDiv.className = 'entity-title';
                titleDiv.textContent = mapping.label;
                
                const tagsDiv = document.createElement('div');
                tagsDiv.className = 'entity-tags';
                
                items.forEach(item => {
                    const tagSpan = document.createElement('span');
                    tagSpan.className = `entity-tag ${mapping.tagClass}`;
                    tagSpan.textContent = item;
                    tagsDiv.appendChild(tagSpan);
                });
                
                groupDiv.appendChild(titleDiv);
                groupDiv.appendChild(tagsDiv);
                entitiesGrid.appendChild(groupDiv);
            }
        });

        if (!hasAnyEntity) {
            entitiesGrid.innerHTML = '<p class="no-entities">No standard entities were identified by the model.</p>';
        }
        
        // Re-trigger animation cleanly when showing result
        const animatedCards = document.querySelectorAll('.fade-in-up');
        animatedCards.forEach(card => {
            card.style.animation = 'none';
            card.offsetHeight; /* trigger reflow to restart */
            card.style.animation = null; 
        });
    }
});
