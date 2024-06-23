let polylines = [];

function getCoords(str) {
    if (str === "" || str === null) return [];
    let coords = [];
    let listCoords = str.slice(1, -1).split(",");
    if (listCoords.length <= 1) return coords;
    for (let i = 0; i < (listCoords.length / 2); i++) {
        coords.push({ lat: Number(listCoords[i * 2 + 1].slice(0, -1)), lng: Number(listCoords[i * 2].trim().slice(1)) });
    }
    return coords;
}

function clearPolylines() {
    polylines.forEach(polyline => polyline.setMap(null));
    polylines = [];
}

function callPythonFunction(map, days, type) {
    fetch(`http://localhost:5000/python-function?days=${days}&type=${type}`)
        .then(response => response.json())
        .then(data => {
            clearPolylines(); // Clear existing polylines

            if (map == null) return;
            data.result.forEach(item => {
                if (item.CoordList && item.Location) {
                    const polyline = new google.maps.Polyline({
                        path: getCoords(item.CoordList),
                        tag: item.Location,
                        geodesic: true,
                        strokeColor: item.color || "#0000FF",
                        strokeOpacity: 1.0,
                        strokeWeight: 4,
                    });
                    polyline.setMap(map);
                    polylines.push(polyline); // Add new polyline to the array
                }
            });
            const uniqueData = removeDuplicates(data.result, 'fullStreetName');
            displayDataAsTable(uniqueData);
        })
        .catch(error => console.error('Error:', error));
}

function removeDuplicates(data, key) {
    const seen = new Set();
    return data.filter(item => {
        const value = item[key];
        if (seen.has(value)) {
            return false;
        }
        seen.add(value);
        return true;
    });
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
    table.dataset.sortOrder = 'asc';

    // Create header row
    const headerRow = document.createElement('tr');
    Object.keys(data[0]).forEach(key => {
        if (key !== 'CoordList' && key !== 'color' && key !== 'fullStreetName') {  // Skip CoordList and color columns
            const th = document.createElement('th');
            th.textContent = key;
            th.addEventListener('click', () => sortTableByColumn(table, key));
            headerRow.appendChild(th);
        }
    });
    table.appendChild(headerRow);

    // Create data rows
    data.forEach(item => {
        const row = document.createElement('tr');
        Object.entries(item).forEach(([key, value]) => {
            if (key !== 'CoordList' && key !== 'color' && key !== 'fullStreetName') {  // Skip CoordList and color columns
                const td = document.createElement('td');
                td.textContent = value;
                row.appendChild(td);
            }
        });
        table.appendChild(row);
    });

    container.appendChild(table);

    document.getElementById('searchInput').addEventListener('input', filterTableByLocation);
}

function filterTableByLocation() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.querySelector('#pythonData table');
    const rows = Array.from(table.rows).slice(1); // Exclude header row

    rows.forEach(row => {
        const locationCell = row.cells[1]; // Assuming the Location column is the second column
        if (locationCell) {
            const locationText = locationCell.textContent || locationCell.innerText;
            if (locationText.toLowerCase().indexOf(filter) > -1) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        }
    });
}

function sortTableByColumn(table, column) {
    const rowsArray = Array.from(table.rows).slice(1);
    const columnIndex = Array.from(table.rows[0].cells).findIndex(th => th.textContent === column);
    const isAscending = table.dataset.sortOrder === 'asc';

    rowsArray.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].textContent;
        const cellB = rowB.cells[columnIndex].textContent;

        if (isAscending) {
            return cellA.localeCompare(cellB, undefined, { numeric: true });
        } else {
            return cellB.localeCompare(cellA, undefined, { numeric: true });
        }
    });

    rowsArray.forEach(row => table.appendChild(row));

    table.dataset.sortOrder = isAscending ? 'desc' : 'asc';
}

window.onload = function() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 43.0722, lng: -89.4008 },
        zoom: 14
    });

    const daysInput = document.getElementById('daysInput');
    const typeSelect = document.getElementById('typeSelect');

    const filterData = () => {
        const days = daysInput.value;
        const type = typeSelect.value;
        callPythonFunction(map, days, type);
    };

    daysInput.addEventListener('change', filterData);
    typeSelect.addEventListener('change', filterData);

    callPythonFunction(map, 30, 'Parking'); 
};
