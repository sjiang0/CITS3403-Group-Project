// delete confirmation
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".delete-form").forEach(form => {
        form.addEventListener("submit", function (e) {
            const confirmed = confirm("Delete this quest?");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});