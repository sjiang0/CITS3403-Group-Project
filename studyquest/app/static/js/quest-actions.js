document.addEventListener("DOMContentLoaded", () => {
  document.addEventListener("submit", async (e) => {
    const form = e.target;

    // Delete quest AJAX
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
      } else {
        alert("Failed to delete quest.");
      }
      return;
    }

    // Complete quest AJAX
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
      if (title && !title.textContent.startsWith("✅")) {
        title.textContent = "✅ " + title.textContent;
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

      return;
    }

    // Uncomplete quest AJAX
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

      const isOverdue =
        dueDate &&
        new Date(dueDate) < new Date();

      if (isOverdue) {
        document.querySelector("#overdue-section ul").prepend(questItem);
      } else {
        document.querySelector("#active-section ul").prepend(questItem);
      }
      return;
    }
  });
});