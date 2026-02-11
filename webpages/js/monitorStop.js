
// Start monitoring a bus station.
function monitorStop(indx){

 stationDetail = stationDetails[indx];

 clrButton = "<br><input type=\"button\" value=\"Clear\" onClick=\"clearMonitor()\">";

 document.getElementById('monitorStopPara').innerHTML =
 '<HR><B>Monitoring ' + stationDetail['stopname'] + '</b><br>ID ' + stationDetail['stopid'] +
        '<br>' + stationDetail['stopdesc'] + clrButton;

 return;
}

// Stop monitoring.
function clearMonitor(){

 document.getElementById('monitorStopPara').innerHTML ='';
 return;

}
