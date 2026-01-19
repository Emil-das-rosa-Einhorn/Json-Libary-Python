import json
import os
import shutil

pfad = os.path.join(os.path.dirname(__file__), 'config.json')

config_autoCreate = False
config_Print = False

ignore = ["load", "dump", "show", "json", "os", "editor", "edit", "info", 
          "pfad", "Print", "ignore", "search", "add", "addlist", "delete",
          "backup", "get", "libconfig","config_autoCreate", "config_Print"]

def libconfig (autoCreate=None,Print=None):

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
    
    header = """
    ============================================================
    JSON LIBRARY - DOCUMENTATION (v2.1)
    ============================================================

    """
    
    config_info = f"Config Path: {pfad}"

    functions = """

    AVAILABLE FUNCTIONS:
    [Functions marked with [X] return 'True' if executed 
    successfully and 'False' upon failure]

    1. load(autoCreate=True/None) [X]
       Loads JSON data into global memory.
       - autoCreate=True: Creates a base config if none exists 
         or restors it form the Backup.
         If the argument is omitted, no config file is created.
       - Should the config file be corrupted, the function 
         attempts to restore the file from the backup.

    2. show(Print=True/None)
       Returns all loaded variable names as a list.
       If set to 'True', output is displayed in the terminal.

    3. editor()
       Interactive terminal menu for changing values.
       - '/?' shows all keys | 'exit' terminates the mode.

    4. edit(Var, Val) [X]
       Changes an EXISTING value directly via code. 

    5. dump(dict) [X]
       Updates EXISTING values in the JSON. 
       Prevents accidental creation of new keys.

    6. add(Varname, Varvalue) [X]
       Creates a NEW data point in the JSON file.

    7. addlist(dict) [X]
       Adds multiple NEW data points simultaneously.
       Example: j.addlist({"D1": 10, "D2": 20})

    8. search(Varname) [X]
       Checks if a variable exists in the config (True/False).

    9. delete(name) [X]
       Permanently deletes a data point from the file and memory.

    10. backup() [X]
        Creates a backup/current state of the config file (Config.json.bak)

    11. get(Var, DefaultValue)
        Secure data access.
        - I = jsonBib.get("Name", DefaultValue)
        - The DefaultValue (optional) is used if "Name" is not in the config file.

    CONTROLS & SECURITY:
    - The delete function permanently removes data from the config file.
    - Use 'Ctrl+C' or 'exit' to safely cancel the editor.
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
                
                print("[INFO] Config has been restored from backup!")
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
            print("[WARNING] Config file corrupted! Attempting to load backup...")
            
            backup_pfad = pfad + ".bak"
            
            if os.path.exists(backup_pfad):
                os.remove(pfad)
                os.rename(backup_pfad, pfad)
                
                with open(pfad, 'r', encoding='utf-8') as f:
                    _daten = json.load(f)
                globals().update(_daten)
                
                print("[INFO] Config has been restored from backup!")
                backup()
                return True
            else:
                print("[ERROR] No backup available. Recovery failed.")
                return False
        else:
            print ("[ERROR] Configuration restore from backup is disabled.")
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
        print("[ERROR] File not found. No updates possible.")
        return False

    filtered_data = {}
    rejected_keys = []

    for key, wert in neue_daten.items():
        if key in daten:
            filtered_data[key] = wert
        else:
            rejected_keys.append(key)

    if filtered_data:
        daten.update(filtered_data)
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)
        print(f"Update successful: {list(filtered_data.keys())} updated.")
    
    if rejected_keys:
        print(f"[INFO] New data points ignored: {rejected_keys} (Do not exist in config).")
        return False
    backup()
    return True

def editor():
    while True:
        load(autoCreate=False)
        try:

            try:
                dataPoint = (input("Please enter the name of the variable you would like to change:"))
                if dataPoint == "/?":
                    show(True)
                    continue
                elif dataPoint == "exit":
                    print ("[INFO] Editor session ended.")
                    break

                else:
                    dataVar = globals()[dataPoint]
                    print (f"{dataPoint} is currently set to: {dataVar}")
                    newValin = (input("Please enter the new value: "))

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
                print(f"""[ERROR] The data point '{dataPoint}' does not exist in the config file. 
 Type /? to see a list of all variables.""")

            except Exception as e:
                #print (e)
                print ("[ERROR] Invalid input")

            else:
                daten = {dataPoint: newVal}
                dump (daten)
        except KeyboardInterrupt:
            print ("[INFO] Editor session ended.")
            break

def edit(Var, Val):
        
    load(autoCreate=False)
    try:

        try:
            dataPoint = Var

            if dataPoint == "/?":
                show(True)
                return True
            else:
                dataVar = globals()[dataPoint]
                print (f"D{dataPoint} is currently set to: {dataVar}")
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
            print(f"[ERROR] The data point '{dataPoint}' does not exist in the config file.")
            return False

        except Exception as e:
            print (e)
            print ("[ERROR] Invalid input")
            return False

        else:
            daten = {dataPoint: newVal}
            dump (daten)
    except KeyboardInterrupt:
        print ("[INFO] Editor session ended.")
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
    
    print(f"Update successful: {list(newVardata.keys())} updated.")
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
    
    print(f"Update successful: {list(newVarlist.keys())} updated.")
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
                
            print(f"[INFO] '{name}' deleted successfully.")
            backup ()
            return True
        else:
            print(f"[ERROR] '{name}' does not exist and cannot be deleted.")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to delete: {e}")
        return False
    
def get(name, default=None):
    return globals().get(name, default)
