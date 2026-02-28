
// Add vehicles to the map.
async function drawVehicles(){

    // First things first - we're calling again in 1 second
    setTimeout(drawVehicles, 1000);

    // Decrement the global counter.
    vehicleUpdateSec -= 1;
    if (vehicleUpdateSec > 0){ // We still have to wait.
      document.getElementById('updatePara').innerHTML = 'Next vehicle position update in ' + vehicleUpdateSec + ' seconds.';
      return;
    }

    // If we got here, we're doing an update. Reset the clock.
    vehicleUpdateSec = config['updateSec'];

    // Check if map is zoomed out too far to even try
    mapZoom = map.getZoom();
    if (mapZoom < config['minZoomForVehicles']){
      removeVehicles();
      document.getElementById('vehicleInfoPara').innerHTML = 'Map is zoomed out to level ' + mapZoom +
         ' need to zoom in to level ' + config['minZoomForVehicles'] + ' to show vehicles.';
      return;
    }

    let bounds = map.getBounds();
    let sw = bounds.getSouthWest();
    let ne = bounds.getNorthEast();

    let url=config['webservicesURL'] + "/vehicleService?minLat=" +
      sw.lat + "&minLon=" + sw.lng + "&maxLat=" + ne.lat + "&maxLon=" + ne.lng;
    if (routesCSV.length > 0){
      url += "&routesCSV=" + routesCSV;
    }

    let response = await fetch(url);

    if (response.status != 200) {
      alert(response.statusText);
      return;
    }

    let responseText = await response.text();

    try {
      var vehicles = JSON.parse(responseText);
    } catch (error) {
      alert("Error parsing vehicle JSON:", error.message);
      return;
    }

    // What we got should look like this :
    // [
    //  {
    //    "route": "WEST",
    //    "timestamp": 1769905251,
    //    "current_status": 2,
    //    "lat": 39.063350677490234,
    //    "lon": -108.56390380859375,
    //    "bearing": 79
    //  },
    //  {
    //    "route": "SOUT",
    //    "timestamp": 1769905235,
    //    "current_status": 2,
    //    "lat": 39.53459930419922,
    //    "lon": -104.8725814819336,
    //    "bearing": 269
    //  }
    // ]

    // Are there just too many vehicles to show?
    if (vehicles.length > config['maxVehicles']){
      removeVehicles();
      document.getElementById('vehicleInfoPara').innerHTML = "There are " + vehicles.length +
        " vehicles in the region, the limit is " + config['maxVehicles'] + ", not showing vehicles, try zooming in.";
      return;
    }

    // Get the data into the vehicleLocs array
    let vehicleLocs = new Array();
    for (const vehicle of vehicles){
       pos = [vehicle['lat'], vehicle['lon']];
       im='Yes';
       if (vehicle['current_status'] != 2){ // current_status == 2 => in motion
        im='No';
       }

       let tArray=timeFormat(vehicle['timestamp']);
       let tmStr=tArray[0];
       let tRel=tArray[1];

       status = '<B>Route ' + vehicle['route'] + '</b>' + " bearing " + vehicle['bearing'] +
           "<br>Time : " + tmStr + "<br>" + tRel + "<br>In motion : " + im;

       v = { "pos": pos, "status": status, "bearing": vehicle['bearing'], "current_status": vehicle['current_status'] };

      vehicleLocs.push(v);
    }


    removeVehicles(); // Remove any existing markers
    // Go through the information in vehicleLocs and put the markers on the map.
    vehicleLocs.forEach(vehicleLoc => {

           fullFile= config['webservicesURL'] + '/icons/stopped_bus.png';
           if (vehicleLoc['current_status'] == 2){
               af=arrow(vehicleLoc['bearing']);
               fullFile= config['webservicesURL'] + '/arrows/black/' + af;
           }

           var vehicleIcon = L.icon({
             iconUrl: fullFile,
             iconSize: [20, 20],
             iconAnchor: [10, 10],
             popupAnchor: [0, -10]
           });

           let m = L.marker(vehicleLoc['pos'], {icon: vehicleIcon}) // Create a new marker
                  .addTo(map) // Add the marker to the map
                  .bindPopup(vehicleLoc['status']); // Bind a clickable popup with the status message we put together
           vehicleMarkers.push(m);
                });

    document.getElementById('vehicleInfoPara').innerHTML = 'Displaying ' + vehicleMarkers.length + ' vehicles';

    return;

}

// Remove the vehicle markers from the map.
function removeVehicles() {

 vehicleMarkers.forEach(vehicleMarker => {
  vehicleMarker.remove();
 });                      
 vehicleMarkers = new Array();

 return;

}

