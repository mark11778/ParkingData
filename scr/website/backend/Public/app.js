function getCoords(str) {
    if(str === "" || str === null) return [];
    let coords = [];
    let listCoords = str.slice(1,-1).split(",");
    if (listCoords.length <= 1) return coords;
    for (let i = 0; i < (listCoords.length /2); i++) {
        coords.push({lat:Number(listCoords[i*2+1].slice(0,-1)), lng:Number(listCoords[i*2].trim().slice(1))});
    }
    return coords;
}

function callPythonFunction(map) {
    fetch('http://localhost:5000/python-function?data=hello')
        .then(response => response.json())
        .then(data => {
            if (map == null) return;
            data.result.forEach(item => {
                console.log(item);
                if(item.CoordList && item.fullStreetName) {
                    new google.maps.Polyline({
                        path: getCoords(item.CoordList),
                        tag: item.fullStreetName,
                        geodesic: true,
                        strokeColor: item.color || "#0000FF",
                        strokeOpacity: 1.0,
                        strokeWeight: 4,
                    }).setMap(map);
                }
            });
            displayDataAsTable(data.result);
        })
        .catch(error => console.error('Error:', error));
}

function displayDataAsTable(data) {
    const container = document.getElementById('pythonData');
    container.innerHTML = '';  // Clear previous data
    
    if (data.length === 0) {
        container.textContent = 'No data available';
        return;
    }
    
    // Create table
    const table = document.createElement('table');
    table.border = '1';
    
    // Create header row
    const headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        const th = document.createElement('th');
        th.textContent = key;
        headerRow.appendChild(th);
    });
    table.appendChild(headerRow);
    
    // Create data rows
    data.forEach(item => {
        const row = document.createElement('tr');
        Object.values(item).forEach(value => {
            const td = document.createElement('td');
            td.textContent = value;
            row.appendChild(td);
        });
        table.appendChild(row);
    });
    
    container.appendChild(table);
}

window.onload = function() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 43.0722, lng: -89.4008 },
        zoom: 14
    });
    
    callPythonFunction(map);
};
