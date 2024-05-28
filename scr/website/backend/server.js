const express = require('express');
const fs = require('fs');
const Papa = require('papaparse');
const app = express();

app.use(express.static('public'));

app.get('/csv-data', (req, res) => {
    const file = fs.createReadStream('Data\\filterDatarev2.csv');
    let data = [];

    Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        complete: function(results) {
            console.log('CSV parsing complete:', results.data);
            res.json(results.data);  // Send the data to the client as JSON
        }
    });
});


const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
