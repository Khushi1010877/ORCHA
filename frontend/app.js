const API = "http://127.0.0.1:8000";
let currentProduct = null;

function showTab(name) {
    document.querySelectorAll(".tab").forEach(function(tab) {
        tab.classList.remove("active");
    });
    document.querySelectorAll(".nav-btn").forEach(function(btn) {
        btn.classList.remove("active");
    });
    document.getElementById("tab-" + name).classList.add("active");
    document.querySelectorAll(".nav-btn").forEach(function(btn) {
        if (btn.getAttribute("data-tab") === name) {
            btn.classList.add("active");
        }
    });
    if (name === "memory") {
        loadMemory();
    }
}

async function runAnalyze() {
    var product = document.getElementById("product-input").value.trim();

    hide("result-card");
    hide("error-box");

    if (!product) {
        showError("error-box", "Please enter a product name.");
        return;
    }

    currentProduct = product;

    show("pipeline");
    setStep(1, "", "Waiting...");
    setStep(2, "", "Waiting...");
    setStep(3, "", "Waiting...");
    setStep(4, "", "Waiting...");

    var btn = document.getElementById("analyze-btn");
    btn.disabled = true;
    btn.textContent = "Analyzing...";

    setStep(1, "active", "Running...");

    try {
        var response = await fetch(API + "/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product: product }),
            signal: AbortSignal.timeout(120000)
        });

        var data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong.");
        }

        setStep(1, "done", "Done ✓");
        setStep(2, "done", "Done ✓");
        setStep(3, "done", "Done ✓");
        setStep(4, "done", "Done ✓");

        showResult(data);

    } catch (err) {
        setStep(1, "", "Failed ✗");
        showError("error-box", err.message);
    }

    btn.disabled = false;
    btn.textContent = "Analyze";
}

function showResult(json) {
    var data = json.data;

    var badge = document.getElementById("result-badge");
    badge.textContent = json.source === "cache" ? "CACHED" : "LIVE";
    badge.className = json.source === "cache" ? "amber" : "purple";

    document.getElementById("result-product").textContent = data.product || currentProduct;
    document.getElementById("result-verdict").textContent = '"' + (data.verdict || "") + '"';

    var sentiment = data.overall_sentiment || "mixed";
    var sentimentEl = document.getElementById("result-sentiment");
    sentimentEl.textContent = capitalize(sentiment);
    sentimentEl.className = "stat-value " + sentiment;

    document.getElementById("result-severity").textContent = (data.severity_score || 0) + "/10";

    var kp = document.getElementById("key-points");
    kp.innerHTML = (data.key_points || []).map(function(p) {
        return "<li>" + p + "</li>";
    }).join("");

    var ai = document.getElementById("action-items");
    ai.innerHTML = (data.action_items || []).map(function(a) {
        return "<li>" + a + "</li>";
    }).join("");

    document.getElementById("final-summary").textContent = data.final_summary || "";

    show("result-card");
}

async function loadMemory() {
    var list = document.getElementById("memory-list");
    list.innerHTML = "<p>Loading...</p>";

    try {
        var response = await fetch(API + "/memory");
        var data = await response.json();
        var entries = data.entries || [];

        if (entries.length === 0) {
            list.innerHTML = "<p style='color:#64748b'>No analyses saved yet.</p>";
            return;
        }

        list.innerHTML = entries.map(function(e) {
            return '<div class="memory-item">' +
                '<div>' +
                '<div class="memory-product">' + e.product + '</div>' +
                '<div class="memory-time">' + new Date(e.analyzed_at).toLocaleString() + '</div>' +
                '</div>' +
                '<div style="display:flex;gap:8px">' +
                '<button class="secondary" onclick="viewMemory(\'' + e.product + '\')">View</button>' +
                '<button class="secondary" style="color:#ef4444" onclick="deleteMemory(\'' + e.product + '\')">Delete</button>' +
                '</div>' +
                '</div>';
        }).join("");

    } catch (err) {
        list.innerHTML = "<p style='color:#ef4444'>Failed to load memory.</p>";
    }
}

async function viewMemory(product) {
    var response = await fetch(API + "/memory/" + encodeURIComponent(product));
    var json = await response.json();
    currentProduct = product;
    document.getElementById("product-input").value = product;
    showTab("analyze");
    hide("pipeline");
    showResult({ source: "cache", data: json.data });
}

async function deleteMemory(product) {
    if (!confirm('Delete analysis for "' + product + '"?')) return;
    await fetch(API + "/memory/" + encodeURIComponent(product), { method: "DELETE" });
    loadMemory();
}

async function runCompare() {
    var a = document.getElementById("compare-a").value.trim();
    var b = document.getElementById("compare-b").value.trim();

    hide("compare-result");
    hide("compare-error");

    if (!a || !b) {
        showError("compare-error", "Please enter both product names.");
        return;
    }

    try {
        var response = await fetch(API + "/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_a: a, product_b: b })
        });

        var json = await response.json();

        if (!response.ok) {
            throw new Error(json.detail || "Compare failed.");
        }

        showCompare(json.data);

    } catch (err) {
        showError("compare-error", err.message);
    }
}

function showCompare(data) {
    var result = document.getElementById("compare-result");
    result.innerHTML =
        '<div class="compare-grid">' +
        '<div class="compare-card"><h3>' + data.product_a.name + '</h3>' + compareRows(data.product_a) + '</div>' +
        '<div class="compare-card"><h3>' + data.product_b.name + '</h3>' + compareRows(data.product_b) + '</div>' +
        '</div>';
    show("compare-result");
}

function compareRows(d) {
    var sentiment = d.sentiment || "mixed";
    return '<div class="compare-row"><span class="compare-key">Sentiment</span><span class="' + sentiment + '">' + capitalize(sentiment) + '</span></div>' +
        '<div class="compare-row"><span class="compare-key">Severity</span><span>' + d.severity_score + '/10</span></div>' +
        '<div class="compare-row"><span class="compare-key">Verdict</span><span style="font-size:12px">' + (d.verdict || "—") + '</span></div>';
}

function downloadHTML() {
    if (!currentProduct) return;
    window.open(API + "/report/html/" + encodeURIComponent(currentProduct), "_blank");
}

function downloadPDF() {
    if (!currentProduct) return;
    window.open(API + "/report/pdf/" + encodeURIComponent(currentProduct), "_blank");
}

function show(id) { document.getElementById(id).classList.remove("hidden"); }
function hide(id) { document.getElementById(id).classList.add("hidden"); }
function showError(id, message) {
    var el = document.getElementById(id);
    el.textContent = message;
    el.classList.remove("hidden");
}
function setStep(number, state, text) {
    var step = document.getElementById("step-" + number);
    var label = document.getElementById("status-" + number);
    step.className = "step " + state;
    label.textContent = text;
}
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}