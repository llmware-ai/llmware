const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const port = 3000;


app.use(express.static(path.join(__dirname, 'public')));


const upload = multer({ dest: 'uploads/' });


app.get('/form', (req, res) => {
    
   res.render("form.ejs");
});


app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
