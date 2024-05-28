document.getElementById('loadData').addEventListener('click', function() {
    fetch('/parse-csv')
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to fetch data');
            }
        })
        .then(data => {
            displayData(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.getElementById('dataDisplay').innerHTML = 'Error loading data.';
        });
});

function displayData(data) {
    const display = document.getElementById('dataDisplay');
    display.innerHTML = '';  // Clear previous data

    if (data.length > 0) {
        const table = document.createElement('table');
        table.setAttribute('border', '1');

        // Optional: Create a header row
        const headerRow = table.insertRow();
        Object.keys(data[0]).forEach(key => {
            const cell = headerRow.insertCell();
            cell.textContent = key;
        });

        // Create rows for each record
        data.forEach(row => {
            const tableRow = table.insertRow();
            Object.values(row).forEach(value => {
                const cell = tableRow.insertCell();
                cell.textContent = value;
            });
        });

        display.appendChild(table);
    } else {
        display.innerHTML = 'No data available.';
    }
}
