document.addEventListener('DOMContentLoaded', () => {
    const flashcardsContainer = document.getElementById('flashcardsContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const topicTitle = document.getElementById('topicTitle');
     
    // Get topic from URL
    const urlParams = new URLSearchParams(window.location.search);
    const topic = urlParams.get('topic') || 'Study Topic';
    topicTitle.textContent = `${topic} Flashcards`;
     
    // Simulate AI flashcard generation
    function generateFlashcards(topic) {
        loadingIndicator.classList.remove('hidden');
        flashcardsContainer.innerHTML = '';
         
        // Simulated async generation
        setTimeout(() => {
            const flashcards = [
                {
                    question: `What is a fundamental concept in ${topic}?`,
                    answer: `A key principle of ${topic} involves understanding...`
                },
                {
                    question: `Advanced topic in ${topic}`,
                    answer: `Deep dive into ${topic} reveals fascinating insights...`
                },
                {
                    question: `Important fact about ${topic}`,
                    answer: `Experts suggest that in ${topic}, the most critical aspect is...`
                },
                {
                    question: `A challenging aspect of ${topic}`,
                    answer: `Many students find this part of ${topic} particularly complex...`
                },
                {
                    question: `Emerging trends in ${topic}`,
                    answer: `Recent developments in ${topic} indicate that...`
                }
            ];
             
            flashcards.forEach((card, index) => {
                const flashcardDiv = document.createElement('div');
                flashcardDiv.classList.add('flashcard');
                 
                flashcardDiv.innerHTML = `
                    <div class="flashcard-inner">
                        <div class="flashcard-front">
                            <h3 class="text-xl font-semibold text-center">${card.question}</h3>
                        </div>
                        <div class="flashcard-back">
                            <p class="text-lg text-center">${card.answer}</p>
                        </div>
                    </div>
                `;
                 
                // Add flip functionality
                flashcardDiv.addEventListener('click', () => {
                    flashcardDiv.classList.toggle('flipped');
                });
                 
                flashcardsContainer.appendChild(flashcardDiv);
            });
             
            loadingIndicator.classList.add('hidden');
        }, 1500);
    }
     
    // Generate flashcards for the topic
    generateFlashcards(topic);
});