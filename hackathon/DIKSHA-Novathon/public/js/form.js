document.getElementById('questionForm').addEventListener('submit', function(event) {
    event.preventDefault(); 
    
   
    var formData = new FormData(this);
    
   
    for (var pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }
    
    
    this.reset();
});
