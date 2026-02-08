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

