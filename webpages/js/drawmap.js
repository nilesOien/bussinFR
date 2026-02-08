
function mapHasChanged(){
 vehicleUpdateSec=0; // Trigger redraw of vehicles.
 return;
}

async function drawmap(){

 // Get the configuration file.
 let response = await fetch('config.json');

 if (response.status != 200) {
  alert(response.statusText);
  return;
 }

 let configText = await response.text();

 const linesArray = configText.split(/\r?\n|\r|\n/g);

 // Parse the text into one long string.
 jsonText='';
 for (const line of linesArray){
  items=line.split('#!'); // The #! is the comment delimiter in that file
  jsonText += items[0].replace(/[\u0000-\u001F\u007F-\u009F]/g, '');
 }

 // Turn the JSON into an object and put it in the global
 // variable 'config' (see globals.js).
 try {
  config = JSON.parse(jsonText);
 } catch (error) {
  console.error("Error parsing JSON:", error.message);
  return;
 }

 // alert(JSON.stringify(config));

 // OK, have the config.
 // Set the tab title, header, and footer.
 document.title=config['tabTitle'];
 document.getElementById('headerPara').innerHTML = config['header'];
 document.getElementById('footerPara').innerHTML = config['footer'];

 // The map part is from https://leafletjs.com/examples/quick-start
 map = L.map('map').setView([config['mapLat'], config['mapLng']], config['initZoom']);

 tileLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: config['maxZoom'],
    minZoom: config['minZoom'],
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
 });

 tileLayer.addTo(map);

 // Add the listener function mapHasChanged() for zoom state changes and recentering.
 map.on('zoomend', mapHasChanged);
 map.on('moveend', mapHasChanged);

 // Start the drawing of vehicles here (after config has loaded)
 drawVehicles();

 return;

}

