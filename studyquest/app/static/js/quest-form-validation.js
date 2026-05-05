function validateForm(event) {
    clearErrors();

    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const questType = document.getElementById('quest_type').value;
    const difficulty = document.getElementById('difficulty').value;

    let isValid = true;

    if (title.trim() === '') {
        document.getElementById('title-error').textContent = 'Quest title is required.';
        isValid = false;
    }

    if (description.trim() === '') {
        document.getElementById('description-error').textContent = 'Description is required.';
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
}