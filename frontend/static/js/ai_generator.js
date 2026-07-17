function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (const cookieItem of cookies) {
            const cookie = cookieItem.trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function () {
    const generateBtn = document.getElementById('generate-ai-btn');
    if (!generateBtn) return;

    const titleField = document.getElementById('task-title-field');
    const descField = document.getElementById('task-description-field');
    const errorMsg = document.getElementById('ai-error-msg');

    generateBtn.addEventListener('click', async function () {
        const title = titleField.value.trim();
        const description = descField.value.trim();

        if (!title) {
            errorMsg.textContent = "Please enter a title first.";
            errorMsg.style.display = 'block';
            return;
        }

        errorMsg.style.display = 'none';

        // Save original button content
        const originalContent = generateBtn.innerHTML;
        generateBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 16px; animation: spin 1s linear infinite;">sync</span> Generating...';
        generateBtn.disabled = true;

        const csrftoken = getCookie('csrftoken');

        try {
            const response = await fetch('/api/generate-description/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    title: title,
                    description: description
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                descField.value = data.data.description;
            } else {
                errorMsg.textContent = data.message || "Failed to generate description. Rate limit exceeded?";
                errorMsg.style.display = 'block';
            }
        } catch (error) {
            console.error('Failed to generate description:', error);
            errorMsg.textContent = "Network error. Please try again.";
            errorMsg.style.display = 'block';
        } finally {
            generateBtn.innerHTML = originalContent;
            generateBtn.disabled = false;
        }
    });
});
