document.addEventListener("DOMContentLoaded", function () {
    var fileInput = document.getElementById("document");
    var uploadForm = document.querySelector(".upload-form");
    var dropzone = document.getElementById("upload-dropzone");
    var browseTrigger = document.getElementById("browse-trigger");
    var selectedFileText = document.getElementById("selected-file-text");
    var fileStateIcon = document.querySelector(".file-state-icon");
    var uploadError = document.getElementById("upload-error");
    var suppressClickUntil = 0;

    if (!fileInput || !dropzone || !uploadForm) {
        return;
    }

    function renderFileState() {
        if (fileInput.files.length > 0) {
            var label = "Selected: " + fileInput.files[0].name;
            fileInput.title = label;
            if (selectedFileText) {
                selectedFileText.textContent = label;
            }
            if (fileStateIcon) {
                fileStateIcon.textContent = "\u2713";
            }
            dropzone.classList.add("has-file");
            dropzone.classList.remove("has-error");
            if (uploadError) {
                uploadError.textContent = "";
            }
        } else {
            if (selectedFileText) {
                selectedFileText.textContent = "No file selected";
            }
            if (fileStateIcon) {
                fileStateIcon.textContent = "\u25CB";
            }
            dropzone.classList.remove("has-file");
        }
    }

    if (browseTrigger) {
        browseTrigger.addEventListener("click", function (event) {
            event.stopPropagation();
            fileInput.click();
        });
    }

    dropzone.addEventListener("click", function () {
        if (Date.now() < suppressClickUntil) {
            return;
        }
        fileInput.click();
    });

    dropzone.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            fileInput.click();
        }
    });

    dropzone.addEventListener("dragover", function (event) {
        event.preventDefault();
        dropzone.classList.add("is-dragover");
    });

    dropzone.addEventListener("dragleave", function () {
        dropzone.classList.remove("is-dragover");
    });

    dropzone.addEventListener("drop", function (event) {
        event.preventDefault();
        event.stopPropagation();
        dropzone.classList.remove("is-dragover");
        // Prevent the synthetic click that can fire right after a drop
        // (this click was opening the native "Open/Cancel" file picker).
        suppressClickUntil = Date.now() + 500;
        if (event.dataTransfer && event.dataTransfer.files.length > 0) {
            fileInput.files = event.dataTransfer.files;
            renderFileState();
        }
    });

    fileInput.addEventListener("change", renderFileState);

    uploadForm.addEventListener("submit", function (event) {
        if (fileInput.files.length === 0) {
            event.preventDefault();
            dropzone.classList.add("has-error");
            if (uploadError) {
                uploadError.textContent = "Please select a document before validation.";
            }
        }
    });
});
