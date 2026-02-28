// The map that we set up through Leaf.
var map;

// The config we get from the JSON on the server.
var config;

// The vehicle markers we put on the map.
var vehicleMarkers = new Array();

// The number of seconds until we update the vehicles on the map.
var vehicleUpdateSec=0;

// The station details we got from the server.
var stationDetails;

// The station marker objects.
var stationMarkers = new Array();

// Are we monitoring a station?
var monitoring=false;

// Monitored station details. This will be a dict.
var monitoredStationDetails;

// Update seconds for monitoring
var monitorUpdateSec = 0;

// Comma separated list of routes, if any
var routesCSV = "";

