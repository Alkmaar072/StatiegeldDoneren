let organisatie = "";

$(document).ready(function () {
  // Kijk of er een organisatie parameter is
  const searchParams = new URLSearchParams(window.location.search);
  if (searchParams.has("organisatie")) {
    organisatie = searchParams.get("organisatie");
  }

  // Zorg voor blur als er geen organisatie is
  if (!organisatie) {
    document.getElementById("content-block").style.position = "relative";
  } else {
    document.getElementById("blur").style.display = "none";
    document.getElementById("content-block").style.position = "unset";
  }

  // Haal de benodigde gegevens om aantallen te kunnen aanpassen
  const hoogBtn = document.getElementsByClassName("hoog");
  const laagBtn = document.getElementsByClassName("laag");
  const inputAantal = document.getElementsByClassName("aantal");
  const subtotaalEuro = document.getElementById("subtotaalEuro");
  const subtotaalPunt = document.getElementById("subtotaalPunt");

  // Onchange voor input zodat de gegevens veranderen bij een wijziging
  // Voeg onchange toe
  for (let i = 0; i < inputAantal.length; i++) {
    let input = inputAantal[i];
    input.addEventListener("change", function (event) {
      // Lees aatal en waarde uit
      let totaal = 0;
      for (let j = 0; j < inputAantal.length; j++) {
        let aantal = inputAantal[j];
        let waarde = aantal.parentElement.children[2].children[0].innerHTML;
        totaal += aantal.value * waarde;
      }

      // Pas totaal aan
      subtotaalPunt.innerHTML = Math.round(parseFloat(totaal) * 100);
      subtotaalEuro.innerHTML = Math.round(parseFloat(totaal) * 100) / 100;
    });
  }

  // Onclick om aantallen te kunnen plussen
  // Voeg onclick toe
  for (let i = 0; i < hoogBtn.length; i++) {
    let btn = hoogBtn[i];
    btn.addEventListener("click", function (event) {
      // Lees aantal en waarde uit
      let btnKlik = event.target;
      let waarde =
        btnKlik.parentElement.parentElement.children[2].children[0].innerHTML;
      let input = btnKlik.parentElement.parentElement.children[4];
      let inputWaarde = input.value;

      // Pas waardes aan
      input.value = parseInt(inputWaarde) + 1;
      subtotaalPunt.innerHTML =
        parseFloat(subtotaalPunt.innerHTML) + parseFloat(waarde) * 100;
      subtotaalEuro.innerHTML =
        Math.round(
          (parseFloat(subtotaalEuro.innerHTML) + parseFloat(waarde)) * 100
        ) / 100;
    });
  }

  // Voeg onclick toe
  for (let i = 0; i < laagBtn.length; i++) {
    let btn = laagBtn[i];
    btn.addEventListener("click", function (event) {
      // Lees aantal en waarde uit
      let btnKlik = event.target;
      let waarde =
        btnKlik.parentElement.parentElement.children[2].children[0].innerHTML;
      let input = btnKlik.parentElement.parentElement.children[4];
      let inputWaarde = input.value;

      // Pas waardes aan en controleer of de waarde niet negatief wordt
      let nieuwWaarde = parseInt(inputWaarde) - 1;
      if (nieuwWaarde >= 0) {
        input.value = nieuwWaarde;
        subtotaalPunt.innerHTML =
          parseFloat(subtotaalPunt.innerHTML) - parseFloat(waarde) * 100;
        subtotaalEuro.innerHTML =
          Math.round(
            (parseFloat(subtotaalEuro.innerHTML) - parseFloat(waarde)) * 100
          ) / 100;
      } else {
        input.value = 0;
      }
    });
  }
});

// Donatie vastleggen in db
function submitDoneren() {
  // Lees aantallen uit en maak json object voor AJAX-call
  let aantal = document.getElementsByClassName("aantal");
  let donatie = {};
  donatie["organisatieId"] = organisatie;
  let artikelen = [];

  // Controleer of er een organisatie is
  if (!organisatie) {
    alert("Geen organisatie gekozen");
  } else {
    // Lees gegevens van de artikelen uit
    for (let i = 0; i < aantal.length; i++) {
      let value = aantal[i].value;
      let id = aantal[i].id;
      let artikel = {};
      if (value > 0) {
        artikel["id"] = id;
        artikel["value"] = value;
        artikelen.push(artikel);
      }
    }

    // Controleer of er artikelen geselecteerd zijn
    if (artikelen.length === 0) {
      alert("Geen artikelen geselecteerd.");
    } else {
      donatie["artikelen"] = artikelen;

      // Statiegeld aanmelden AJAX-call om donatie vast te leggen
      $.ajax({
        url: "/statiegeld_aanmelden/donatie",
        type: "POST",
        data: JSON.stringify(donatie),
        success: function () {
          window.location.href = "/dashboard_organisatie";
        },
        contentType: "application/json",
        dataType: "json",
      });
    }
  }
}

// Schone pagina herladen
function weigerenDoneren() {
  window.location.href = "/statiegeld_aanmelden";
}
