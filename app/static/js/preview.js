// static/js/preview.js - Real-time iframe preview handler
document.addEventListener("DOMContentLoaded", () => {
    const previewFrame = document.getElementById("resume-preview-frame");
    const styleSelector = document.getElementById("style-selector");
    const refreshBtn = document.getElementById("refresh-preview-btn");
    const printBtn = document.getElementById("print-preview-btn");

    if (!previewFrame) return;

    // Handle style changes
    if (styleSelector) {
        styleSelector.addEventListener("change", async (e) => {
            const newStyle = e.target.value;
            const resumeId = styleSelector.dataset.resumeId;

            // Update iframe src
            const previewUrl = `/export/preview/${resumeId}/${newStyle}`;
            previewFrame.src = previewUrl;

            // Update on the backend
            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
                await fetch(`/resume/${resumeId}/update-style`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify({ style: newStyle })
                });

                // Also update the PDF download link href
                const downloadLink = document.getElementById("download-pdf-btn");
                if (downloadLink) {
                    downloadLink.href = `/export/download/${resumeId}/${newStyle}`;
                }
            } catch (err) {
                console.error("Failed to update style preference:", err);
            }
        });
    }

    // Refresh preview iframe
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            previewFrame.contentWindow.location.reload();
        });
    }

    // Direct browser print preview
    if (printBtn) {
        printBtn.addEventListener("click", () => {
            if (previewFrame.contentWindow) {
                previewFrame.contentWindow.focus();
                previewFrame.contentWindow.print();
            }
        });
    }
});
