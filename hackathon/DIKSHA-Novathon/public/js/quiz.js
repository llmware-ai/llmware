document.addEventListener("DOMContentLoaded", function() {
    const quizForm = document.getElementById('quizForm');
    const correctAnswers = JSON.parse(quizForm.dataset.correctAnswers);
  
    quizForm.addEventListener('submit', function(event) {
      event.preventDefault(); // Prevent default form submission
  
      let userAnswers = {};
  
      // Collect user-selected answers
      correctAnswers.forEach((_, index) => {
        const selectedOption = document.querySelector(`input[name="q${index}"]:checked`);
        if (selectedOption) {
          userAnswers[`q${index}`] = selectedOption.value;
        }
      });
  
      // Send the user answers to the server via a POST request
      fetch('/submit-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userAnswers })
      })
      .then(response => response.json())
      .then(result => {
        // Handle the result (e.g., show score)
        alert(`You got ${result.correctCount} out of ${correctAnswers.length} correct.`);
      })
      .catch(error => console.error('Error:', error));
    });
  });
  