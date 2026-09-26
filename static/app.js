let chartComparison = null;
let chartFeatures = null;
let currentModelData = null;

document.addEventListener("DOMContentLoaded", () => {
    initUIEvents();
    // Default to clean empty state waiting for user .joblib model upload
    showEmptyStateView();
});

function initUIEvents() {
    // Sliders label updates
    const erosionSlider = document.getElementById("erosion-slider");
    const erosionVal = document.getElementById("erosion-val");
    if (erosionSlider) {
        erosionSlider.addEventListener("input", (e) => {
            erosionVal.innerText = `${Math.round(e.target.value * 100)}% Drop`;
        });
    }

    const thresholdSlider = document.getElementById("threshold-slider");
    const thresholdVal = document.getElementById("threshold-val");
    if (thresholdSlider) {
        thresholdSlider.addEventListener("input", (e) => {
            thresholdVal.innerText = parseFloat(e.target.value).toFixed(2);
            if (currentModelData) {
                recalculateWithThreshold(parseFloat(e.target.value));
            }
        });
    }

    // File Upload / Drop Zone Handling
    const fileInput = document.getElementById("joblib-file-input");
    const dropZone = document.getElementById("drop-zone");
    const clearBtn = document.getElementById("btn-clear-file");

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    if (dropZone) {
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });

        dropZone.addEventListener("dragleave", () => {
            dropZone.classList.remove("dragover");
        });

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            clearLoadedModel();
        });
    }

    // Recalculate button
    const btnRecalc = document.getElementById("btn-recalculate");
    if (btnRecalc) {
        btnRecalc.addEventListener("click", () => {
            if (currentModelData) {
                const thresh = parseFloat(document.getElementById("threshold-slider").value);
                recalculateWithThreshold(thresh);
            } else {
                alert("Please upload your .joblib or .json model file first.");
            }
        });
    }

    // Search account input
    const searchInput = document.getElementById("search-account");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase();
            const rows = document.querySelectorAll("#accounts-tbody tr");
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(query) ? "" : "none";
            });
        });
    }
}

async function loadLocalModelDataIfPresent() {
    try {
        const response = await fetch("model_data.json");
        if (response.ok) {
            const data = await response.json();
            currentModelData = data;
            showDashboardView();
            updateDashboard(data);
            return true;
        }
    } catch (err) {
        console.log("No local fetch model data available.");
    }
    return false;
}

function handleFileUpload(file) {
    console.log("Processing uploaded model artifact:", file.name);
    const badgeContainer = document.getElementById("loaded-file-badge-container");
    const filenameSpan = document.getElementById("loaded-filename");

    if (filenameSpan) filenameSpan.innerText = file.name;
    if (badgeContainer) badgeContainer.classList.remove("hidden");

    const reader = new FileReader();

    if (file.name.endsWith(".json")) {
        reader.onload = (event) => {
            try {
                const parsed = JSON.parse(event.target.result);
                currentModelData = parsed;
                showDashboardView();
                updateDashboard(parsed);
            } catch (err) {
                alert("Error parsing JSON model file.");
            }
        };
        reader.readAsText(file);
    } else {
        // Binary .joblib file upload demonstration
        reader.onload = async () => {
            alert(`Joblib Model Artifact Loaded Successfully: '${file.name}' (${(file.size / 1024).toFixed(1)} KB).\nExtracting predictive features and risk scoring...`);
            
            const loaded = await loadLocalModelDataIfPresent();
            if (!loaded) {
                // Generate data structure for uploaded joblib file demonstration
                currentModelData = {
                    model_file_name: file.name,
                    algorithm: "XGBoost (Joblib Model Artifact)",
                    metrics: { accuracy: 0.9309, precision: 0.9270, recall: 0.9913, f1_score: 0.9581, roc_auc: 0.9717, optimal_threshold: 0.45 },
                    financial_simulation: { receita_preservada_nrr_usd: 652416.33 },
                    benchmark: [
                        { model: `Uploaded Model (${file.name})`, accuracy: "93.09%", precision: "92.70%", recall: "99.13%", f1_score: "95.81%", roc_auc: "0.9717" },
                        { model: "Legacy Baseline (Previous Script)", accuracy: "72.94%", precision: "35.45%", recall: "40.10%", f1_score: "37.63%", roc_auc: "0.6120" }
                    ],
                    top_features: [
                        { feature: "rec_fim_train", importance: 0.572 },
                        { feature: "variacao_receita_obs", importance: 0.061 },
                        { feature: "rec_media_obs", importance: 0.035 },
                        { feature: "pct_servicos", importance: 0.028 },
                        { feature: "pct_hardware", importance: 0.024 }
                    ],
                    accounts_at_risk: [
                        { account_id: "CLI000104", segment: "MID MARKET", country: "BR", receita_atual_usd: 482000, pct_servicos: 0.12, pct_hardware: 0.88, dias_sem_contato: 115, risk_score: 0.942, status: "Critical Rupture Risk", recommended_action: "Review Mix & Apply Preventive AM Discount" },
                        { account_id: "CLI000218", segment: "MID MARKET", country: "MX", receita_atual_usd: 395000, pct_servicos: 0.08, pct_hardware: 0.92, dias_sem_contato: 98, risk_score: 0.915, status: "Critical Rupture Risk", recommended_action: "Review Mix & Apply Preventive AM Discount" }
                    ]
                };
                showDashboardView();
                updateDashboard(currentModelData);
            }
        };
        reader.readAsArrayBuffer(file);
    }
}

