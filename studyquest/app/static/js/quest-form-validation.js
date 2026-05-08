document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("quest_form").addEventListener("submit", validateForm);
});

function validateForm(event) {
    clearErrors();

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const questType = document.getElementById('quest_type').value;
    const difficulty = document.getElementById('difficulty').value;
    const dueDate = document.getElementById('due_date').value;

    let isValid = true;

    if (title.trim() === '') {
        document.getElementById('title-error').textContent = 'Quest title is required.';
        isValid = false;
    }

    if (description.trim() === '') {
        document.getElementById('description-error').textContent = 'Description is required.';
        isValid = false;
    } else if (description.length < 10) {
        document.getElementById('description-error').textContent = 'Description must be at least 10 characters.';
        isValid = false;
    }

    if (questType === '') {
        document.getElementById('quest_type-error').textContent = 'Please select a quest type.';
        isValid = false;
    }

    if (difficulty === '') {
        document.getElementById('difficulty-error').textContent = 'Please select a difficulty.';
        isValid = false;
    }

    if (dueDate) {
        const selectedDate = new Date(dueDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (selectedDate < today) {
            document.getElementById('due_date-error').textContent =  'Due date cannot be in the past.';
            isValid = false;
        }
    }

    if (!isValid) {
        event.preventDefault(); 
    }

    return isValid;
}

function clearErrors() {
    document.getElementById('title-error').textContent = '';
    document.getElementById('description-error').textContent = '';
    document.getElementById('quest_type-error').textContent = '';
    document.getElementById('difficulty-error').textContent = '';
    document.getElementById('due_date-error').textContent = '';
}