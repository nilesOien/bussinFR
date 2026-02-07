
/**
 * Calculates the distance between two geographical points using the Haversine formula.
 *
 * @param {number} lat1 - Latitude of the first point in degrees.
 * @param {number} lon1 - Longitude of the first point in degrees.
 * @param {number} lat2 - Latitude of the second point in degrees.
 * @param {number} lon2 - Longitude of the second point in degrees.
 * @returns {number} The distance in kilometers.
 *
 * As you can probably guess I absolutely AI'd this - Niles.
 */
function distanceBetweenPoints(lat1, lon1, lat2, lon2) {
    const R = 6371.0; // Radius of the Earth in kilometers (mean value)
    const toRadians = (deg) => deg * (Math.PI / 180);

    // Convert degrees to radians
    const rlat1 = toRadians(lat1);
    const rlon1 = toRadians(lon1);
    const rlat2 = toRadians(lat2);
    const rlon2 = toRadians(lon2);

    // Haversine formula components
    const dlon = rlon2 - rlon1;
    const dlat = rlat2 - rlat1;

    const a = Math.sin(dlat / 2) * Math.sin(dlat / 2) +
              Math.cos(rlat1) * Math.cos(rlat2) *
              Math.sin(dlon / 2) * Math.sin(dlon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    // Calculate the final distance
    const distance = R * c;

    return distance;
}

// Add busses to the map.
async function doBus(){

    let bounds = map.getBounds();
    let sw = bounds.getSouthWest();
    let ne = bounds.getNorthEast();

    let url=config['webservicesURL'] + "/vehicleService?minLat=" +
      sw.lat + "&minLon=" + sw.lng + "&maxLat=" + ne.lat + "&maxLon=" + ne.lng;

    let response = await fetch(url);

    if (response.status != 200) {
      alert(response.statusText);
      return;
    }

    let responseText = await response.text();

    try {
      vehicles = JSON.parse(responseText);
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

    vehiclePopups = new Array();
    for (const vehicle of vehicles){
      var vPop = L.popup()
       .setLatLng([vehicle['lat'], vehicle['lon']])
       .setContent(vehicle['route'] + " bearing " + vehicle['bearing'])
       .openOn(map);
      vehiclePopups.push(vPop);
    }

    return;

}