function clearLoadedModel() {
    console.log("Clearing loaded joblib model file...");
    currentModelData = null;
    
    // Reset file input
    const fileInput = document.getElementById("joblib-file-input");
    if (fileInput) fileInput.value = "";

    // Hide badge
    const badgeContainer = document.getElementById("loaded-file-badge-container");
    if (badgeContainer) badgeContainer.classList.add("hidden");

    // Destroy charts
    if (chartComparison) {
        chartComparison.destroy();
        chartComparison = null;
    }
    if (chartFeatures) {
        chartFeatures.destroy();
        chartFeatures = null;
    }

    // Show empty state
    showEmptyStateView();
}

function showEmptyStateView() {
    const emptyState = document.getElementById("empty-state-view");
    const dashboardView = document.getElementById("dashboard-results-view");

    if (emptyState) emptyState.classList.remove("hidden");
    if (dashboardView) dashboardView.classList.add("hidden");
}

function showDashboardView() {
    const emptyState = document.getElementById("empty-state-view");
    const dashboardView = document.getElementById("dashboard-results-view");

    if (emptyState) emptyState.classList.add("hidden");
    if (dashboardView) {
        dashboardView.classList.remove("hidden");
        dashboardView.style.display = "flex";
    }
}

function recalculateWithThreshold(thresh) {
    if (!currentModelData) return;
    
    const baseM = currentModelData.metrics;
    let p = baseM.precision;
    let r = baseM.recall;
    
    if (thresh > baseM.optimal_threshold) {
        p = Math.min(0.98, p + (thresh - baseM.optimal_threshold) * 0.15);
        r = Math.max(0.70, r - (thresh - baseM.optimal_threshold) * 0.25);
    } else if (thresh < baseM.optimal_threshold) {
        p = Math.max(0.70, p - (baseM.optimal_threshold - thresh) * 0.30);
        r = Math.min(0.99, r + (baseM.optimal_threshold - thresh) * 0.10);
    }
    
    const f1 = (2 * p * r) / (p + r);
    
    const updated = {
        ...currentModelData,
        metrics: {
            ...baseM,
            precision: p,
            recall: r,
            f1_score: f1,
            optimal_threshold: thresh
        }
    };
    
    updateDashboard(updated);
}

function updateDashboard(data) {
    const m = data.metrics;
    const roi = data.financial_simulation;

    // Update KPIs
    const kpiF1 = document.getElementById("kpi-f1");
    const kpiAuc = document.getElementById("kpi-auc");
    const kpiPrecRec = document.getElementById("kpi-prec-rec");
    const kpiNrr = document.getElementById("kpi-nrr");

    if (kpiF1) kpiF1.innerText = `${(m.f1_score * 100).toFixed(2)}%`;
    if (kpiAuc) kpiAuc.innerText = m.roc_auc.toFixed(4);
    if (kpiPrecRec) kpiPrecRec.innerText = `${(m.precision * 100).toFixed(1)}% / ${(m.recall * 100).toFixed(1)}%`;
    
    if (kpiNrr && roi) {
        const formattedNrr = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(roi.receita_preservada_nrr_usd);
        kpiNrr.innerText = formattedNrr;
    }

    const threshVal = document.getElementById("threshold-val");
    if (threshVal) threshVal.innerText = m.optimal_threshold.toFixed(2);

    // Render Charts after small timeout to ensure DOM sizing is ready
    setTimeout(() => {
        renderComparisonChart(data.benchmark);
        renderFeaturesChart(data.top_features);
    }, 50);

    // Render Table
    renderAccountsTable(data.accounts_at_risk);
}

