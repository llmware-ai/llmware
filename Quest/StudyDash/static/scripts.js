$(document).ready(function() {
    $('#summarizeForm').submit(function(event) {
        event.preventDefault();
        var documentText = $('#documentText').val();
        var modelName = $('#modelSelect').val();
        
        $.ajax({
            url: '/summarize',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ document_text: documentText, model_name: modelName }),
            success: function(response) {
                $('#summaryOutput').text(response.summary);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $('#sentimentForm').submit(function(event) {
        event.preventDefault();
        var formData = {
            'essay_text': $('#essayText').val()
        };
        $.ajax({
            type: 'POST',
            url: '/analyze_sentiment',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                $('#sentimentOutput').html('<p>Sentiment: ' + response.sentiment + '</p>');
                $('#sentimentOutput').append('<p>Confidence: ' + response.confidence + '</p>');
            },
            error: function(error) {
                console.log('Error:', error);
            }
        });
    });   

    $('#chatForm').submit(function(event) {
        event.preventDefault();
        var userInput = $('#userInput').val(); // Fetch user input correctly
        var modelName = $('#modelSelectChat').val(); // Fetch selected model (optional)
        
        var formData = {
            'user_input': userInput,
            'model_name': modelName
        };

        $.ajax({
            type: 'POST',
            url: '/chat',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                console.log(response); // Log response for debugging
                
                // Update chat output
                $('#chatOutput').append('<div class="user-message">You: ' + userInput + '</div>');
                $('#chatOutput').append('<div class="bot-message">Bot: ' + response.response.llm_response + '</div>');
                $('#userInput').val(''); 
            },
            error: function(error) {
                console.log('Error:', error);
            }
        });
    });
});