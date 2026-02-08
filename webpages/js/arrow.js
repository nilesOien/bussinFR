// Returns an arrow file name for a given angle.
function arrow(angle){

 while (angle < 0.0){
  angle += 360.0;
 }

 while (angle > 360.0){
  angle -= 360.0;
 }

 if (angle <= 5.0) {
  return 'arrow_000.png';
 }

 if (angle >= 355.0){
  return 'arrow_000.png';
 }

 x=angle/10.0;
 angle=10*Math.round(x);

 ang=String(angle).padStart(3, '0');

 return 'arrow_' + ang + '.png';

}
