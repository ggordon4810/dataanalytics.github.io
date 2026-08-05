```javascript
document.addEventListener("DOMContentLoaded", function () {
    initializeMobileNavigation();
    initializeFileUpload();
    initializeManualEntryTable();
    initializeGraphTypeControls();
    initializeRangeDisplays();
    initializeFormLoading();
    initializeFlashMessages();
});


/* =================================
   Mobile Navigation
================================= */

function initializeMobileNavigation() {
    const menuButton = document.getElementById("menu-button");
    const navLinks = document.getElementById("nav-links");

    if (!menuButton || !navLinks) {
        return;
    }

    menuButton.addEventListener("click", function () {
        const isOpen = navLinks.classList.toggle("open");

        menuButton.setAttribute(
            "aria-expanded",
            String(isOpen)
        );
    });

    navLinks.addEventListener("click", function (event) {
        if (event.target.tagName === "A") {
            navLinks.classList.remove("open");
            menuButton.setAttribute("aria-expanded", "false");
        }
    });
}


/* =================================
   CSV Upload
================================= */

function initializeFileUpload() {
    const uploadZone = document.getElementById("upload-zone");
    const fileInput = document.getElementById("csv-file");
    const selectedFile = document.getElementById("selected-file");

    if (!uploadZone || !fileInput) {
        return;
    }

    uploadZone.addEventListener("click", function () {
        fileInput.click();
    });

    uploadZone.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", function () {
        displaySelectedFile(fileInput.files, selectedFile);
    });

    uploadZone.addEventListener("dragover", function (event) {
        event.preventDefault();
        uploadZone.classList.add("dragover");
    });

    uploadZone.addEventListener("dragleave", function () {
        uploadZone.classList.remove("dragover");
    });

    uploadZone.addEventListener("drop", function (event) {
        event.preventDefault();
        uploadZone.classList.remove("dragover");

        const droppedFiles = event.dataTransfer.files;

        if (!droppedFiles || droppedFiles.length === 0) {
            return;
        }

        const file = droppedFiles[0];

        if (!file.name.toLowerCase().endsWith(".csv")) {
            showClientError(
                "Only CSV files are supported."
            );
            return;
        }

        const transfer = new DataTransfer();
        transfer.items.add(file);
        fileInput.files = transfer.files;

        displaySelectedFile(fileInput.files, selectedFile);
    });
}


function displaySelectedFile(files, selectedFileElement) {
    if (!selectedFileElement) {
        return;
    }

    if (!files || files.length === 0) {
        selectedFileElement.textContent = "";
        return;
    }

    const file = files[0];

    selectedFileElement.textContent =
        `Selected file: ${file.name}`;
}


/* =================================
   Manual Data Entry
================================= */

function initializeManualEntryTable() {
    const tableBody = document.getElementById("data-rows");
    const addRowButton = document.getElementById("add-data-row");

    if (!tableBody || !addRowButton) {
        return;
    }

    addRowButton.addEventListener("click", function () {
        addDataRow(tableBody);
    });

    tableBody.addEventListener("click", function (event) {
        const removeButton = event.target.closest(
            ".remove-data-row"
        );

        if (!removeButton) {
            return;
        }

        const rows = tableBody.querySelectorAll("tr");

        if (rows.length <= 2) {
            showClientError(
                "At least two data rows are required."
            );
            return;
        }

        removeButton.closest("tr").remove();
        updateRowNumbers(tableBody);
    });
}


function addDataRow(tableBody) {
    const rowCount = tableBody.querySelectorAll("tr").length;
    const rowNumber = rowCount + 1;

    const row = document.createElement("tr");

    row.innerHTML = `
        <td class="row-number">${rowNumber}</td>

        <td>
            <label class="visually-hidden" for="x-value-${rowNumber}">
                X value ${rowNumber}
            </label>
            <input
                type="text"
                id="x-value-${rowNumber}"
                name="x_value"
                placeholder="X value"
                required
            >
        </td>

        <td>
            <label class="visually-hidden" for="y-value-${rowNumber}">
                Y value ${rowNumber}
            </label>
            <input
                type="number"
                id="y-value-${rowNumber}"
                name="y_value"
                step="any"
                placeholder="Y value"
                required
            >
        </td>

        <td class="error-column-cell">
            <label class="visually-hidden" for="error-value-${rowNumber}">
                Error value ${rowNumber}
            </label>
            <input
                type="number"
                id="error-value-${rowNumber}"
                name="error_value"
                step="any"
                min="0"
                placeholder="Optional"
            >
        </td>

        <td>
            <button
                type="button"
                class="danger-button small-button remove-data-row"
            >
                Remove
            </button>
        </td>
    `;

    tableBody.appendChild(row);
}


function updateRowNumbers(tableBody) {
    const rows = tableBody.querySelectorAll("tr");

    rows.forEach(function (row, index) {
        const rowNumber = index + 1;
        const numberCell = row.querySelector(".row-number");

        if (numberCell) {
            numberCell.textContent = rowNumber;
        }
    });
}


/* =================================
   Graph Type Controls
================================= */

function initializeGraphTypeControls() {
    const graphTypeSelect = document.getElementById("graph-type");
    const errorColumnSelect =
        document.getElementById("error-column");
    const lineSettings =
        document.getElementById("line-settings");
    const markerSettings =
        document.getElementById("marker-settings");

    if (!graphTypeSelect) {
        return;
    }

    function updateGraphSettings() {
        const graphType = graphTypeSelect.value;

        if (lineSettings) {
            lineSettings.hidden = graphType === "bar";
        }

        if (markerSettings) {
            markerSettings.hidden = graphType === "bar";
        }

        if (errorColumnSelect) {
            errorColumnSelect.disabled = false;
        }
    }

    graphTypeSelect.addEventListener(
        "change",
        updateGraphSettings
    );

    updateGraphSettings();
}


/* =================================
   Range Input Labels
================================= */

function initializeRangeDisplays() {
    const rangeInputs =
        document.querySelectorAll("input[type='range']");

    rangeInputs.forEach(function (input) {
        const outputId = input.dataset.output;
        const output = outputId
            ? document.getElementById(outputId)
            : null;

        if (!output) {
            return;
        }

        function updateOutput() {
            output.textContent = input.value;
        }

        input.addEventListener("input", updateOutput);
        updateOutput();
    });
}


/* =================================
   Loading Overlay
================================= */

function initializeFormLoading() {
    const loadingOverlay =
        document.getElementById("loading-overlay");

    const forms = document.querySelectorAll(
        "form[data-show-loading='true']"
    );

    if (!loadingOverlay || forms.length === 0) {
        return;
    }

    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitButton = form.querySelector(
                "button[type='submit']"
            );

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.dataset.originalText =
                    submitButton.textContent;
                submitButton.textContent = "Processing...";
            }

            loadingOverlay.classList.add("active");
        });
    });
}


/* =================================
   Flash Messages
================================= */

function initializeFlashMessages() {
    const messages =
        document.querySelectorAll(".flash-message");

    messages.forEach(function (message) {
        window.setTimeout(function () {
            message.classList.add("hide");

            window.setTimeout(function () {
                message.remove();
            }, 400);
        }, 5000);
    });
}


/* =================================
   Client-Side Error Messages
================================= */

function showClientError(message) {
    let alertContainer =
        document.getElementById("client-alert-container");

    if (!alertContainer) {
        alertContainer = document.createElement("div");
        alertContainer.id = "client-alert-container";

        const pageContainer =
            document.querySelector(".page-container");

        if (pageContainer) {
            pageContainer.prepend(alertContainer);
        } else {
            document.body.prepend(alertContainer);
        }
    }

    const alert = document.createElement("div");

    alert.className =
        "alert alert-error flash-message";

    alert.setAttribute("role", "alert");
    alert.textContent = message;

    alertContainer.appendChild(alert);

    window.setTimeout(function () {
        alert.classList.add("hide");

        window.setTimeout(function () {
            alert.remove();
        }, 400);
    }, 5000);
}
```

