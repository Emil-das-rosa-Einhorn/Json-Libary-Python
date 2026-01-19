import json
import os
import shutil

pfad = os.path.join(os.path.dirname(__file__), 'config.json')

config_autoCreate = False
config_Print = False

# Stelle sicher, dass deine ignore-Liste am Anfang der Datei so aussieht:
ignore = ["load", "dump", "show", "json", "os", "editor", "edit", "info", 
          "pfad", "Print", "ignore", "search", "add", "addlist", "delete",
          "backup", "get", "bibconfig","config_autoCreate", "config_Print"]

def bibconfig (autoCreate=None,Print=None):

    global config_autoCreate, config_Print

    if autoCreate is not None:
        config_autoCreate = autoCreate
    else:
        config_autoCreate = False

    if Print is not None:
        config_Print = Print
    else:
        config_Print = False

def info():
    """Gibt eine detaillierte Übersicht über alle Bibliotheks-Funktionen aus."""
    
    header = """
    ============================================================
    JSON-BIBLIOTHEK - DOKUMENTATION (v2.0)
    ============================================================

    """
    
    config_info = f"Pfad zur Config: {pfad}"

    functions = """

    VERFÜGBARE FUNKTIONEN:
    [Funktionen mit einem [X] geben 'True' zurück wenn diese Erfolgreich 
    ausgefürt werden und 'False' beim scheitern]

    1. load(autoCreate=True/None) [X]
       Lädt die JSON-Daten in den globalen Speicher.
       - autoCreate=True: Erstellt eine Basis-Config, falls keine existiert.
         Beim Weglassen des Arguments wird keine Config Datei erstellt.
       - sollte die Config Datei beschädigt sein, 
         versucht die Funktion die Datei aus dem Backup wieder herzustellen.

    2. show(Print=True/None)
       Gibt alle geladenen Variablen-Namen als Liste zurück.
       Bei 'True' erfolgt eine Ausgabe im Terminal.

    3. editor()
       Interaktives Terminal-Menü zum Ändern von Werten.
       - '/?' zeigt alle Keys | 'exit' beendet den Modus.

    4. edit(Var, Val) [X]
       Ändert einen BESTEHENDEN Wert direkt per Code. 
       Gibt True/False bei Erfolg zurück.

    5. dump(dict) [X]
       Aktualisiert BESTEHENDE Werte in der JSON. 
       Verhindert das versehentliche Anlegen neuer Keys.

    6. add(Varname, Varvalue) [X]
       Erstellt einen NEUEN Datenpunkt in der JSON-Datei.

    7. addlist(dict) [X]
       Fügt mehrere NEUE Datenpunkte gleichzeitig hinzu.
       Beispiel: j.addlist({"D1": 10, "D2": 20})

    8. search(Varname) [X]
       Prüft, ob eine Variable in der Config existiert (True/False).

    9. delete(name) [X]
       Löscht einen Datenpunkt dauerhaft aus der Datei und dem Speicher.

    10. backup() [X]
        Erstellt ein Backup der Config Datei (Config.json.bak)

    11. get(Var,Ersatzwert)
        Sicherer Zugriff auf die Daten
        - I = jsonBib.get("Name",Ersatzwert)
        - Der Ersatzwert wird genutzt wenn "Name" nicht in der Config Datei ist.

    STEUERUNG & SICHERHEIT:
    - Die Delete funktion löscht Daten permanent aus der Config Datei.
    - Nutze 'Strg+C ' oder 'exit' zum sicheren Abbrechen des Editors.
    ============================================================
    """
    print(header)
    print(config_info)
    print(functions)

def backup():
    if os.path.exists(pfad):
        shutil.copy(pfad, pfad + ".bak")
        return True
    return False

def load(autoCreate=None):
    if not os.path.exists(pfad):
        if autoCreate or config_autoCreate:
            backup_pfad = pfad + ".bak"
            if os.path.exists(backup_pfad):
                os.rename(backup_pfad, pfad)
                
                with open(pfad, 'r', encoding='utf-8') as f:
                    _daten = json.load(f)
                globals().update(_daten)
                
                print("[ERFOLG1] Config wurde aus Backup wiederhergestellt!")
                backup()
                return True
            else:
                standard_daten = {"Version": 1.0}
                with open(pfad, 'w', encoding='utf-8') as f:
                    json.dump(standard_daten, f, indent=4)
                globals().update(standard_daten)
                backup()
                return True
        return False

    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            _daten = json.load(f)
        globals().update(_daten)
        backup()
        return True

    except (json.JSONDecodeError, ValueError):
        if autoCreate or config_autoCreate:
            print("[WARNUNG] Config-Datei beschädigt! Versuche Backup zu laden...")
            
            backup_pfad = pfad + ".bak"
            
            if os.path.exists(backup_pfad):
                os.remove(pfad)
                os.rename(backup_pfad, pfad)
                
                with open(pfad, 'r', encoding='utf-8') as f:
                    _daten = json.load(f)
                globals().update(_daten)
                
                print("[ERFOLG2] Config wurde aus Backup wiederhergestellt!")
                backup()
                return True
            else:
                print("[FEHLER] Kein Backup vorhanden. Wiederherstellung fehlgeschlagen.")
                return False
        else:
            print ("[FEHLER] Kein erstellen der Config Datei aus dem Backup erwünscht")
            return False

