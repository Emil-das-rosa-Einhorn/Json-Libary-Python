import json
import os
import shutil
import tempfile
import portalocker
import datetime

file_Name = 'files/config.json'

pfad = os.path.join(os.path.dirname(__file__), file_Name)
backup_pfad = pfad + ".bak"
reset_pfad = pfad + ".reset"

config_autoCreate = False
config_Print = False
config_set_reset = False
config_autoLoad = False
config_check = False
passed = True
MsgtoCons_global = 0
locked = "unlocked" #unlocked, soft_lock, hard_lock
refresh = False
mode = "normal" #normal, safe_mode
ConfVersion = 1.0

konflikte = []

ignore = {
    '__annotations__', '__builtins__', '__cached__', '__doc__', 
    '__file__', '__loader__', '__name__', '__package__', '__spec__',
    '_lock', '_target', '__dict__', '__class__', '__init__', '__getattr__', 
    '__setattr__', '__delattr__', '__members__', '__module__'
}

donotEdit = {'_header','ConfVersion', 'mode', 'refresh', 'locked', 'check', 'autoLoad', 'autoCreate', 'Print', 'set_reset', 'MsgtoCons'}

class ConfigContainer:
    """A container for all configuration values."""
    def __getattr__(self, name):
        return None

cfg = ConfigContainer()

