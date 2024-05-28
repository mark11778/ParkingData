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


function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 43.0722, lng: -89.4008 },
        zoom: 14    });

       getRoads(map)
}

function getRoads(map) {
    if (map == null) return;
    fetch('/csv-data')
    .then(response => response.json())
    .then(data => {
        if (data != null) {
            data.forEach(item => {
                if(item != null || item.CoordList != null || item.fullStreetName != null){
                    new google.maps.Polyline({
                        path: getCoords(item.CoordList),
                        tag: item.fullStreetName,
                        geodesic: true,
                        strokeColor: "#0000FF",
                        strokeOpacity: 1.0,
                        strokeWeight: 2,
                        }).setMap(map);
                }
          
            });
        }
    })
    .catch(error => console.error('Error loading CSV data:', error));
}        

function getCoords(str) {
    if( str === "" || str === null) return [];
    coords = [];
    
    listCoords = str.slice(1,-1).split(",");
    console.log(listCoords)
    for (let i = 0; i < (listCoords.length /2); i++) {
        coords.push({lat:Number(listCoords[i*2+1].slice(0,-1)) , lng:Number(listCoords[i*2].trim().slice(1))})
    }
    console.log(coords)
    return coords;
}