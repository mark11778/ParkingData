const express = require('express');
const fs = require('fs');
const Papa = require('papaparse');

const app = express();

// Serve static files from the 'public' directory
app.use(express.static('public'));


// Path to your local CSV file
const filePath = 'Data\\springSt.csv';

app.get('/parse-csv', (req, res) => {
    const fileStream = fs.createReadStream(filePath);

    let data = [];
    Papa.parse(fileStream, {
        header: true,
        step: function(result) {
            data.push(result.data);
        },
        complete: function() {
            console.log('Finished parsing.');
            res.send(data);  // Send parsed data to client or just log it to the console
        }
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