def _read(filename=None):
    """Reads the config file and returns the raw content."""
    if filename is not None:
        fileName(filename)
    if health_check():
        try:
            with open(pfad, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            if MsgtoCons_global <= 2: print(f"[ERROR] Failed to read file: {e}")
            return None
    else:
        if MsgtoCons_global <= 2: print ("[ERROR] File could not be Opened")
        return None

def _write(daten, filename=None):

    if filename is not None:
        fileName(filename)

    if locked == 'hard_lock':
        if MsgtoCons_global <= 1: print("[WARRNING] File is currently locked.")
        return False
    
    ordner = os.path.dirname(pfad)
    if not os.path.exists(ordner) and ordner != '':
        if MsgtoCons_global <= 2: print ("[ERROR] Directory does not exist. Please create the directory or specify a valid path.")
        return False

    fd, temp_pfad = tempfile.mkstemp(dir=ordner, prefix="temp_cfg_", suffix=".json")

    if "_header" in daten:
        daten["_header"]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            json.dump(daten, f, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
            portalocker.unlock(f)
        os.replace(temp_pfad, pfad)
        return True

    except Exception as e:
        print(f"[ERROR] Atomic write failed: {e}")
        if os.path.exists(temp_pfad):
            os.remove(temp_pfad)
        return False
    
def refrech():
    """Starts a background thread that periodically checks the file integrity and loads the Keys.
    It will automatically attempt a recovery if the file is corrupted."""
    pass

def health_check(autoCreate=None):
    """Checks if the config file exists and creates a new one from the backup if needed."""
    if not os.path.exists(pfad):
        if autoCreate or config_autoCreate:
            if os.path.exists(backup_pfad):
                os.rename(backup_pfad, pfad)     
                if MsgtoCons_global <= 0: print("[INFO] Config has been restored from backup!")
                return True
            else:
                standard_daten = {"Version": 1.0}
                _write (standard_daten)
                return True
        return False

    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            pass
        return True

    except (json.JSONDecodeError, ValueError):
        if autoCreate or config_autoCreate:
            if MsgtoCons_global <= 1: print("[WARNING] Config file corrupted! Attempting to load backup...")
            
            backup_pfad = pfad + ".bak"
            
            if os.path.exists(backup_pfad):
                os.remove(pfad)
                os.rename(backup_pfad, pfad)
                
                if MsgtoCons_global <= 0: print("[INFO] Config has been restored from backup!")
                return True
            else:
                if MsgtoCons_global <= 2: print("[ERROR] No backup available. Recovery failed.")
                return False
        else:
            if MsgtoCons_global <= 2: print ("[ERROR] Configuration restore from backup is disabled.")
            return False

def scan_keys(daten=None):
    """Checks if a group name or key is on the ignore list."""
    if not health_check():
        return False
    try:
        if daten is not None:
            konflikte = set(daten.keys()) & ignore
        
            if konflikte:
                if MsgtoCons_global <= 2:
                    print(f"[ERROR] Key conflict detected: {konflikte}")
                return False
            return True
        else:
            _daten = _read()
        check_failed = False
        Key_list = []
        ER_Key_list = []
        for key in _daten.keys():
            if key in ignore:
                konflikte.append(key)
                if MsgtoCons_global <= 1: print(f"[WARNING] Key conflict detected: '{key}' is a reserved keyword and cannot be used as a variable name.")
                check_failed = True
                ER_Key_list.append(key)
            else:
                Key_list.append(key)
    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] Failed to scan keys: {e}")
        return False
    
    if MsgtoCons_global <= 0: print (f"[INFO] {Key_list} is not a reserved keyword")
    
    if check_failed:
        return False
    else:
        return True

def libconfig (check=None,autoLoad=True,autoCreate=None,Print=None,set_reset=None,filename=None,MsgtoCons = 0):
    """
       Configures the library settings.
        - check=True/None: Enables/disables config file existence check on initialization.
        - autoLoad=True/None: Enables/disables automatic loading of the config file on initialization
        - autoCreate=True/None: Enables/disables automatic creation of a base config if none exists.
        - Print=True/None: Enables/disables terminal output
        - set_reset=True/None: Enables/disables the ability to set reset points.
        - fileName="Filename"/None: Sets a custom name for the Json file.
        - MsgtoCons=0-3 controls which messages are printed to the console.
          - MsgtoCons=0: All messages are printed.
          - MsgtoCons=1: [WARNING] & [ERROR] are printed.
          - MsgtoCons=2: [ERROR] is printed.
          - MsgtoCons=3: No messages are printed.
    """
    global config_autoCreate, config_Print, config_set_reset, config_autoLoad, config_check, passed, MsgtoCons_global, locked, refresh, mode, ConfVersion

    MsgtoCons_global = MsgtoCons

    MsgtoCons_global = get ("MsgtoCons", group="_header", default=MsgtoCons_global)
    locked = get ("locked", group="_header", default='unlocked') #unlocked, soft_lock, hard_lock
    refresh = get ("refresh", group="_header", default=False)
    mode = get ("mode", group="_header", default="normal") #normal, safe_mode
    if mode == "safe_mode":
        refresh = True
        autoCreate = True
        autoLoad = True 
        set_reset = True
        check = True
    ConfVersion = get ("ConfVersion", group="_header", default=1.0)

    if MsgtoCons_global <= 0: print (f"[INFO] Library configuration initialized with MsgtoCons={MsgtoCons_global}, locked={locked}, refresh={refresh}, mode='{mode}', ConfVersion={ConfVersion}")

    if filename is not None and filename is not False:
        fileName(filename)
    
    if autoCreate is not None and autoCreate is not False:
        config_autoCreate = autoCreate
    else:
        config_autoCreate = False

    Print = get ("Print", group="_header", default=Print)
    if Print is not None and Print is not False:
        config_Print = Print
    else:
        config_Print = False

    if set_reset is not None and set_reset is not False:

        config_set_reset = set_reset
    else:
        config_set_reset = False

    if autoLoad is not None and autoLoad is not False:

        config_autoLoad = autoLoad
        load()

    else:
        config_autoLoad = False

    if check is not None and check is not False:

        config_check = check
    else:
        config_check = False
    
    if config_check:
        if os.path.exists(pfad):
            passed = True
        else:
            if config_autoLoad:
                if MsgtoCons_global <= 0: print("[INFO] Auto loading config...")
                load()
                if os.path.exists(pfad):
                    passed = True
                else:
                    if MsgtoCons_global <= 2:print("[ERROR] No Config found and unable to auto load! Please create a config file or disable 'Config check' in libconfig.")
                    passed = False
            else:
                if MsgtoCons_global <= 2: print("[ERROR] No Config found! Please create a config file or disable 'Config check' in libconfig.")
                passed = False
    
    if not setreset():
        if not config_set_reset:
            if MsgtoCons_global <= 1: print ("[WARNING] 'Set reset point' is disabled.")
            if passed:
                pass
        else:
            if MsgtoCons_global <= 1: print ("[WARNING] Could not set reset point. Ensure that the config file exists or 'Set reset point' is enabled.")
            passed = False
        
    return passed

def fileName(filename):
    """Sets the name of the config file."""
    global pfad, backup_pfad, reset_pfad
    pfad = os.path.join(os.path.dirname(__file__), filename)
    backup_pfad = pfad + ".bak"
    reset_pfad = pfad + ".reset"
    if os.path.exists(pfad):
        return True
    else:
        return False

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

    1. libconfig(check=True/None,autoLoad=True/None,autoCreate=True/None,Print=True/None,set_reset=True/None, filename="Filename"/None, MsgtoCons=0-3) [X]
       Configures the library settings.
        - check=True/None: Enables/disables config file existence check on initialization.
        - autoLoad=True/None: Enables/disables automatic loading of the config file on initialization
        - autoCreate=True/None: Enables/disables automatic creation of a base config if none exists.
        - Print=True/None: Enables/disables terminal output
        - set_reset=True/None: Enables/disables the ability to set reset points.
        - fileName="Filename"/None: Sets a custom name for the Json file.
        - MsgtoCons=0-3 controls which messages are printed to the console.
          - MsgtoCons=0: All messages are printed.
          - MsgtoCons=1: [WARNING] & [ERROR] are printed.
          - MsgtoCons=2: [ERROR] is printed.
          - MsgtoCons=3: No messages are printed.

    2. fileName(filename)
       Sets the name of the config file.

    3. setreset(set_reset=TrueNone) [X]
       Sets a reset point by creating a .reset backup of the current config file.
         - set_reset=True/None: Enables/disables the ability to set reset points.
    
    4. reset() [X]
       Restores the config file from the .reset backup.
    
    5. load(autoCreate=True/None) [X]
       Loads JSON data into global memory.
       - autoCreate=True: Creates a base config if none exists 
         or restors it form the Backup.
         If the argument is omitted, no config file is created.
       - Should the config file be corrupted, the function 
         attempts to restore the file from the backup.

    6. show(Print=True/None)
       Returns all loaded variable names as a list.
       If set to 'True', output is displayed in the terminal.

    7. edit(Var, Val,group="name"/None) [X]
       Changes an EXISTING value directly via code. 

    8. dump(dict) [X]
       Updates EXISTING values in the JSON. 
       Prevents accidental creation of new keys.

    9. add(Varname, Varvalue) [X]
       Creates a NEW data point in the JSON file.

    10. addlist(dict) [X]
       Adds multiple NEW data points simultaneously.
       Example: j.addlist({"D1": 10, "D2": 20})

    11. search(Varname) [X]
       Checks if a variable exists in the config (True/False).

    12. delete(name) [X]
       Permanently deletes a data point from the file and memory.

    13. backup() [X]
        Creates a backup/current state of the config file (Config.json.bak)

    14. get(key, group=None, default=None)
        Secure data access.
        - I = jsonBib.get("Name", group="group", default="DefaultValue")
        - The Key is the name of the data point to retrieve.
        - The Group (optional) specifies a subgroup within the JSON structure.
        - The DefaultValue (optional) is used if "Name" is not in the config file.

    15. getAll()
        Returns all data points in the config file as a dictionary.

    16. validate(Var, Valmin, Valmax=None) [X]
        Validates if a variable meets specified conditions.
        - For numerical values, both minimum and maximum can be set.
        - For boolean or None values, only Valmin is required.
    
    17. renameGroup(old_name, new_name) [X]
        Renames a Group or Key.

    18. compare (Filename1=None,Filename2=None) [X]
        lets you compare the content of two files.
        if no file name is given the function will compare the 
        set config file and the Config.reset file

    19. scan_keys(daten=None) [X]
       Checks if a group name or key is on the ignore list.
        - if daten is None, the function checks all keys in the config file and prints a warning for any conflicts.
        - if daten is provided, the function checks only the keys in the provided dictionary and returns 'True' if no conflicts are found or 'False' if conflicts exist.
        

    CONTROLS & SECURITY:
    - The delete function permanently removes data from the config file.
    - Use 'Ctrl+C' or 'exit' to safely cancel the editor.
    ============================================================
    """
    print(header)
    print(config_info)
    print(functions)

def backup():
    """Creates a backup/current state of the config file (Config.json.bak)"""
    if os.path.exists(pfad):
        shutil.copy(pfad, pfad + ".bak")
        return True
    return False

def load(autoCreate=None):
    """Loads JSON data into global memory.
       - autoCreate=True: Creates a base config if none exists 
         or restors it form the Backup.
         If the argument is omitted, no config file is created.
       - Should the config file be corrupted, the function 
         attempts to restore the file from the backup."""
    
    scan_keys()
    if health_check(autoCreate=autoCreate):
        try:
            _daten = _read()
            cfg.__dict__.clear()
            cfg.__dict__.update(_daten)
        except Exception as e:
            if MsgtoCons_global <= 2: print(f"[ERROR] Failed to load config: {e}")
            return False
        if MsgtoCons_global <= 0: print(f"[INFO] Config file loaded into 'cfg' object.")
        return True
    else:
        return False

def setreset(set_reset=None):
    """
    Sets a reset point by creating a .reset backup of the current config file.
         - set_reset=True/None: Enables/disables the ability to set reset points.
    """
    if config_set_reset or set_reset:
        if not health_check():
            return False
        try:
            if os.path.exists(pfad):
                shutil.copy(pfad, pfad + ".reset")
                if MsgtoCons_global <= 0: print(f"[INFO] Reset point set successfully. Reset point saved as '{reset_pfad}'")
                return True
            return False
        except Exception as e:
            if MsgtoCons_global <= 2: print(f"[ERROR] Failed to set reset point: {e}")
            return False
    else:
        return False

def show (Print=None):
    """Returns all loaded variable names as a list.
       If set to 'True', output is displayed in the terminal."""
    variablen = [name for name in cfg.__dict__ if not name.startswith("__") and name not in donotEdit]
    if Print or config_Print:
        print (variablen)
    else:
        pass
    return variablen

def dump(new_data, group=None):
    """ Updates EXISTING values in the JSON. 
       Prevents accidental creation of new keys."""
    
    if not health_check():
        return False
    
    if not scan_keys(new_data):
        return False
    
    if  group in ignore:
        return False
    
    backup()
    try:
        daten = _read()
    except FileNotFoundError:
        if MsgtoCons_global <= 2: print("[ERROR] File not found.")
        return False
    
    if group == "_header":
        if MsgtoCons_global <= 2: print(f"[ERROR] The '_header' group is reserved and cannot be edited.")
        return False
    elif new_data.keys() & donotEdit:
        if MsgtoCons_global <= 2: print(f"[ERROR] Attempt to edit reserved keys: {new_data.keys() & donotEdit}.")
        return False
    
    success = False
    try:
        if group:
            if group in daten and isinstance(daten[group], dict):
                for key, wert in new_data[group].items():
                    if key in daten[group]:
                        daten[group][key] = wert
                        if MsgtoCons_global <= 0: print(f"[INFO] Update in '{group}': {key} updated.")
                        success = True
                    else:
                        if MsgtoCons_global <= 2: print(f"[ERROR] Key '{key}' not found in group '{group}'.")
            else:
                if MsgtoCons_global <= 2: print(f"[ERROR] Group '{group}' does not exist.")
                return False
        else:
            for key, wert in new_data.items():
                if key in daten:
                    daten[key] = wert
                    if MsgtoCons_global <= 0: print(f"[INFO] Update successful: {key} updated.")
                    success = True
                else:
                    if MsgtoCons_global <= 2: print(f"[ERROR] Key '{key}' does not exist. Use 'add' or 'addlist' to create new keys.")
    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] Failed to update: {e}")
        return False
    
    if success:
        try:
            olddaten = _read()
            olddaten.update(daten)
            _write(daten)
            backup()
            return True
        except Exception as e:
            if MsgtoCons_global <= 2: print(f"[ERROR] Failed to write updated data: {e}")
            return False
    
    return False

def edit(Var, Val, group=None):
    """Changes an EXISTING value directly via code."""

    if not health_check():
        return False
    
    try:
        if Var in donotEdit:
            if MsgtoCons_global <= 2: print(f"[ERROR] '{Var}' is a Header attribute and cannot be edited.")
            return False
        elif group == "_header":
            if MsgtoCons_global <= 2: print(f"[ERROR] The '_header' group is reserved and cannot be edited.")
            return False
        
        if group:
            payload = {group: {Var: Val}} 
        else:
            payload = {Var: Val}

        return dump(payload, group=group)

    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] {e}")
        return False

def search (Varsearch):
    """Checks if a variable exists in the config (True/False)."""
    if not health_check():
        return False
    
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
    """Creates a NEW data point in the JSON file."""

    if not health_check():
        return False
    
    if locked == 'soft_lock':
        if MsgtoCons_global <= 1: print("[WARRNING] File is currently soft-locked. Keys cannot be added but existing keys can be edited.")
        return False
    
    for a in ignore:
        if Varname == a or Varname in donotEdit:
            if MsgtoCons_global <= 2: print(f"[ERROR] '{Varname}' is a reserved keyword and cannot be used as a variable name.")
            return False
    newVardata = {Varname: Varvalue}

    daten = _read()

    daten.update(newVardata)

    _write(daten)
    
    if MsgtoCons_global <= 0: print(f"Update successful: {list(newVardata.keys())} updated.")
    backup()
    return True

def addlist(newVarlist):
    """Adds multiple NEW data points simultaneously.
       Example: j.addlist({"D1": 10, "D2": 20})"""
    if not health_check():
        return False

    if locked == 'soft_lock':
        if MsgtoCons_global <= 1: print("[WARRNING] File is currently soft-locked. Keys cannot be added but existing keys can be edited.")
        return False
    
    if newVarlist.keys() & ignore or newVarlist.keys() & donotEdit:
        if MsgtoCons_global <= 2: print(f"[ERROR] '{newVarlist.keys() & ignore}{newVarlist.keys() & donotEdit}' is a reserved keyword and cannot be used as a variable name.")
        return False
        
    daten = _read()

    daten.update(newVarlist)

    _write(daten)
    
    if MsgtoCons_global <= 0: print(f"Update successful: {list(newVarlist.keys())} updated.")
    return True

def delete(name):
    """Permanently deletes a data point from the file and memory."""
    if not health_check():
        return False
    
    if locked == 'soft_lock':
        if MsgtoCons_global <= 1: print("[WARRNING] File is currently soft-locked. Keys cannot be added or deleted.")
        return False

    try:
        daten = _read()
        
        if name in daten:
            if name in donotEdit:
                if MsgtoCons_global <= 2: print(f"[ERROR] '{name}' is a reserved keyword and cannot be deleted.")
                return False
            del daten[name]
            _write(daten)
            
            if hasattr(cfg, name): 
                delattr(cfg, name)
                
            if MsgtoCons_global <= 0: print(f"[INFO] '{name}' deleted successfully.")
            backup ()
            return True
        else:
            if MsgtoCons_global <= 2: print(f"[ERROR] '{name}' does not exist and cannot be deleted.")
            return False
            
    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] Failed to delete: {e}")
        return False
    
def get(key, group=None, default=None):
    """Secure data access.
        - I = jsonBib.get("Name", group="group", default="DefaultValue")
        - The Key is the name of the data point to retrieve.
        - The Group (optional) specifies a subgroup within the JSON structure.
        - The DefaultValue (optional) is used if "Name" is not in the config file."""
    try:
        daten = _read()

        if group is not None:
            if group in daten and key in daten[group]:
                wert = daten[group][key]
            else:
                return default

        else:
            def find_recursive(obj, target):
                if target in obj:
                    return obj[target]
                for v in obj.values():
                    if isinstance(v, dict):
                        res = find_recursive(v, target)
                        if res is not None:
                            return res
                return None
            
            wert = find_recursive(daten, key)

        if wert is None:
            return default
    
        return wert

    except Exception as e:
        if MsgtoCons_global <= 3: print(f"[ERROR] get failed for '{key}': {e}")
        return default
    
def getAll():
    """Returns all data points in the config file as a dictionary."""
    health_check()
    backup()
    try:
        data = _read()
        return data
    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] getAll failed: {e}")
        return None

def reset():
    """Restores the config file from the .reset backup."""
    if locked == 'soft_lock':
        if MsgtoCons_global <= 1: print("[WARRNING] File is currently soft-locked and cannot be reset.")
        return False

    try:
        if os.path.exists(reset_pfad):
            if os.path.exists(pfad):
                os.remove(pfad)
            os.rename(reset_pfad, pfad)
            setreset()
            load()
            if MsgtoCons_global <= 0: print("[INFO] Config has been restored and loaded from .reset!")
            return True
        else:
            if MsgtoCons_global <= 2: print("[ERROR] No reset file found. Reset failed.")
            return False
    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] Failed to reset configuration: {e}")
        return False
    
def validate(Var, Valmin, Valmax=None):
    """Validates if a variable meets specified conditions.
        - For numerical values, both minimum and maximum can be set.
        - For boolean or None values, only Valmin is required."""
    if not health_check():
        return False
    
    current_val = get(Var)

    if current_val is None:
        if MsgtoCons_global <= 2: print(f"[ERROR] The variable '{Var}' does not exist.")
        return False
    if Valmax is not None and isinstance(Valmax, (bool, str, type(None))):
        if MsgtoCons_global <= 2: print("[ERROR] Valmax must be a number.")
        return False
    if not isinstance(Valmin, (bool, type(None))):
        if isinstance(Valmin, (int, float)):
            if Valmax is not None:
                if Valmin <= get(Var) <= Valmax:
                    return True
                else:
                    return False
            else:
                if get(Var) == Valmin:
                    return True
                else:
                    return False
    else:
        if get(Var) == Valmin:
            return True
        else:
            return False
        
def renameGroup(old_name, new_name):
    """Renames a Group or Key."""
    if not health_check():
        return False
    
    if locked == 'soft_lock':
        if MsgtoCons_global <= 1: print("[WARRNING] File is currently soft-locked. Keys cannot be renamed.")
        return False
    
    if new_name in ignore or new_name in donotEdit:
        if MsgtoCons_global <= 2: print(f"[ERROR] '{new_name}' is a reserved keyword and cannot be used as a group name.")
        return False
    elif old_name in ignore or old_name in donotEdit:
        if MsgtoCons_global <= 2: print(f"[ERROR] '{old_name}' is a reserved keyword and cannot be changed.")
        return False
    
    try:
        backup()
        daten = _read()

        if new_name in daten:
            if MsgtoCons_global <= 2: print(f"[ERROR] Group '{new_name}' already exists.")
            return False
        if old_name in daten:
            daten[new_name] = daten.pop(old_name)
            
            _write(daten)
            
            if MsgtoCons_global <= 0: print(f"[SUCCESS] Group '{old_name}' renamed to '{new_name}'")
            return True
        else:
            if MsgtoCons_global <= 2: print(f"[ERROR] Group '{old_name}' not found.")
            return False
            
    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] {e}")
        return False
    
def compare (Filename1=None,Filename2=None):
    """lets you compare the content of two files.
        if no file name is given the function will compare the 
        set config file and the Config.reset file"""
    
    if Filename1 == None:
        file1_pfad = pfad
    else:
        file1_pfad = os.path.join(os.path.dirname(__file__), Filename1)
    
    if Filename2 == None:
        file2_pfad = reset_pfad
    else:
        file2_pfad = os.path.join(os.path.dirname(__file__), Filename2)
    
    try:
        confjson = _read(file1_pfad)
        
        resetjson = _read(file2_pfad)

        dif = confjson.keys() ^ resetjson.keys()

    except Exception as e:
        if MsgtoCons_global <= 2: print(f"[ERROR] Failed to compare files: {e}")
        return False

    if MsgtoCons_global <= 0 and dif: print(f"[INFO] The following keys differ between the two files: {dif}")

    if confjson == resetjson:
        return True
    else:
        return False