def show (Print=None):
    load(autoCreate=False)
    variablen = [name for name in globals() if not name.startswith("__") and name not in ignore]
    if Print or config_Print:
        print (variablen)
    else:
        pass
    return variablen

def dump(neue_daten):
    backup()
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
    except FileNotFoundError:
        print("[ERROR] Datei nicht gefunden. Keine Updates möglich.")
        return False

    gefilterte_daten = {}
    abgelehnte_keys = []

    for key, wert in neue_daten.items():
        if key in daten:
            gefilterte_daten[key] = wert
        else:
            abgelehnte_keys.append(key)

    if gefilterte_daten:
        daten.update(gefilterte_daten)
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)
        print(f"Update erfolgreich: {list(gefilterte_daten.keys())} aktualisiert.")
    
    if abgelehnte_keys:
        print(f"[HINWEIS] Neue Datenpunkte ignoriert: {abgelehnte_keys} (Existieren nicht in der Config).")
        return False
    backup()
    return True

def editor():
    while True:
        load(autoCreate=False)
        try:

            try:
                dataPoint = (input("Bitte gib den Namen der Variablen ein die du ändern möchtest: "))
                if dataPoint == "/?":
                    show(True)
                    continue
                elif dataPoint == "exit":
                    print ("Editor wird Beendet")
                    break

                else:
                    dataVar = globals()[dataPoint]
                    print (f"Der Aktuelle wert für {dataPoint} ist: {dataVar}")
                    newValin = (input("Bitte gib den neuen Wert ein: "))

                if newValin == "False":
                    newValin = False
                    daten = {dataPoint: newValin}
                    dump (daten)
                    continue
                elif newValin == "True":
                    newValin = True
                    daten = {dataPoint: newValin}
                    dump (daten)
                    continue
                elif newValin == "None":
                    newValin = None
                    daten = {dataPoint: newValin}
                    dump (daten)
                    continue
                else:

                    try:
                        newVal = int(newValin)
                        print ("detected int")
                    
                    except ValueError:
                        try:
                            newVal = float(newValin)
                            print ("detected Var")
                        
                        except ValueError:
                            newVal = newValin
                            print ("detected String")
                
            except KeyError:
                print(f"""[ERROR] Der Datenpunkt '{dataPoint}' existiert nicht in der Cofig Datei.
gib /? ein um alle variablen angezeigt zu bekommen.""")

            except Exception as e:
                #print (e)
                print ("[ERROR] Fehlerhafte Eingabe")

            else:
                daten = {dataPoint: newVal}
                dump (daten)
        except KeyboardInterrupt:
            print ("Editor wird Beendet")
            break

def edit(Var, Val):
        
    load(autoCreate=False)
    try:

        try:
            dataPoint = Var

            if dataPoint == "/?":
                show(True)
                return True
            elif dataPoint == "exit":
                print ("Editor wird Beendet")
                return False

            else:
                dataVar = globals()[dataPoint]
                print (f"Der Aktuelle wert für {dataPoint} ist {dataVar}")
                newValin = Val
            

            if isinstance(newValin, bool):
                print(f"detected bool ({newValin})")
                if newValin == False:
                    newVal = False
                elif newValin == True:
                    newVal = True
            elif newValin == None:
                newVal = None

            else:
    
                try:
                    newVal = int(newValin)
                    print ("detected int")
                
                except ValueError:
                    try:
                        newVal = float(newValin)
                        print ("detected Var")
                    
                    except ValueError:
                        newVal = newValin
                        print ("detected String")
            
        except KeyError:
            print(f"[ERROR] Der Datenpunkt '{dataPoint}' existiert nicht in der Cofig Datei.")
            return False

        except Exception as e:
            print (e)
            print ("[ERROR] Fehlerhafte Eingabe")
            return False

        else:
            daten = {dataPoint: newVal}
            dump (daten)
    except KeyboardInterrupt:
        print ("Editor wird Beendet")
        return False
    
    return True

def search (Varsearch):

    Varonlist = False

    Varlist = show(Print=False)

    for GlobVar in Varlist:
        if GlobVar == Varsearch:
            Varonlist = True
        else:
            pass

    if Varonlist:
        return True
    else:
        return False
    
def add(Varname,Varvalue):
    newVardata = {Varname: Varvalue}
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
    except FileNotFoundError:
        daten = {}
        return False

    daten.update(newVardata)

    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
    
    print(f"Update erfolgreich: {list(newVardata.keys())} aktualisiert.")
    backup()
    return True

def addlist(newVarlist):
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
    except FileNotFoundError:
        daten = {}
        return False

    daten.update(newVarlist)

    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
    
    print(f"Update erfolgreich: {list(newVarlist.keys())} aktualisiert.")
    return True

def delete(name):
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
        
        if name in daten:
            del daten[name]
            
            with open(pfad, 'w', encoding='utf-8') as f:
                json.dump(daten, f, indent=4, ensure_ascii=False)
            
            if name in globals():
                del globals()[name]
                
            print(f"Datenpunkt '{name}' wurde erfolgreich gelöscht.")
            backup ()
            return True
        else:
            print(f"[ERROR] '{name}' existiert nicht und kann nicht gelöscht werden.")
            return False
            
    except Exception as e:
        print(f"Fehler beim Löschen: {e}")
        return False
    
def get(name, default=None):
    return globals().get(name, default)
