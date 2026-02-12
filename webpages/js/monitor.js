
// Start monitoring a bus station.
function monitorStart(indx){

 // Set the global vars.
 monitoredStationDetails = stationDetails[indx];

 clrButton = "<br><input type=\"button\" value=\"Clear\" onClick=\"monitorEnd()\">";

 document.getElementById('monitorStopPara').innerHTML =
 '<HR><B>Monitoring ' + monitoredStationDetails['stopname'] + '</b><br>ID ' + monitoredStationDetails['stopid'] +
        '<br>' + monitoredStationDetails['stopdesc'] + clrButton;

 document.getElementById('monitorUpdatePara').innerHTML ='';
 document.getElementById('monitorPara').innerHTML ='';

 monitorUpdateSec=0;
 if (!(monitoring)){
  monitoring=true; 
  monitor();
 }

 return;
}

// Stop monitoring.
function monitorEnd(){

 document.getElementById('monitorStopPara').innerHTML ='';
 document.getElementById('monitorUpdatePara').innerHTML ='';
 document.getElementById('monitorPara').innerHTML ='';
 
 monitoring=false;
 monitorUpdateSec=0;
 return;

}

// Monitor the selected station - look for updates
// as appropriate.
async function monitor(){

 // Did we stop monitoring? Return if so.
 if (!(monitoring)){
  monitorUpdateSec=0;
  return;
 }

 // We're still monitoring. We will be back in 1 second.
 setTimeout(monitor,1000);

 // Do we still have time before an update?
 // If so then tell the user and return.
 if (monitorUpdateSec > 0){
  monitorUpdateSec = monitorUpdateSec - 1;
  document.getElementById('monitorUpdatePara').innerHTML = "Next update on stop " +
   monitoredStationDetails['stopid'] + " in " + monitorUpdateSec + " seconds";
   return;
 }

 // If we got to here, we're doing the update.
 // Reset the count.
 monitorUpdateSec = config['updateSec'];


 // Get the arrival data.

 let url=config['webservicesURL'] + "/tripService?stopID=" +
  monitoredStationDetails['stopid'];

 let response = await fetch(url);

 if (response.status != 200) {
   alert(response.statusText);
   return;
 }

 let responseText = await response.text();

 try {
   var arrivals = JSON.parse(responseText);
 } catch (error) {
   alert("Error parsing vehicle JSON:", error.message);
   return;
 }

 // Arrivals data looks like :
 // [
 //   {
 //     "route": "NRTH",
 //     "arrivaltime": 1769972166
 //   },
 //   {
 //     "route": "SOUT",
 //     "arrivaltime": 1769973002
 //   },
 //   {
 //     "route": "WEST",
 //     "arrivaltime": 1769973249
 //   },
 //   {
 //     "route": "WEST",
 //     "arrivaltime": 1769975812
 //   }
 // ] 

 let current_sec = Math.floor(Date.now() / 1000);
 let ar = timeFormat(current_sec);
 let tmStr = ar[0];

 arrivalHTML = "Expect " + arrivals.length + " arrivals at stop " + monitoredStationDetails['stopid'] +
               " as of " + tmStr + "<br>";

 if (arrivals.length > 0){
  arrivalHTML += "<table class=\"center\">";
  arrivalHTML += "<tr><th>Route</th><th>Time</th><th>Minutes</th></tr>";
  for (const arrival of arrivals){
   tarr = timeFormat(arrival['arrivaltime']);
   arrivalHTML += "<tr><td>" + arrival['route'] + "</td><td>" +
                  tarr[0] + "</td><td>" + tarr[1] + "</td></tr>";
  }
  arrivalHTML += "</table>";
 }

 document.getElementById('monitorPara').innerHTML = arrivalHTML;


 return;

}

