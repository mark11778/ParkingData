window.onload = function() {
    fetch('/csv-data')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const container = document.getElementById('csvData');
            data.forEach(item => {
                const div = document.createElement('div');
                div.textContent = JSON.stringify(item);
                container.appendChild(div);
            });
        })
        .catch(error => console.error('Error loading CSV data:', error));
};
