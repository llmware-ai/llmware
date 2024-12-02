document.addEventListener('DOMContentLoaded', () => {
    const topicInput = document.getElementById('topicInput');
    const generateBtn = document.getElementById('generateBtn');

    generateBtn.addEventListener('click', () => {
        const topic = topicInput.value.trim();
        if (topic) {
            // Redirect to results page with topic
            window.location.href = `/results?topic=${encodeURIComponent(topic)}`;
;
        } else {
            alert('Please enter a study topic');
        }
    });
});