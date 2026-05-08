document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".filter-btn");
    const allBtn = document.getElementById("all-btn");

    let activeFilters = {
        status: new Set(),
        difficulty: new Set(),
        type: new Set()
    };

    // Change button styling on activt/not active
    function toggleButton(btn, active) {
        if (active) {
            btn.classList.add("btn-gold");
            btn.classList.remove("btn-outline");
        } else {
            btn.classList.add("btn-outline");
            btn.classList.remove("btn-gold");
        }
    }

    // clear all filters
    function resetAllFilters() {
        activeFilters.status.clear();
        activeFilters.difficulty.clear();
        activeFilters.type.clear();

        document.querySelectorAll(".filter-btn").forEach(btn => {
            btn.classList.remove("btn-gold");
            btn.classList.add("btn-outline");
        });

        if (allBtn) {
            allBtn.classList.add("btn-gold");
            allBtn.classList.remove("btn-outline");
        }
    }

    // checks if any filters active, changes allBtn style accordingly
    function syncAllButton() {
        const anyActive =
            activeFilters.status.size > 0 ||
            activeFilters.difficulty.size > 0 ||
            activeFilters.type.size > 0;

        if (!allBtn) return;

        if (anyActive) {
            allBtn.classList.remove("btn-gold");
            allBtn.classList.add("btn-outline");
        } else {
            allBtn.classList.add("btn-gold");
            allBtn.classList.remove("btn-outline");
        }
    }

    // core function: apply multi-filter system
    function applyFilters() {
        const sections = ["overdue", "active", "completed"];

        let anyFilterActive =
            activeFilters.status.size > 0 ||
            activeFilters.difficulty.size > 0 ||
            activeFilters.type.size > 0;

        sections.forEach(section => {
            const container = document.getElementById(`${section}-section`);
            const items = container.querySelectorAll(".quest-item");

            const sectionAllowed =
                activeFilters.status.size === 0 ||
                activeFilters.status.has(section);

            let visibleCount = 0;

            items.forEach(q => {
                const difficulty = q.dataset.difficulty;
                const type = q.dataset.type;

                const matchDifficulty =
                    activeFilters.difficulty.size === 0 ||
                    activeFilters.difficulty.has(difficulty);

                const matchType =
                    activeFilters.type.size === 0 ||
                    activeFilters.type.has(type);

                const show = matchDifficulty && matchType;

                const finalShow = sectionAllowed && show;

                q.style.display = finalShow ? "" : "none";

                if (finalShow) visibleCount++;
            });

            if (anyFilterActive) {
                container.style.display = visibleCount > 0 ? "" : "none";
            } else {
                container.style.display = "";
            }
        });
    }

    // if allBtn clicked, resets all filters 
    if (allBtn) {
        allBtn.addEventListener("click", () => {
            resetAllFilters();
            syncAllButton();   
            applyFilters();
        });
    }

    // attaches click listeners to all filter buttons. 'undoes/reverses' action if clicked
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const status = btn.dataset.section;
            const difficulty = btn.dataset.filterDifficulty;
            const type = btn.dataset.filterType;

            if (status) {
                if (activeFilters.status.has(status)) {
                    activeFilters.status.delete(status);
                    toggleButton(btn, false);
                } else {
                    activeFilters.status.add(status);
                    toggleButton(btn, true);
                }
            }

            if (difficulty) {
                if (activeFilters.difficulty.has(difficulty)) {
                    activeFilters.difficulty.delete(difficulty);
                    toggleButton(btn, false);
                } else {
                    activeFilters.difficulty.add(difficulty);
                    toggleButton(btn, true);
                }
            }
            if (type) {
                if (activeFilters.type.has(type)) {
                    activeFilters.type.delete(type);
                    toggleButton(btn, false);
                } else {
                    activeFilters.type.add(type);
                    toggleButton(btn, true);
                }
            }
            syncAllButton();   
            applyFilters();
        });
    });
    syncAllButton();
    applyFilters();
});