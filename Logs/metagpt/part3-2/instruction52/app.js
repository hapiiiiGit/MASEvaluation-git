/**
 * app.js
 * Implements frontend logic for document upload, summary display, and formula builder.
 * Integrates with backend APIs for document, summary, and formula management.
 */

// =================== CONFIG ===================
const API_BASE = '/api/';

// =================== UTILS ===================
function showStatus(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.style.color = isError ? 'red' : 'green';
    setTimeout(() => { el.textContent = ''; }, 4000);
}

function clearChildren(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

// =================== DOCUMENT UPLOAD ===================
document.getElementById('upload-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const input = document.getElementById('file-input');
    const files = input.files;
    if (!files.length) {
        showStatus('upload-status', 'Please select at least one file.', true);
        return;
    }

    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }

    try {
        const resp = await fetch(API_BASE + 'documents/', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        if (!resp.ok) {
            const data = await resp.json();
            showStatus('upload-status', data.detail || 'Upload failed.', true);
            return;
        }
        showStatus('upload-status', 'Upload successful!');
        await loadDocuments();
    } catch (err) {
        showStatus('upload-status', 'Error uploading files.', true);
    }
});

// =================== DOCUMENTS & SUMMARIES ===================
async function loadDocuments() {
    try {
        const resp = await fetch(API_BASE + 'documents/', { credentials: 'include' });
        if (!resp.ok) throw new Error('Failed to fetch documents');
        const docs = await resp.json();
        renderDocuments(docs);
    } catch (err) {
        showStatus('upload-status', 'Error loading documents.', true);
    }
}

async function fetchSummary(documentId) {
    try {
        const resp = await fetch(`${API_BASE}documents/${documentId}/summary/`, { credentials: 'include' });
        if (!resp.ok) throw new Error('Failed to fetch summary');
        return await resp.json();
    } catch (err) {
        return { summary_text: 'Error fetching summary.' };
    }
}

async function renderDocuments(docs) {
    const container = document.getElementById('documents-list');
    clearChildren(container);

    if (!docs.length) {
        container.textContent = 'No documents uploaded yet.';
        return;
    }

    for (let doc of docs) {
        const docDiv = document.createElement('div');
        docDiv.className = 'document-item';

        const title = document.createElement('h4');
        title.textContent = `${doc.filename} (${doc.file_type})`;
        docDiv.appendChild(title);

        // Summary
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'summary-item';
        summaryDiv.textContent = 'Loading summary...';
        docDiv.appendChild(summaryDiv);

        // Fetch and display summary
        fetchSummary(doc.document_id).then(summary => {
            summaryDiv.textContent = summary.summary_text || 'No summary available.';
        });

        container.appendChild(docDiv);
    }
}

// =================== FORMULA BUILDER ===================
document.getElementById('formula-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const name = document.getElementById('formula-name').value.trim();
    const expression = document.getElementById('formula-expression').value.trim();
    if (!name || !expression) {
        showStatus('formula-status', 'Please provide both name and expression.', true);
        return;
    }

    try {
        const resp = await fetch(API_BASE + 'formulas/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name, expression })
        });
        if (!resp.ok) {
            const data = await resp.json();
            showStatus('formula-status', data.detail || 'Failed to save formula.', true);
            return;
        }
        showStatus('formula-status', 'Formula saved!');
        document.getElementById('formula-form').reset();
        await loadFormulas();
    } catch (err) {
        showStatus('formula-status', 'Error saving formula.', true);
    }
});

async function loadFormulas() {
    try {
        const resp = await fetch(API_BASE + 'formulas/saved/', { credentials: 'include' });
        if (!resp.ok) throw new Error('Failed to fetch formulas');
        const formulas = await resp.json();
        renderFormulas(formulas);
        renderFormulaSelect(formulas);
    } catch (err) {
        showStatus('formula-status', 'Error loading formulas.', true);
    }
}

function renderFormulas(formulas) {
    const container = document.getElementById('saved-formulas-list');
    clearChildren(container);

    if (!formulas.length) {
        container.textContent = 'No formulas saved yet.';
        return;
    }

    formulas.forEach(formula => {
        const div = document.createElement('div');
        div.className = 'formula-item';
        div.innerHTML = `<strong>${formula.name}</strong>: ${formula.expression}`;
        container.appendChild(div);
    });
}

function renderFormulaSelect(formulas) {
    const select = document.getElementById('select-formula');
    clearChildren(select);

    formulas.forEach(formula => {
        const option = document.createElement('option');
        option.value = formula.formula_id;
        option.textContent = formula.name;
        select.appendChild(option);
    });

    // Trigger variable input generation
    select.dispatchEvent(new Event('change'));
}

// =================== FORMULA EVALUATION ===================
document.getElementById('select-formula').addEventListener('change', async function (e) {
    const formulaId = e.target.value;
    if (!formulaId) return;

    // Fetch formula details to parse variables
    try {
        const resp = await fetch(`${API_BASE}formulas/${formulaId}/`, { credentials: 'include' });
        if (!resp.ok) throw new Error('Failed to fetch formula');
        const formula = await resp.json();
        renderVariableInputs(formula.expression);
    } catch (err) {
        renderVariableInputs('');
    }
});

function renderVariableInputs(expression) {
    const container = document.getElementById('formula-variables');
    clearChildren(container);

    if (!expression) return;

    // Extract variable names from expression (simple regex for [A-Za-z_][A-Za-z0-9_]*)
    const varSet = new Set();
    const regex = /\b([A-Za-z_][A-Za-z0-9_]*)\b/g;
    let match;
    while ((match = regex.exec(expression)) !== null) {
        // Exclude known functions and numbers
        if (!['sin','cos','tan','log','exp','sqrt','pi','e'].includes(match[1]) && isNaN(match[1])) {
            varSet.add(match[1]);
        }
    }

    varSet.forEach(variable => {
        const label = document.createElement('label');
        label.htmlFor = `var-${variable}`;
        label.textContent = `${variable}:`;
        const input = document.createElement('input');
        input.type = 'number';
        input.id = `var-${variable}`;
        input.name = variable;
        input.required = true;
        container.appendChild(label);
        container.appendChild(input);
    });
}

document.getElementById('evaluate-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const formulaId = document.getElementById('select-formula').value;
    if (!formulaId) {
        showStatus('evaluation-result', 'Please select a formula.', true);
        return;
    }

    // Gather variable values
    const variableInputs = document.querySelectorAll('#formula-variables input');
    const inputData = {};
    for (let input of variableInputs) {
        if (input.value === '') {
            showStatus('evaluation-result', `Please provide value for ${input.name}.`, true);
            return;
        }
        inputData[input.name] = parseFloat(input.value);
    }

    try {
        const resp = await fetch(`${API_BASE}formulas/${formulaId}/evaluate/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ input_data: inputData })
        });
        const data = await resp.json();
        if (!resp.ok) {
            showStatus('evaluation-result', data.detail || 'Evaluation failed.', true);
            return;
        }
        showStatus('evaluation-result', `Result: ${data.result}`);
    } catch (err) {
        showStatus('evaluation-result', 'Error evaluating formula.', true);
    }
});

// =================== INITIAL LOAD ===================
window.addEventListener('DOMContentLoaded', async function () {
    await loadDocuments();
    await loadFormulas();
});