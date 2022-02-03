import json
from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
import datetime


import requests

from helpers import apology, login_required

import os
import re
from flask_mail import Mail, Message

# Configure application
app = Flask(__name__)
app.config["SECRET_KEY"] = "b'\x99F\x94ZX\xd7!\xae$\xdb\x99\xb6"S$%'"

if __name__ == "__main__":
    app.run(debug = True)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///statiegelddoneren.db")

# Send mail
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'statiegelddoneren@gmail.com'
app.config['MAIL_PASSWORD'] = 'berend12345'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
def index():
    return redirect("/landing")

@app.route("/dashboard_organisatie", methods=["GET", "POST"])
def dashboard():
    session["active_page"] = "dashboard"
    # De dag, week, maand en jaarwaardes bereken voor een ingelogde particulier
    if not session.get("particulier") is None:
        dagWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)), 0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE (status = 'Afgerond' AND particulier.id = :id) AND strftime('%d', donatie.afgerond_op) = strftime('%d', 'now');", id = session.get("particulier")["id"])
        maandWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)),0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE (status = 'Afgerond' AND particulier.id = :id) AND strftime('%m', donatie.afgerond_op) = strftime('%m', 'now');", id = session.get("particulier")["id"])
        weekWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)), 0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE (status = 'Afgerond' AND particulier.id = :id) AND strftime('%W', donatie.afgerond_op) = strftime('%W', 'now');", id = session.get("particulier")["id"])
        jaarWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)), 0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE (status = 'Afgerond' AND particulier.id = :id) AND strftime('%Y', donatie.afgerond_op) = strftime('%Y', 'now');", id = session.get("particulier")["id"])
        return render_template("/dashboard_organisatie.html", maandWaarde=maandWaarde, weekWaarde=weekWaarde, dagWaarde=dagWaarde, jaarWaarde=jaarWaarde)
    # De dag, week, maand en jaarwaardes bereken voor een ingelogde organisatie
    elif not session.get("organisatie") is None:
        dagWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)), 0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id WHERE (status = 'Afgerond' AND organisatie.id = :id) AND strftime('%d', donatie.afgerond_op) = strftime('%d', 'now');", id = session.get("organisatie")["id"])
        maandWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)),0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id WHERE (status = 'Afgerond' AND organisatie.id = :id) AND strftime('%m', donatie.afgerond_op) = strftime('%m', 'now');", id = session.get("organisatie")["id"])
        weekWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)), 0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id WHERE (status = 'Afgerond' AND organisatie.id = :id) AND strftime('%W', donatie.afgerond_op) = strftime('%W', 'now');", id = session.get("organisatie")["id"])
        jaarWaarde = db.execute("SELECT ifnull(SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)), 0) as waarde FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id WHERE (status = 'Afgerond' AND organisatie.id = :id) AND strftime('%Y', donatie.afgerond_op) = strftime('%Y', 'now');", id = session.get("organisatie")["id"])
        return render_template("/dashboard_organisatie.html", maandWaarde=maandWaarde, weekWaarde=weekWaarde, dagWaarde=dagWaarde, jaarWaarde=jaarWaarde)
    else:
        return render_template("/login.html")

@app.route("/dashboard/inBehandeling", methods=["GET", "POST"])
def inBehandeling():
    # De data voor de lopende transacties tabel uit de DB halen en deze opslaan voor een particulier
    if not session.get("particulier") is None:
        try:
            inBehandeling = db.execute("SELECT donatie.id,donatie.date_time,ophaalmoment_start,status,organisatie_naam,SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)) as 'waarde' FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE status = 'In Behandeling' AND particulier.id = :id GROUP BY donatie.id;", id = session.get("particulier")["id"])
            dataReturn = {}
            data = []
            for row in inBehandeling:
                donatie = {}
                donatie["Id"] = row["id"]
                donatie["Datum"] = row["date_time"]
                donatie["Ophaalmoment"] = row["ophaalmoment_start"]
                donatie["Status"] = row["status"]
                donatie["Organistatie"] = row["organisatie_naam"]
                donatie["Waarde"] = row["waarde"]
                data.append(donatie)
            dataReturn["data"] = data
            return jsonify(dataReturn)
        except:
            return apology("Er is iets fout gegaan.", 403)
        # De data voor de lopende transacties tabel uit de DB halen en deze opslaan voor een Organisatie
    elif not session.get("organisatie") is None:
        try:
            inBehandeling = db.execute("SELECT donatie.id,donatie.date_time,ophaalmoment_start,status,organisatie_naam,SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)) as 'waarde' FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE status = 'In Behandeling' AND organisatie.id = :id GROUP BY donatie.id;", id = session.get("organisatie")["id"])
            dataReturn = {}
            data = []
            for row in inBehandeling:
                donatie = {}
                donatie["Id"] = row["id"]
                donatie["Datum"] = row["date_time"]
                donatie["Ophaalmoment"] = row["ophaalmoment_start"]
                donatie["Status"] = row["status"]
                donatie["Organistatie"] = row["organisatie_naam"]
                donatie["Waarde"] = row["waarde"]
                data.append(donatie)
            dataReturn["data"] = data
            return jsonify(dataReturn)
        except:
            return apology("Er is iets fout gegaan.", 403)

