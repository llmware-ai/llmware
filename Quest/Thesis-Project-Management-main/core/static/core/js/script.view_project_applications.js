document.addEventListener('DOMContentLoaded', function () {

    const sentimentAnalysis = document.getElementById("analysis-sentiment")
    const group_id = parseInt(sentimentAnalysis.getAttribute("group_id"))

    sentimentAnalysis.addEventListener('click', function () {
        fetch(`/supervisor/analysis/${group_id}/`)
            .then(response => response.json())
            .then(data => {

                sentimentAnalysis.classList = "sentiment-value"
                
                console.log(data)
                var displayText = 'Confidence Level: ' + data.confidence_level + '<br>Sentiment Value: ' + data.sentiment_value;

                sentimentAnalysis.innerHTML = displayText;
            })
    })
})