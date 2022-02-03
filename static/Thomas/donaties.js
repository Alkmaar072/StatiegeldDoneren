let url = "/donaties/alleDonaties";
let OPHAALIDS = [];
$(document).ready(function () {
  $("#donaties").DataTable({
    dom: '<"top"Bfrt><"bottom"lip>',
    buttons: [
      // Standaard buttons
      "copy", "excel", "pdf", "selectAll", "selectNone",
      // Custom buttons voor filter en ophaalmoment
      {
        text: "Alle",
        action: function (e, dt, node, config) {
          table.columns(7).search("").draw();
        },
      },
      {
        text: "Nieuwe",
        action: function (e, dt, node, config) {
          table.columns(7).search("Nieuw").draw();
        },
      },
      {
        text: "In behandeling",
        action: function (e, dt, node, config) {
          table.columns(7).search("In behandeling").draw();
        },
      },
      {
        text: "Afgerond",
        action: function (e, dt, node, config) {
          table.columns(7).search("Afgerond").draw();
        },
      },
      {
        text: "Plan ophaalmoment",
        action: function (e, dt, node, config) {
          let table = $("#donaties").DataTable();
          if (table.rows(".selected").any()) {
            // Tel de geselecteerde rijen
            let count = table.rows({ selected: true }).data();
            let nietNieuw = 0;

            // Controleer of alle rijen de status nieuw hebben
            $.each(count, function (index, value) {
              if (value.status !== "Nieuw") {
                nietNieuw++;
              }
            });
            if (!nietNieuw) {
              // Sla id van donatie op in OPHAALIDS en laat modal zien
              $.each(count, function (index, value) {
                OPHAALIDS.push(value.id);
              });
              let modal = new bootstrap.Modal(
                document.getElementById("ophaalModal")
              );
              modal.show();
            } else {
              alert("U kunt alleen nieuwe donaties ophalen.");
            }
          } else {
            alert("U heeft geen regel geselecteerd!");
          }
        },
        attr: {
          id: "planAfspraak",
        },
      },
    ],
    // Zet de tekst van de standaard buttons in nl
    language: {
      buttons: {
        copy: "Kopieer",
        selectAll: "Selecteer alles",
        selectNone: "Deselecteer alles",
      },
    },
    // AJAX-call om alle donaties op te halen
    ajax: {
      url: "/donaties/alleDonaties",
      type: "POST",
      contentType: "application/json",
    },
    pageLength: 10,
    // Gegevens aan de kolommen koppelen
    columnDefs: [
      {
        targets: 0,
        data: null,
        defaultContent: "",
        orderable: false,
        className: "select-checkbox",
      },
      {
        targets: 1,
        data: "id",
        defaultContent: "",
      },
      {
        targets: 2,
        data: "adres",
        defaultContent: "",
      },
      {
        targets: 3,
        data: "particulierId",
        orderable: false,
        // Button om naar profiel te gaan
        render: function (data, type, row, meta) {
          return (
            "<a class='btn btn-outline-primary btn-sm' href='/profile?type=particulier&id="+data+"'>zie profiel</a>"
          );
        },
      },
      {
        targets: 4,
        data: "waarde",
        defaultContent: "",
        // De waarde in euro's weergeven
        render: DataTable.render.number(".", ",", 2, "€"),
      },
      {
        targets: 5,
        data: "punten",
        defaultContent: "",
      },
      {
        targets: 6,
        data: "datum",
        defaultContent: "",
      },
      {
        targets: 7,
        data: "status",
        defaultContent: "",
      },
      {
        targets: 8,
        data: "ophaalmoment",
        defaultContent: "",
      },
      {
        targets: 9,
        data: "afgerond",
        defaultContent: "",
      },
      {
        targets: 10,
        data: null,
        orderable: false,
        // Button om donatie in te zien
        defaultContent: "<button class='btn btn-primary btn-sm'>Zie donatie in</button>",
      },
    ],
    select: {
      style: "os",
      selector: "td:first-child",
    },
    select: {
      style: "multi",
    },
  });

  var table = $("#donaties").DataTable();
  // Donaties regels inzien
  $("#donaties tbody").on("click", "button", function () {
    var data = table.row($(this).parents("tr")).data();

    // AJAX-call voor tabel donatieregels inzien
    var donatieId = { donatieId: data["id"] };
    $.ajax({
      url: "/donaties/donatieRegels",
      type: "POST",
      data: JSON.stringify(donatieId),
      success: function (donatie_regels) {
        // Vul tabel met gegevens
        $("#donatieRegelsTable tbody").empty();
        $.each(donatie_regels["data"], function (index, value) {
          console.log(value);
          $("#donatieRegelsTable > tbody:last-child").append(
            "<tr><td>" +
              value["Aantal"] +
              "</td><td>" +
              value["Naam"] +
              "</td><td>" +
              value["Omschrijving"] +
              "</td><td>€" +
              value["Waarde"] +
              "</td><td>" +
              value["Punten"] +
              "</td></tr>"
          );
        });
      },
      contentType: "application/json",
      dataType: "json",
    });

    // Laat modal zien
    let donatieRegels = new bootstrap.Modal(document.getElementById("donatieRegels"));
    donatieRegels.show();
  });
});

// Ophaalmoment vastleggen in db
function bevestigingOphaal() {
  // Lees gegevens uit
  let datum = document.getElementById("datum").value;
  let startTime = document.getElementById("startTime").value;
  let endTime = document.getElementById("endTime").value;

  // Maak json object voor AJAX-call
  let ophaalmoment = {};
  ophaalmoment["startTime"] = datum + " " + startTime;
  ophaalmoment["endTime"] = datum + " " + endTime;
  ophaalmoment["donatieId"] = OPHAALIDS;

  // AJAX-call voor plan ophaalmoment
  $.ajax({
    url: "/donaties/planOphaal",
    type: "POST",
    data: JSON.stringify(ophaalmoment),
    success: function () {
      window.location.href = "/donaties";
    },
    contentType: "application/json",
    dataType: "json",
  });
}
