document.addEventListener("DOMContentLoaded", () => {
    // helper functions
    function updateStats() {
        const total = document.querySelectorAll(".quest-item").length;

        const active = document.querySelectorAll('#active-section .quest-item').length;
        const completed = document.querySelectorAll('#completed-section .quest-item').length;
        const overdue = document.querySelectorAll('#overdue-section .quest-item').length;

        const totalEl = document.getElementById("total-count");
        const activeEl = document.getElementById("active-count");
        const completedEl = document.getElementById("completed-count");
        const overdueEl = document.getElementById("overdue-count");

        if (totalEl) totalEl.textContent = total;
        if (activeEl) activeEl.textContent = active;
        if (completedEl) completedEl.textContent = completed;
        if (overdueEl) overdueEl.textContent = overdue;
    }

    function updateOverdueIcon(questItem) {
        const title = questItem.querySelector(".quest-title");
        if (!title) return;

        const dueDate = questItem.dataset.dueDate;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const questDueDate = new Date(dueDate);
        questDueDate.setHours(0, 0, 0, 0);

        const isOverdue =
            dueDate &&
            questDueDate < today &&
            questItem.dataset.status !== "completed";

        // remove old icons
        title.textContent = title.textContent.replace(/^✅\s|^❌\s/, "");

        if (questItem.dataset.status === "completed") {
            title.textContent = "✅ " + title.textContent;
        } else if (isOverdue) {
            title.textContent = "❌ " + title.textContent;
        }
    }

    function removeEmptyMessages() {
        const sections = [
            "#active-section",
            "#completed-section",
            "#overdue-section"
        ];

        sections.forEach(section => {
            const ul = document.querySelector(`${section} ul`);
            if (!ul) return;

            const emptyMessage = ul.querySelector("li:not(.quest-item)");
            const hasQuests = ul.querySelector(".quest-item");

            if (emptyMessage && hasQuests) {
            emptyMessage.remove();
            }
        });
    }

    // add one event listener to entire document
    document.addEventListener("submit", async (e) => {
        const form = e.target;

        // DELETE
        if (form.classList.contains("delete-form")) {
        e.preventDefault();

        if (!confirm("Delete this quest?")) return;

        const response = await fetch(form.action, {
            method: "POST",
            headers: {
            "X-Requested-With": "XMLHttpRequest"
            },
            body: new FormData(form)
        });

        if (response.ok) {
            form.closest(".quest-item")?.remove();

            removeEmptyMessages();
            updateStats();
        } else {
            alert("Failed to delete quest.");
        }
        return;
        }

        // COMPLETE
        if (form.classList.contains("complete-form")) {
        e.preventDefault();

        const csrfToken = form.querySelector('input[name="csrf_token"]')?.value;

        const response = await fetch(form.action, {
            method: "POST",
            headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken
            },
            body: new FormData(form)
        });

        if (!response.ok) {
            alert("Failed to complete quest.");
            return;
        }

        const questItem = form.closest(".quest-item");
        if (!questItem) return;

        questItem.classList.add("complete");
        questItem.setAttribute("data-status", "completed");

        const title = questItem.querySelector(".quest-title");

        if (title) {
            title.textContent = "✅ " + title.textContent.replace(/^❌\s/, "");
        }

        const questId = form.action.split("/").slice(-2)[0];
        const actionsDiv = questItem.querySelector(".quest-actions");

        actionsDiv.innerHTML = `
            <form method="POST" action="/quest/${questId}/uncomplete" class="uncomplete-form">
            <input type="hidden" name="csrf_token" value="${csrfToken}">
            <button class="btn btn-gold btn-sm">Uncomplete</button>
            </form>

            <form method="POST" action="/quest/${questId}/delete" class="delete-form">
            <input type="hidden" name="csrf_token" value="${csrfToken}">
            <button type="submit" class="btn btn-danger btn-sm">Delete</button>
            </form>
        `;

        document.querySelector("#completed-section ul").prepend(questItem);

        removeEmptyMessages();
        updateOverdueIcon(questItem);
        updateStats();

        return;
        }

        // UNCOMPLETE
        if (form.classList.contains("uncomplete-form")) {
        e.preventDefault();

        const csrfToken = form.querySelector('input[name="csrf_token"]')?.value;

        const response = await fetch(form.action, {
            method: "POST",
            headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken
            },
            body: new FormData(form)
        });

        if (!response.ok) {
            alert("Failed to uncomplete quest.");
            return;
        }

        const questItem = form.closest(".quest-item");
        if (!questItem) return;

        questItem.classList.remove("complete");
        questItem.setAttribute("data-status", "active");

        const title = questItem.querySelector(".quest-title");

        if (title) {
            title.textContent = title.textContent.replace("✅ ", "");
        }

        const questId = form.action.split("/").slice(-2)[0];
        const actionsDiv = questItem.querySelector(".quest-actions");

        actionsDiv.innerHTML = `
            <a href="/quest/${questId}/edit" class="btn btn-outline btn-sm">Edit</a>

            <form method="POST" action="/quest/${questId}/complete" class="complete-form">
            <input type="hidden" name="csrf_token" value="${csrfToken}">
            <button class="btn btn-outline btn-sm">Complete</button>
            </form>

            <form method="POST" action="/quest/${questId}/delete" class="delete-form">
            <input type="hidden" name="csrf_token" value="${csrfToken}">
            <button type="submit" class="btn btn-danger btn-sm">Delete</button>
            </form>
        `;

        const dueDate = questItem.dataset.dueDate;

        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const questDueDate = new Date(dueDate);
        questDueDate.setHours(0, 0, 0, 0);

        const isOverdue =
            dueDate &&
            questDueDate < today &&
            questItem.dataset.status !== "completed";

        if (isOverdue) {
            document.querySelector("#overdue-section ul").prepend(questItem);
            questItem.setAttribute("data-status", "overdue");
        } else {
            document.querySelector("#active-section ul").prepend(questItem);
            questItem.setAttribute("data-status", "active");
        }

        removeEmptyMessages();
        updateOverdueIcon(questItem);
        updateStats();

        return;
        }
    });
});