from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supergeheimespasswort'

benutzer = {
    "georg": "passwort1",
    "anna": "passwort2",
    "max": "passwort3"
}

buchungen = []
parkplaetze = ["A", "B", "E", "D", "F", "C"]

def ist_frei(platz, neue_ankunft, neue_abfahrt):
    for eintrag in buchungen:
        if eintrag['platz'] == platz:
            if not (neue_abfahrt <= eintrag['ankunft'] or neue_ankunft >= eintrag['abfahrt']):
                return False
    return True

@app.route("/", methods=["GET", "POST"])
def index():
    if "nutzer" not in session:
        return redirect(url_for("login"))

    nutzer = session["nutzer"]
    if request.method == "POST":
        ankunft = datetime.fromisoformat(request.form['ankunft'])
        abfahrt = datetime.fromisoformat(request.form['abfahrt'])

        platz = None
        for p in parkplaetze:
            if ist_frei(p, ankunft, abfahrt):
                platz = p
                break

        if platz:
            buchungen.append({
                "name": nutzer,
                "ankunft": ankunft,
                "abfahrt": abfahrt,
                "platz": platz
            })

        return redirect("/")

    return render_template("index.html", buchungen=buchungen, nutzer=nutzer)

@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = ""
    if request.method == "POST":
        nutzer = request.form['nutzer']
        pw = request.form['passwort']
        if nutzer in benutzer and benutzer[nutzer] == pw:
            session['nutzer'] = nutzer
            return redirect(url_for("index"))
        else:
            fehler = "Ungültige Anmeldedaten."

    return render_template("login.html", fehler=fehler)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)