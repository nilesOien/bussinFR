// Take the routes from the text box, load them
// into the global variable, and then trigger a vehicle update.
function applyRoutes(){
 routesCSV=document.getElementById("routeBox").value;
 if (routesCSV.length == 0){
  document.getElementById("routePara").innerHTML="";
 } else {
  document.getElementById("routePara").innerHTML="Filtering for routes : <B>" + routesCSV + "</b>";
 }
 vehicleUpdateSec=0;
 return;
}
