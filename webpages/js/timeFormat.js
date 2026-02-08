// Small function to do time formatting.
// A UNIX time (seconds since 1970) is passed in.
//
// An array with two elements is returned.
// The first element is a string representing the time, something like "5:20 PM"
// The second element is a string representing the time's relation to the current time,
// something like "In 2 minutes" or "2 minutes ago".
//
function timeFormat(unixtime){

 const tmOptions = {
  hour: 'numeric',
  minute: 'numeric',
  timeZoneName: 'short'
 };

 const dateObject = new Date(unixtime * 1000); 
 let tmStr = dateObject.toLocaleString('en-US', tmOptions);

 let current_time = Math.floor(Date.now() / 1000);

 diffStr='';
 if (current_time >= unixtime){ // It's in the past
  minutes = Math.round((current_time - unixtime)/60.0);
  diffStr=minutes + ' minutes ago';
 } else { // It's in the future
  minutes = Math.round((unixtime - current_time)/60.0);
  diffStr='In ' + minutes + ' minutes';
 }

 ret = new Array();
 ret.push(tmStr);
 ret.push(diffStr);

 return ret;

}
