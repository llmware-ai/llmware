function searchQuery() {
    var query = document.getElementById('query').value;
    if (query.trim() === '') {
        alert("Please enter a query to search.");
        return;
    }
}

function displaySearchResults(results) {
    var searchResultsDiv = document.getElementById('searchResults');
    searchResultsDiv.innerHTML = '';

    if (results.length === 0) {
        searchResultsDiv.innerHTML = '<p>No results found.</p>';
        return;
    }

    var resultList = document.createElement('ul');
    results.forEach(result => {
        var listItem = document.createElement('li');
        listItem.textContent = result;
        resultList.appendChild(listItem);
    });

    searchResultsDiv.appendChild(resultList);
}
