==========  JSON-BIBLIOTHEK - README (v2.1)  ==========

BESCHREIBUNG:
Diese Bibliothek ermöglicht eine einfache Verwaltung von 
Konfigurationsdateien in Python. JSON-Daten werden direkt 
in globale Variablen geladen und bei Änderungen automatisch
gesichert.

------------------------------------------------------------
HAUPTFEATURES
------------------------------------------------------------
* Auto-Load:    JSON-Keys werden zu Python-Variablen.
* Self-Healing: Automatische Reparatur durch .bak-Dateien.
* Editor:       Werte interaktiv im Terminal ändern.
* Sicherheit:   Automatisches Backup vor jedem Schreibvorgang.
* Datentypen:   Unterstützt int, float, str, bool und None.

------------------------------------------------------------
INSTALLATION & START
------------------------------------------------------------
1. Datei 'JsonBib.py' in dein Projektverzeichnis kopieren.
2. Importieren:  import JsonBib as j
3. Setup:        j.bibconfig(autoCreate=True, Print=False)
4. Laden:        j.load()

------------------------------------------------------------
WICHTIGSTE FUNKTIONEN
------------------------------------------------------------

[X] = Gibt True/False für den Erfolgsstatus zurück.

1. j.get(Name, Ersatzwert)
     - Sicherer Zugriff. Gibt den Ersatzwert zurück, falls der
     - Name in der Config fehlt.

2. j.edit(Variable, Wert) [X]
     - Ändert einen bestehenden Wert im Speicher und der Datei.

3. j.editor()
     - Öffnet das interaktive Menü. 
     - Befehle im Editor: '/?' (Liste zeigen), 'exit' (Beenden).

4. j.add(Name, Wert) [X]
     - Erstellt einen komplett neuen Datenpunkt.

5. addlist(dict) [X]
   - Fügt mehrere NEUE Datenpunkte gleichzeitig hinzu.
   - Beispiel: j.addlist({"D1": 10, "D2": 20})

6. search(Varname) [X]
   - Prüft, ob eine Variable in der Config existiert (True/False).

7. delete(name) [X]
   - Löscht einen Datenpunkt dauerhaft aus der Datei und dem Speicher.

8. backup() [X]
    - Erstellt ein Backup der Config Datei (Config.json.bak)

9. j.show(Print=True)
   - Gibt eine Liste aller geladenen Variablen zurück.

10. j.info()
   - Zeigt die ausführliche Hilfe direkt im Terminal an.

------------------------------------------------------------
DATENSICHERHEIT (.bak)
------------------------------------------------------------
Die Bibliothek erstellt automatisch eine 'config.json.bak'.
Sollte die Hauptdatei beschädigt werden (z.B. durch Fehler
beim Speichern), stellt die load()-Funktion den letzten
funktionsfähigen Stand automatisch wieder her.

------------------------------------------------------------
STEUERUNG
------------------------------------------------------------
- Abbrechen: Strg+C (im Editor)
- Null-Werte: In Python 'None', im Editor als 'None' tippen.
- Booleans: 'True' oder 'False' eingeben.