@app.route("/dashboard_organisatie/afronden", methods=["GET", "POST"])
def afronden():
    # Dit stukje haalt de donatie Id van de geklikte donatie uit het JSON bestand, zodat de status van die donatie geüpdate kan worden. 
    jsonData = request.get_json()
    donatieId = jsonData["donatieId"]
    afgerond = db.execute("UPDATE donatie SET status = 'Afgerond', afgerond_op = DATETIME('now') WHERE donatie.id = :donatieId;", donatieId=donatieId)
    # Na het updaten wordt hij doorgestuurd naar bevestigd zodat het in de tweede tabel kan komen te staan
    return render_template("/dashboard/Bevestigd")

@app.route("/dashboard/Bevestigd", methods=["GET", "POST"])
def Bevestigd():
    # Doet hetzelfde als inBehandeling, maar haalt 2 andere kolommen op voor de particulier
    if not session.get("particulier") is None:
        try:
            Bevestigd = db.execute("SELECT donatie.date_time,ophaalmoment_end,afgerond_op,status,organisatie_naam,SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)) as 'waarde' FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE status = 'Afgerond' AND particulier.id = :id GROUP BY donatie.id;", id = session.get("particulier")["id"])
            dataReturn = {}
            data = []
            for row in Bevestigd:
                donatie = {}
                donatie["Datum"] = row["date_time"]
                donatie["Ophaalmoment"] = row["ophaalmoment_end"]
                donatie["Afgerond op"] = row["afgerond_op"]
                donatie["Status"] = row["status"]
                donatie["Organistatie"] = row["organisatie_naam"]
                donatie["Waarde"] = row["waarde"]
                data.append(donatie)
            dataReturn["data"] = data
            return jsonify(dataReturn)
        except:
            return apology("Er is iets fout gegaan.", 403)
        # Deze doet hetzelfde, alleen dan voor een organisatie
    elif not session.get("organisatie") is None:
        try:
            Bevestigd = db.execute("SELECT donatie.date_time,ophaalmoment_end,afgerond_op,status,organisatie_naam,SUM(ROUND(artikel.waarde * donatie_regels.aantal, 1)) as 'waarde' FROM 'donatie' join organisatie ON donatie.organisatie_id = organisatie.id join donatie_regels ON donatie.id = donatie_regels.donatie_id join artikel ON donatie_regels.artikel_id = artikel.id join particulier ON donatie.particulier_id = particulier.id WHERE status = 'Afgerond' AND organisatie.id = :id GROUP BY donatie.id;", id = session.get("organisatie")["id"])
            dataReturn = {}
            data = []
            for row in Bevestigd:
                donatie = {}
                donatie["Datum"] = row["date_time"]
                donatie["Ophaalmoment"] = row["ophaalmoment_end"]
                donatie["Afgerond op"] = row["afgerond_op"]
                donatie["Status"] = row["status"]
                donatie["Organistatie"] = row["organisatie_naam"]
                donatie["Waarde"] = row["waarde"]
                data.append(donatie)
            dataReturn["data"] = data
            return jsonify(dataReturn)
        except:
            return apology("Er is iets fout gegaan.", 403)

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/verstuurd")
def verstuurd():
    return render_template("verstuurd.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        naam = request.form.get("naam")
        telefoonnummer = request.form.get("telefoonnummer")
        email = request.form.get("email")
        onderwerp = request.form.get("onderwerp")
        omschrijving = request.form.get("omschrijving")

        msg = Message( onderwerp, sender = 'statiegelddoneren@gmail.com', recipients = ['statiegelddoneren@gmail.com'])
        msg.body = omschrijving + "\r\n " + "\r\nNaam: " + naam + "\r\nTelefoonnummer: " + telefoonnummer + "\r\nEmail: " + email
        mail.send(msg)
        return render_template("verstuurd.html")
    else:
        return render_template("contact.html")

# Statiegeld aanmelden pagina weergeven
@app.route("/statiegeld_aanmelden", methods=["GET", "POST"])
def statiegeld_aanmelden():
    session["active_page"] = "statiegeld_aanmelden"

    # Controleer login
    if session.get("particulier"):
        # Haal gegevens op uit db om te laten zien
        artikelen = db.execute("SELECT * FROM artikel")
        favorieten = db.execute("select * from favoriet join organisatie on favoriet.organisatie_id = organisatie.id where particulier_id = :id", id=session.get("particulier")["id"])

        # Kijk of er een parameter organisatie is
        if request.method == "GET" and request.args.get("organisatie") != None:
            favorietId = request.args.get("organisatie")
            favorietOrganisatie = db.execute("select * from organisatie where id =:id", id = favorietId)
            return render_template("statiegeld_aanmelden.html", artikelen=artikelen, favorieten=favorieten, favorietId=favorietId, favorietOrganisatie=favorietOrganisatie)
        else:
            return render_template("statiegeld_aanmelden.html", artikelen=artikelen, favorieten=favorieten)
    else:
        return render_template("/login_user.html")

# Statiegeld aanmelden AJAX-call om donatie vast te leggen
@app.route("/statiegeld_aanmelden/donatie", methods=["GET", "POST"])
def donatie():
    if session.get("particulier"):
        # Haal de gegevens uit de POST request op
        data = request.get_json()
        organisatieId = data["organisatieId"]
        particulier = session["particulier"]["id"]
        artikelen = data["artikelen"]

        # Maak een donatie aan en voeg daarna de regels toe
        try:
            donatie = db.execute("INSERT INTO donatie (particulier_id, organisatie_id) VALUES (:particulier_id, :organisatie_id)", particulier_id=particulier, organisatie_id=organisatieId)
            i = 0
            for artikel in artikelen:
                db.execute("INSERT INTO donatie_regels (donatie_id, artikel_id, aantal) VALUES (:donatie_id, :artikel_id, :aantal)", donatie_id=donatie, artikel_id=artikel["id"], aantal=artikel["value"])
                i+=1
        except:
            return apology("Er is iets fout gegaan.", 403)

        return jsonify(donatie)
    else:
        return render_template("/login_user.html")

# Donaties pagina weergeven
@app.route("/donaties")
def donaties():
    session["active_page"] = "donaties"

    # Controleer login
    if session.get("organisatie"):
        # Geef de dag van vandaag + 2 dagen mee om afspraak te plannen
        return render_template("donaties.html", date=date.today() + datetime.timedelta(days=2))
    else:
        return render_template("/login_association.html")

# Donaties AJAX-call voor DataTable
@app.route("/donaties/alleDonaties", methods=["GET", "POST"])
def alleDonaties():
    # Controleer login
    if session.get("organisatie"):
        # Haal alle donaties op uit de db
        try:
            # Donaties samengevoegd per donatie.id, alle waardes van de donatie.regels bij elkaar geteld,
            # IFNULL voor als er nog geen datum is
            alleDonaties = db.execute("SELECT donatie.id, particulier.adres, SUM(artikel.waarde * donatie_regels.aantal) as 'waarde', STRFTIME('%d-%m-%Y %H:%M:%S', datetime(donatie.date_time, '+1 hour')) as 'datum', donatie.status, IFNULL((STRFTIME('%d-%m-%Y %H:%M:%S', donatie.ophaalmoment_start) || ' - ' || substr(donatie.ophaalmoment_end,-6,6)), 'Niet gepland') as 'ophaalmoment', IFNULL(STRFTIME('%d-%m-%Y %H:%M:%S', donatie.afgerond_op), 'Niet afgerond') as 'afgerond', particulier.id as 'particulierId' FROM organisatie join donatie on organisatie.id = donatie.organisatie_id join donatie_regels on donatie.id = donatie_regels.donatie_id join artikel on donatie_regels.artikel_id = artikel.id join particulier on donatie.particulier_id = particulier.id where organisatie.id = :id group by donatie.id", id=session.get("organisatie")["id"])

            # Gegevens uitlezen en een json object maken voor return
            dataReturn = {}
            data = []
            for row in alleDonaties:
                donatie = {}
                donatie["adres"] = row["adres"]
                donatie["datum"] = row["datum"]
                donatie["id"] = row["id"]
                donatie["status"] = row["status"]
                donatie["waarde"] = row["waarde"]
                donatie["punten"] = round(row["waarde"] * 100)
                donatie["ophaalmoment"] = row["ophaalmoment"]
                donatie["afgerond"] = row["afgerond"]
                donatie["particulierId"] = row["particulierId"]
                data.append(donatie)
            dataReturn["data"] = data
            return jsonify(dataReturn)
        except:
            return "Er is iets mis gegaan."
    else:
        return render_template("/login_association.html")

# Donaties AJAX-call voor tabel donatieregels inzien
@app.route("/donaties/donatieRegels", methods=["GET", "POST"])
def donatieRegels():
    # Controleer login
    if session.get("organisatie"):
        # Haal de gegevens uit de POST request op
        jsondata = request.get_json()
        donatieId = jsondata["donatieId"]

        # Selecteer donatie_regels van een bepaalde donatie.id
        try:
            alleDonaties = db.execute("SELECT artikel.naam, artikel.omschrijving, donatie_regels.aantal, PRINTF('%.2f', artikel.waarde) as 'waarde' FROM 'donatie' join donatie_regels on donatie.id = donatie_regels.donatie_id join artikel on donatie_regels.artikel_id = artikel.id where donatie.id = :id", id=donatieId)

            # Gegevens uitlezen en een json object maken voor return
            dataReturn = {}
            data = []
            for row in alleDonaties:
                donatie = {}
                donatie["Naam"] = row["naam"]
                donatie["Omschrijving"] = row["omschrijving"]
                donatie["Aantal"] = row["aantal"]
                donatie["Waarde"] = row["waarde"]
                donatie["Punten"] = round(float(row["waarde"]) * 100)
                data.append(donatie)
            dataReturn["data"] = data
            return jsonify(dataReturn)
        except:
            return "Er is iets mis gegaan."
    else:
        return render_template("/login_association.html")

# Donaties AJAX-call voor plan ophaalmoment
@app.route("/donaties/planOphaal", methods=["GET", "POST"])
def planOphaal():
    # Controleer login
    if session.get("organisatie"):
        # Haal de gegevens uit de POST request op
        jsondata = request.get_json()
        startTime = jsondata["startTime"]
        endTime = jsondata["endTime"]
        donatieIds = jsondata["donatieId"]

        # Update de donaties
        try:
            for id in donatieIds:
                ophaalmoment = db.execute("UPDATE donatie SET status = 'In Behandeling', 'ophaalmoment_start'=:startTime, 'ophaalmoment_end'=:endTime WHERE id = :id;", startTime=startTime, endTime=endTime, id=id)
            return jsonify("Gelukt")
        except:
            return "Er is iets mis gegaan."
    else:
        return render_template("/login_association.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    session["active_page"] = "settings"
    if not session.get("particulier") is None:
        if request.method == "POST":
            adres = request.form.get("adres")
            postcode = request.form.get("postcode")
            woonplaats = request.form.get("woonplaats")
            telefoonnummer = request.form.get("telefoonnummer")
            profielfoto_url = request.form.get("profielfoto_url")
            wachtwoord = request.form.get("wachtwoord")
            herhaling = request.form.get("wachtwoord_herhaal")
            if wachtwoord != herhaling:
                return apology("Wachtwoorden komen niet overeen!", 403)

            # Hash the password
            hash = generate_password_hash(wachtwoord)

            # Attempt to create a new user
            # try:
            particulier = db.execute("UPDATE particulier SET adres=:adres, postcode=:postcode, woonplaats=:woonplaats, telefoonnummer=:telefoonnummer, profielfoto_url=:profielfoto_url, wachtwoord=:wachtwoord WHERE id = :id", adres=adres, postcode=postcode, woonplaats=woonplaats, telefoonnummer=telefoonnummer, profielfoto_url=profielfoto_url, wachtwoord=hash, id=session.get("particulier")["id"])
            session["particulier"] = db.execute("SELECT * FROM particulier WHERE id = :id", id=session.get("particulier")["id"])[0]
            # except:
                # return apology("Er is iets fout gegaan!", 403)
            return render_template("settings.html")
        else:
            return render_template("settings.html")
    else:
        return render_template("/login.html")

# Route verkenner
@app.route("/verkenner", methods=["GET"])
def verkenner():
    session["active_page"] = "verkenner"
    # Check voor session
    if not session.get("particulier") is None or not session.get("organisatie") is None:
        placeholder = request.args.get("q")
        # Verkenner wanneer er nog niks is opgezocht via de zoekbalk
        if placeholder is None:
            return render_template("verkenner.html")
        # Verkenner wanneer er wel iets is opgezocht via de zoekbalk
        else:
           # Query voor naam organisatie
            organisaties = db.execute("SELECT * FROM organisatie WHERE organisatie_naam LIKE ?", "%" + placeholder + "%")
            # Query voor plaats organisatie
            plaats = db.execute("SELECT * FROM organisatie WHERE vestigingsplaats LIKE ?", "%" + placeholder + "%")
            # Lijsten samenvoegen zonder duplicates
            for x in plaats:
                if x not in organisaties:
                    organisaties.append(x)

            return render_template("verkenner.html", organisaties=organisaties, gezocht=placeholder)
    else:
        return render_template("/login.html")

# Registratie van de gebruiker
@app.route("/register_user", methods=["GET", "POST"])
def register_user():
    # Verstuurd de volgende data naar de database
    if request.method == "POST":
        voornaam = request.form.get("voornaam")
        achternaam = request.form.get("achternaam")
        email = request.form.get("email")
        adres = request.form.get("adres")
        postcode = request.form.get("postcode")
        telefoonnummer = request.form.get("telefoonnummer")
        gebruikersnaam = request.form.get("gebruikersnaam")
        geslacht = request.form.get("geslacht")
        geboortedatum = request.form.get("geboortedatum")
        woonplaats = request.form.get("woonplaats")
        password = request.form.get("password")
        confirmation = request.form.get("password-repeat")
        # Herhaal wachtwoord moet identiek zijn met wachtwoord
        if password != confirmation:
            return apology("Wachtwoorden komen niet overeen!", 403)

        # Hash het wachtwoord
        hash = generate_password_hash(password)

        # Bevestigingsmail sturen na registreren.
        msg = Message('Statiegelddoneren.nl', sender = 'statiegelddoneren@gmail.com', recipients = [email])
        msg.body = "Welkom, dankuwel voor het registreren bij Statiegelddoneren.nl. Uw registratie is compleet!"
        mail.send(msg)

        # Nieuwe gebruiker wordt toegevoegd
        try:
            particulier = db.execute("INSERT INTO particulier (voornaam, achternaam, email, adres, postcode, woonplaats, telefoonnummer, gebruikersnaam, wachtwoord, geslacht, geboorte_datum) VALUES (:voornaam, :achternaam, :email, :adres, :postcode, :woonplaats, :telefoonnummer, :gebruikersnaam, :wachtwoord, :geslacht, :geboorte_datum)", voornaam=voornaam, achternaam=achternaam, email=email, adres=adres,  postcode=postcode, woonplaats=woonplaats, telefoonnummer=telefoonnummer, gebruikersnaam=gebruikersnaam, wachtwoord=hash, geboorte_datum=geboortedatum, geslacht=geslacht)
        except:
            return apology("Gebruikersnaam bestaat al!", 403)

        # Onthoudt dat gebruiker is aangemeld
        session["particulier"] = particulier

        # Verstuur gebruiker naar de loginpagina van gebruikers
        return redirect("/login_user")
    else:
        return render_template("register_user.html")

# Registratie organisatie
@app.route("/register_association", methods=["GET", "POST"])
def register_association():
    # Verstuurd de volgende data naar de database
    if request.method == "POST":
        organisatie_naam = request.form.get("organisatie_naam")
        kvk_nummer = request.form.get("kvk_nummer")
        email = request.form.get("email")
        adres = request.form.get("adres")
        postcode = request.form.get("postcode")
        telefoonnummer = request.form.get("telefoonnummer")
        website_url = request.form.get("website_url")
        vestigingsplaats = request.form.get("vestigingsplaats")
        plaats = request.form.get("plaats")
        omschrijving = request.form.get("omschrijving")
        password = request.form.get("password")
        confirmation = request.form.get("password-repeat")
        # Herhaal wachtwoord moet identiek zijn met wachtwoord
        if password != confirmation:
            return apology("Wachtwoorden komen niet overeen!", 403)

        # Hash het wachtwoord
        hash = generate_password_hash(password)

        # Bevestigingsmail wordt verstuurd na registreren
        msg = Message('Statiegelddoneren.nl', sender = 'statiegelddoneren@gmail.com', recipients = [email])
        msg.body = "Beste organisatie, uw registratie is compleet! U kunt nu inloggen op statiegelddoneren.nl en uw avonturen beginnen met het statiegeld ophalen voor uw organisatie. Heel veel succes!"
        mail.send(msg)

        # Nieuwe organisatie toegevoegd
        try:
            organisatie = db.execute("INSERT INTO organisatie (organisatie_naam, kvk_nummer, email, adres, postcode, telefoonnummer, website_url, vestigingsplaats, omschrijving, wachtwoord) VALUES (:organisatie_naam, :kvk_nummer, :email, :adres, :postcode, :telefoonnummer, :website_url, :vestigingsplaats, :omschrijving, :wachtwoord)", organisatie_naam=organisatie_naam, kvk_nummer=kvk_nummer, email=email, adres=adres, postcode=postcode, telefoonnummer=telefoonnummer, website_url=website_url, vestigingsplaats=vestigingsplaats, omschrijving=omschrijving, wachtwoord=hash)
        except:
            return apology("Organisatie bestaat al!", 403)

        # Onthoudt dat organisatie is aangemeld
        session["organisatie"] = organisatie

        # Verstuur organisatie naar loginpagina van organisaties
        return redirect("/login_association")
    else:
        return render_template("register_association.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    """ Log user in """

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("gebruikersnaam"):
            return apology("Vul een gebruikersnaam in!", 403)

        # Ensure password was submitted
        elif not request.form.get("wachtwoord"):
            return apology("Vul een wachtwoord in!", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM particulier WHERE gebruikersnaam = ?", request.form.get("gebruikersnaam"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["wachtwoord"], (request.form.get("wachtwoord"))):
            return apology("Ongeldig gebruikersnaam en/of wachtwoord!", 403)

        # Remember which user has logged in
        session["particulier"] = rows[0]

        # Redirect user to home page
        return redirect("/dashboard_organisatie")

    else:
        return render_template("login_user.html")

@app.route("/login_association", methods=["GET", "POST"])
def login_association():
    """ Log association in """

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("Vul een emailadres in!", 403)

        # Ensure password was submitted
        elif not request.form.get("wachtwoord"):
            return apology("Vul een wachtwoord in!", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM organisatie WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["wachtwoord"], (request.form.get("wachtwoord"))):
            return apology("Ongeldig gebruikersnaam en/of wachtwoord!", 403)

        # Remember which user has logged in
        session["organisatie"] = rows[0]

        # Redirect user to home page
        return redirect("/dashboard_organisatie")

    else:
        return render_template("login_association.html")

@app.route("/profile", methods=["GET"])
def profile():
    """ Laat profiel zien"""

    if not session.get("particulier") or session.get("organisatie") is None:
        # Pak type van account
        type = request.args.get("type")
        if type is None:
            return render_template("profile.html")
        else:
            # Als type particulier is, pak account gegevens
            if type == "particulier":
                profileGegevens = db.execute("SELECT * FROM particulier WHERE id = ?", request.args.get("id"))
            # Als organisatie is is, pak account gegevens
            elif type == "organisatie":
                profileGegevens = db.execute("SELECT * FROM organisatie WHERE id = ?", request.args.get("id"))
        return render_template("profile.html", profile=profileGegevens)
    # Anders redirect naar login
    else:
        return redirect("/login")

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """ Create a new post """

    if request.method == "POST":
        # Ensure an image was included
        if not request.files["image"]:
            return apology("must provide an image", 403)

        # Collect user input
        file = request.files["image"]
        filename = file.filename
        text = request.form.get("text")

        # Create new post in database
        # The image is stored in the database through saving its name
        post = db.execute("INSERT INTO posts (image_name, text, user_id) VALUES (:image, :text, :user_id)", image=filename, text=text, user_id=session["user_id"])

        # Save image file in images folder
        request.files["image"].save(f"static/images/{filename}")

        return redirect("/")
    else:
        return render_template("create.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register new user """

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")

        # Ensure password matches confirmation
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return apology("passwords don\'t match", 403)

        # Hash the password
        hash = generate_password_hash(password)

        # Attempt to create a new user
        try:
            user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)
        except:
            return apology("username is already taken.", 403)

        # Remember user that is now logged in
        session["user_id"] = user

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")
