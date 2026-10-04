// static/js/dynamic_fields.js - Interactive form helpers
document.addEventListener("DOMContentLoaded", () => {
    // Current job checkbox toggles End Date field
    const isCurrentCheckbox = document.getElementById("is_current");
    const endDateField = document.getElementById("end_date");

    if (isCurrentCheckbox && endDateField) {
        const toggleEndDate = () => {
            if (isCurrentCheckbox.checked) {
                endDateField.value = "Present";
                endDateField.disabled = true;
                endDateField.classList.add("bg-gray-100", "cursor-not-allowed");
            } else {
                if (endDateField.value === "Present") {
                    endDateField.value = "";
                }
                endDateField.disabled = false;
                endDateField.classList.remove("bg-gray-100", "cursor-not-allowed");
            }
        };

        isCurrentCheckbox.addEventListener("change", toggleEndDate);
        toggleEndDate(); // Initial run
    }

    // Confirmation on destructive deletions
    const deleteForms = document.querySelectorAll("form.delete-form");
    deleteForms.forEach(form => {
        form.addEventListener("submit", (e) => {
            const confirmMsg = form.dataset.confirm || "Are you sure you want to delete this record?";
            if (!confirm(confirmMsg)) {
                e.preventDefault();
            }
        });
    });
});
