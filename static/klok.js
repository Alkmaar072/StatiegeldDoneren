$(document).ready(function(){

//functies die tijd kunnen lezen
var today = new Date();
var curHr = today.getHours();

//if-else statement om op hero-image te groeten, afgesteld op bepaald moment van de dag
if (curHr >= 0 && curHr < 6){
    document.getElementById("groet").innerHTML = "Goedenacht!";
}
else if (curHr >= 6 && curHr < 12){
    document.getElementById("groet").innerHTML = "Goedemorgen!";
}
else if (curHr >= 12 && curHr < 18){
    document.getElementById("groet").innerHTML = "Goedemiddag!";
}
else{
    document.getElementById("groet").innerHTML = "Goedenavond!";
}

});


