
// Draw the bus stops on the map.
async function drawStops(){


    // Check if map is zoomed out too far to even try
    mapZoom = map.getZoom();
    if (mapZoom < config['minZoomForStations']){
      removeStops();
      document.getElementById('stopInfoPara').innerHTML = 'Map is zoomed out to level ' + mapZoom +
         ' need to zoom in to level ' + config['minZoomForStations'] + ' to show stops.';
      return;
    }

    let bounds = map.getBounds();
    let sw = bounds.getSouthWest();
    let ne = bounds.getNorthEast();

    let url=config['webservicesURL'] + "/busStopService?minLat=" +
      sw.lat + "&minLon=" + sw.lng + "&maxLat=" + ne.lat + "&maxLon=" + ne.lng;

    let response = await fetch(url);

    if (response.status != 200) {
      alert(response.statusText);
      return;
    }

    let responseText = await response.text();

    try {
      stationDetails = JSON.parse(responseText);
    } catch (error) {
      alert("Error parsing vehicle JSON:", error.message);
      return;
    }

    // What we have in the global var stationDetails looks like :
    // [
    //   {
    //    "stopid": "17724",
    //    "stopname": "19th St & Stout St",
    //    "stopdesc": "Vehicles Travelling East",
    //    "lat": 39.748748,
    //    "lon": -104.989695
    //  },
    //  {
    //    "stopid": "34343",
    //    "stopname": "Union Station",
    //    "stopdesc": "Vehicles Travelling North",
    //    "lat": 39.753394,
    //    "lon": -105.000558
    //  }
    // ]

    // Are there just too many stops to show?
    if (stationDetails.length > config['maxStations']){
      removeStops();
      document.getElementById('stopInfoPara').innerHTML = "There are " + stationDetails.length +
        " stops in the region, the limit is " + config['maxStations'] + ", not showing stops, try zooming in.";
      return;
    }

    var stationIcon = L.icon({
      iconUrl: '../icons/stop.png',
      iconSize: [20, 20],
      iconAnchor: [10, 10],
      popupAnchor: [0, -10]
    });

    removeStops(); // Remove any existing markers
    // Go through the information in stationDetails and put the markers on the map.
    indx=0;
    stationDetails.forEach(stationDetail => {

           let stationHTML = '<B>' + stationDetail['stopname'] + "</b><br>ID " + stationDetail['stopid'] + '<br>' +
                             stationDetail['stopdesc'] + '<br>';

           stationHTML += "<input type=\"button\" value=\"Monitor\" onClick=monitorStart(" + indx + ")>";

           let m = L.marker([stationDetail['lat'], stationDetail['lon']], {icon: stationIcon}) // Create a new marker
                  .addTo(map) // Add the marker to the map
                  .bindPopup(stationHTML); // Bind a clickable popup with the status message we put together
           stationMarkers.push(m);

           indx += 1;

                });

    document.getElementById('stopInfoPara').innerHTML = 'Displaying ' + stationMarkers.length + ' stops';



 return;

}

// Remove the bus stop markers from the map.
function removeStops() {

 stationMarkers.forEach(stationMarker => {
  stationMarker.remove();
 });                      
 stationMarkers = new Array();

 document.getElementById('stopInfoPara').innerHTML = '';

 return;

}