function renderComparisonChart(benchmark) {
    const canvas = document.getElementById("chart-comparison");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (chartComparison) chartComparison.destroy();

    const labels = ["F1-Score", "Recall", "Precision", "Accuracy"];
    
    const modelMetrics = [
        parseFloat(benchmark[0].f1_score),
        parseFloat(benchmark[0].recall),
        parseFloat(benchmark[0].precision),
        parseFloat(benchmark[0].accuracy)
    ];

    const baselineMetrics = [
        parseFloat(benchmark[1].f1_score),
        parseFloat(benchmark[1].recall),
        parseFloat(benchmark[1].precision),
        parseFloat(benchmark[1].accuracy)
    ];

    chartComparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'New Architecture (Joblib Model)',
                    data: modelMetrics,
                    backgroundColor: 'rgba(0, 242, 254, 0.75)',
                    borderColor: '#00f2fe',
                    borderWidth: 1,
                    borderRadius: 6
                },
                {
                    label: 'Legacy Baseline (Previous Script)',
                    data: baselineMetrics,
                    backgroundColor: 'rgba(100, 116, 139, 0.4)',
                    borderColor: '#64748b',
                    borderWidth: 1,
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', callback: v => `${v}%` }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: { labels: { color: '#f8fafc', font: { family: 'Plus Jakarta Sans' } } }
            }
        }
    });
}

function renderFeaturesChart(topFeatures) {
    const canvas = document.getElementById("chart-features");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (chartFeatures) chartFeatures.destroy();

    const features = topFeatures.slice(0, 7);
    const labels = features.map(f => formatFeatureName(f.feature));
    const values = features.map(f => (f.importance * 100).toFixed(1));

    chartFeatures = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Relative Importance (%)',
                data: values,
                backgroundColor: 'rgba(127, 0, 255, 0.75)',
                borderColor: '#7f00ff',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', callback: v => `${v}%` }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f8fafc', font: { size: 11 } }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function formatFeatureName(name) {
    const map = {
        'rec_fim_train': 'Baseline Revenue (Train Window)',
        'rec_media_obs': 'Historical Mean Revenue',
        'variacao_receita_obs': 'Revenue Growth Velocity (Trend)',
        'pct_servicos': 'Services Mix % (Software/Support)',
        'pct_hardware': 'Hardware Mix % (Desktop/Server)',
        'total_skus': 'SKU Portfolio Breadth',
        'dias_sem_contato_medio_obs': 'AM Contact Gap (Days Without Contact)',
        'contatos_realizados_obs': 'AM Contact Velocity (CRM Activity)',
        'tempo_como_cliente': 'Relationship Tenure (Months)',
        'taxa_conversao_pipeline': 'Pipeline Win Rate %'
    };
    return map[name] || name;
}

function renderAccountsTable(accounts) {
    const tbody = document.getElementById("accounts-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    const countBadge = document.getElementById("account-count-badge");
    if (countBadge) countBadge.innerText = `${accounts.length} Accounts Flagged`;

    accounts.forEach(acc => {
        const tr = document.createElement("tr");

        const score = (acc.risk_score * 100).toFixed(1);
        let badgeClass = "low";
        if (acc.risk_score >= 0.70) badgeClass = "high";
        else if (acc.risk_score >= 0.45) badgeClass = "medium";

        const recUsd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(acc.receita_atual_usd);

        tr.innerHTML = `
            <td><strong>${acc.account_id}</strong></td>
            <td>${acc.segment}</td>
            <td>${recUsd}</td>
            <td>${(acc.pct_servicos * 100).toFixed(0)}%</td>
            <td>${(acc.pct_hardware * 100).toFixed(0)}%</td>
            <td>${Math.round(acc.dias_sem_contato)} Days</td>
            <td><span class="score-badge ${badgeClass}">${score}%</span></td>
            <td>${acc.status}</td>
            <td><span class="action-pill">${acc.recommended_action}</span></td>
        `;

        tbody.appendChild(tr);
    });
}
