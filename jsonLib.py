# JSON Library for Python (v4.0) in defvelopment

import json
import os
import shutil
import tempfile
from xml.etree.ElementTree import indent
import portalocker
import datetime
import threading
import time

file_Name = 'files/V4.json'
pfad = os.path.join(os.path.dirname(__file__), file_Name)
backup_pfad = pfad + ".bak"
reset_pfad = pfad + ".reset"
typemap_path = pfad + ".typemap"
config_autoCreate = False
config_Print = False
config_set_reset = False
config_autoLoad = False
config_check = False
passed = True
MsgtoCons_global = 0
locked_global= "unlocked" #unlocked, soft_lock, hard_lock
refresh_global= False
mode_global = "normal" #normal, safe_mode, typemap
indent_global = 4
ensure_ascii_global = False
dataSaver_global = None
ConfVersion = 1.0
refresh_cycle = False
refresh_alive = False
lockdown = False

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

def info():
    
    header = """
    ============================================================
    JSON LIBRARY - DOCUMENTATION (v3.2)
    ============================================================

    """
    
    config_info = f"Config Path: {pfad}"

    functions = """

    AVAILABLE FUNCTIONS:
    [Functions marked with [X] return 'True' if executed 
    successfully and 'False' upon failure]

    1. libconfig(check=True/None,autoLoad=True/None,autoCreate=True/None,Print=True/None,set_reset=True/None, filename="Filename"/None, MsgtoCons=0-3) [X]
       Configures the library settings.
        - setup=None/dict: Enables you to send all config variables as a dict
          - dict = {"check":None,"autoLoad":None,"autoCreate":None,"Print":None,"set_reset":None,"filename":"files/config.json","MsgtoCons":0,"Vers":None,"VersHi":None,"VersLow":None,"mode":None,"refresh":None,"locked":None,"indent":None,"ensure_ascii":None,"dataSaver":None}
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
          - MsgtoCons="INFO": Only Info mesages
          - MsgtoCons="WARNING": Only WARNING mesages
          - MsgtoCons="ERROR": Only ERROR mesages
        - Vers: Sets a specific version range. If VersHi or VersLow is None, it defines the exact supported config version. 
                If the version does not match, the library enters lockdown mode.
          - Lockdown: Once engaged, no functions can be accessed. This ensures the integrity of both the program and your configuration file.
          - Vers=1.0/None: Sets the exact supported config version.
          - VersHi=1.0/None: Sets the highest supported config version.
          - VersLow=1.0/None: Sets the lowest supported config version.

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
    
    20. check_refresh(interval=5)
        - Starts a background daemon thread to monitor file integrity.
        - Automatically reloads keys into j.cfg if refresh=True is set in libconfig.

    21. check_refresh_toggle(cycle=None)
        Controls the refresh cycle during runtime without killing the thread.
        - cycle=True: Resumes monitoring.
        - cycle=False: Pauses monitoring (Thread enters idle state).
        - cycle=None: Toggles the current state.

    22. versCheck (Vers):
        - Vers: Sets a specific version range. If VersHi or VersLow is None, it defines the exact supported config version. 
            If the version does not match, the library enters lockdown mode.
        - Lockdown: Once engaged, no functions can be accessed. This ensures the integrity of both the program and your configuration file.
        - Vers=1.0/None: Sets the exact supported config version.
        - VersHi=1.0/None: Sets the highest supported config version.
        - VersLow=1.0/None: Sets the lowest supported config version.

    23. create(Filename, contentdir, headir=None, Full_Path=None) [X]
        - Creates a NEW JSON file with a standardized header.
        - contentdir: The dictionary containing the file data.
        - headir: Optional custom header. If None, a default headir_base (v1.0) is used.
        - Full_Path=True: Uses the Filename as the absolute path.
        - Full_Path=None: Combines the current directory with the Filename.

    24. rename(Filename_old, Filename_new, Full_Path=None)
        - Renames or moves a file.
        - It reads the data from the old file, creates a new file with that data using create(), and subsequently deletes the original file.

    CONTROLS & SECURITY:
    - The delete function permanently removes data from the config file.
    - Use 'Ctrl+C' or 'exit' to safely cancel the editor.
    ============================================================
    """
    print(header)
    print(config_info)
    print(functions)

def _read(filename=None,Full_Path=None):
    """Reads the config file and returns the raw content."""

    if lockdown:
        return False
    
    if filename is not None:
        if Full_Path is not None:
            if not fileName(filename, Full_Path=Full_Path):
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] File does not exist {filename}")
                return False
        else:
            if not fileName(filename):
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] File does not exist {filename}")
                return False


    if health_check():
        try:
            with open(pfad, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to read file: {e}")
            return None
    else:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print ("[ERROR] File could not be Opened")
        return None

def _write(daten, filename=None, Full_Path=None):

    if lockdown:
        return False

    if filename is not None:
        if Full_Path is not None:
            if not fileName(filename, Full_Path=Full_Path):
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] File does not exist {filename}")
                return False
        else:
            if not fileName(filename):
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] File does not exist {filename}")
                return False


    if locked_global == 'hard_lock':
        if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARRNING] File is currently locked.")
        return False
    
    ordner = os.path.dirname(pfad)
    if not os.path.exists(ordner) and ordner != '':
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print ("[ERROR] Directory does not exist. Please create the directory or specify a valid path.")
        return False

    fd, temp_pfad = tempfile.mkstemp(dir=ordner, prefix="temp_cfg_", suffix=".json")

    if "_header" in daten:
        daten["_header"]["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        if dataSaver_global:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_EX)
                json.dump(daten, f, indent=None, separators=(',', ':'), ensure_ascii=ensure_ascii_global)
                f.flush()
                os.fsync(f.fileno())
                portalocker.unlock(f)
            os.replace(temp_pfad, pfad)
            return True
        else:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                portalocker.lock(f, portalocker.LOCK_EX)
                json.dump(daten, f, indent=indent_global, ensure_ascii=ensure_ascii_global)
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
    
def _typechecker (Var, Val, Change=None, Var_group=None):
    _Type_List = ["INT", "STRING", "FLOAT", "LIST", "BOOLEAN", None]
    _Allow_List = ["RANGE", "LIST", "EXCLUDE", "VALUE", "INT", "STRING", "FLOAT", "BOOLEAN", None]
    old_path = pfad
    fileName(typemap_path)
    if Var_group is None:
        typemap_data = get(Var)
    else:
        typemap_data = get(Var, group=Var_group)
    _Type = typemap_data["Type"]
    _Allow = typemap_data["Allow"]
    _Content = typemap_data["Content"]
    _Default = typemap_data["Def"]

    if _Type not in _Type_List:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Wrong attibut in Typemap Data. {_Type}")
        fileName(old_path)
        return False

    if _Allow not in _Allow_List:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Wrong attibut in Typemap Data. {_Allow}")
        fileName(old_path)
        return False

    fileName(old_path)

def check_refresh_toggle(cycle=None):
    """Starts and stops the refresh cycle that periodically checks the file integrity and loads the Keys."""
    global refresh_cycle
    if cycle:
        refresh_cycle = True
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Refresh cycle enabled.")
    elif cycle is None:
        refresh_cycle = not refresh_cycle
        if refresh_cycle:
            if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Refresh cycle enabled.")
        else:
            if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Refresh cycle disabled.")
    else:
        refresh_cycle = False
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Refresh cycle disabled.")

def check_refresh(interval=5):
    """Starts a background thread that periodically checks the file integrity and loads the Keys.
    It will automatically attempt a recovery if the file is corrupted."""
    if lockdown:
        return False
    
    global refresh_alive
    def run_check():
        while True:
            time.sleep(interval)
            if refresh_cycle:
                if not health_check():
                    if MsgtoCons_global <= 1 or MsgtoCons_global == 5:
                        print("[WARNING] File integrity issue detected and handled.")
                else:
                    if refresh_global:
                        load()
                        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] File loaded successfully.")
    if not refresh_alive:
        refresh_alive = True
        thread = threading.Thread(target=run_check, daemon=True)
        thread.start()

def health_check(autoCreate=None):
    """Checks if the config file exists and creates a new one from the backup if needed."""

    if lockdown:
        return False
    
    global backup_pfad
    if not os.path.exists(pfad):
        if autoCreate or config_autoCreate:
            if os.path.exists(backup_pfad):
                os.rename(backup_pfad, pfad)     
                if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Config has been restored from backup!")
                return True
            else:
                standard_daten = {
                    "_header": {
                        "ConfVersion": 1.0,
                        "mode": "normal",
                        "refresh": True,
                        "locked": "unlocked",
                        "Print": None,
                        "MsgtoCons": 0,
                        "last_updated": "2000-01-01 00:00:00"
                    },
                    "Version": 1.0
                    }
                _write (standard_daten)
                return True
        return False

    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            pass
        return True

    except (json.JSONDecodeError, ValueError):
        if autoCreate or config_autoCreate:
            if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARNING] Config file corrupted! Attempting to load backup...")
            
            backup_pfad = pfad + ".bak"
            
            if os.path.exists(backup_pfad):
                os.remove(pfad)
                os.rename(backup_pfad, pfad)
                
                if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Config has been restored from backup!")
                return True
            else:
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print("[ERROR] No backup available. Recovery failed.")
                return False
        else:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print ("[ERROR] Configuration restore from backup is disabled.")
            return False

def scan_keys(daten=None):
    """Checks if a group name or key is on the ignore list."""
    global konflikte
    if lockdown:
        return False
    
    if not health_check():
        return False
    try:
        if daten is not None:
            konflikte = set(daten.keys()) & ignore
        
            if konflikte:
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6:
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
                if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print(f"[WARNING] Key conflict detected: '{key}' is a reserved keyword and cannot be used as a variable name.")
                check_failed = True
                ER_Key_list.append(key)
            else:
                Key_list.append(key)
    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to scan keys: {e}")
        return False
    
    if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print (f"[INFO] {Key_list} is not a reserved keyword")
    
    if check_failed:
        return False
    else:
        return True

def libconfig (setup=None,check=None,autoLoad=True,autoCreate=None,Print=None,set_reset=None,filename=None,MsgtoCons = 0,Vers=None,VersHi=None,VersLow=None,mode=None,refresh=None,locked=None, indent=None, ensure_ascii=None, dataSaver=None):
    """
       Configures the library settings.
        - setup=None/dict: Enables you to send all config variables as a dict
          - dict = {"check":None,"autoLoad":None,"autoCreate":None,"Print":None,"set_reset":None,"filename":"files/config.json","MsgtoCons":0,"Vers":None,"VersHi":None,"VersLow":None,"mode":None,"refresh":None,"locked":None,"indent":None,"ensure_ascii":None,"dataSaver":None}
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
          - MsgtoCons="INFO": Only INFO mesages
          - MsgtoCons="WARNING": Only WARNING mesages
          - MsgtoCons="ERROR": Only ERROR mesages
        - Vers: Sets a specific version range. If VersHi or VersLow is None, it defines the exact supported config version. 
                If the version does not match, the library enters lockdown mode.
          - Lockdown: Once engaged, no functions can be accessed. This ensures the integrity of both the program and your configuration file.
          - Vers=1.0/None: Sets the exact supported config version.
          - VersHi=1.0/None: Sets the highest supported config version.
          - VersLow=1.0/None: Sets the lowest supported config version.
    """
    global config_autoCreate, config_Print, config_set_reset, config_autoLoad, config_check, passed, MsgtoCons_global, locked_global, refresh_global, mode_global, ConfVersion, indent_global, ensure_ascii_global, dataSaver_global

    if setup is not None:
        #dict = {"check":None,"autoLoad":None,"autoCreate":None,"Print":None,"set_reset":None,"filename":"files/config.json","MsgtoCons":0,"Vers":None,"VersHi":None,"VersLow":None,"mode":None,"refresh":None,"locked":None,"indent":None,"ensure_ascii":None,"dataSaver":None}
        check      = setup.get("check", None)
        autoLoad   = setup.get("autoLoad", None)
        autoCreate = setup.get("autoCreate", None)
        Print      = setup.get("Print", None)
        set_reset  = setup.get("set_reset", None)
        filename   = setup.get("filename", "files/config.json")
        MsgtoCons  = setup.get("MsgtoCons", 0)
        Vers       = setup.get("Vers", None)
        VersHi     = setup.get("VersHi", None)
        VersLow    = setup.get("VersLow", None)
        mode       = setup.get("mode", None)
        refresh    = setup.get("refresh", None)
        locked     = setup.get("locked", None)
        indent     = setup.get("indent", None)
        ensure_ascii = setup.get("ensure_ascii", None)
        dataSaver  = setup.get("dataSaver", None)

    if indent is not None:
        indent_global = indent
    else:
        indent_global = 4

    if ensure_ascii is not None:
        if ensure_ascii == True:
            ensure_ascii_global = True
        else:
            ensure_ascii_global = False
    else:
        ensure_ascii_global = False

    if dataSaver is not None:
        print (f"dataSaver not None: {dataSaver}")
        if dataSaver == True:
            dataSaver_global = True
        elif dataSaver == False:
            dataSaver_global = False
        else:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Invalid value for 'dataSaver'. Please send a boolean value (True/False).")
            dataSaver_global = None

    try:
        MsgtoCons_int = int(MsgtoCons)
        if 0 <= MsgtoCons_int <= 3:
            MsgtoCons = MsgtoCons_int
        else:
            MsgtoCons = 0

    except ValueError:
        if MsgtoCons == "INFO":
            MsgtoCons = 4
        elif MsgtoCons == "WARNING":
            MsgtoCons = 5
        elif MsgtoCons == "ERROR":
            MsgtoCons = 6
        else:
            MsgtoCons = 0

    if filename is not None and filename is not False:
        fileName(filename)

    mode_list = ["normal", "safe_mode"]
    locked_list = ["unlocked", "soft_lock", "hard_lock"]

    if mode is not None:
        if mode not in mode_list:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] The specified mode ({mode}) is not supported. Initializing the file in Hard safe_mode.")
            mode = "safe_mode"

    if locked is not None:
        if locked not in locked_list:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Lock method ({locked}) is not supported. Initializing the file in hard_lock mode.")
            mode = "hard_lock"
    else:
        locked = "hard_lock"
    
    if refresh is not None:
        if not isinstance(refresh,bool):
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print("[ERROR] 'refresh' must be a boolean. Setting 'refresh' to False.")
            refresh = False

    MsgtoCons_global = get ("MsgtoCons", group="_header", default=MsgtoCons)
    locked_global= get ("locked", group="_header", default=locked) #unlocked, soft_lock, hard_lock
    refresh_global= get ("refresh", group="_header", default=refresh)
    mode_global = get ("mode", group="_header", default= mode) #normal, safe_mode

    if mode_global not in mode_list:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] The specified mode ({mode_global}) of the Fileheader is not supported. Initializing the file in Hard safe_mode.")
        mode_global = "safe_mode"

    if locked_global not in locked_list:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Lock method ({locked_global}) of the Fileheader is not supported. Initializing the file in hard_lock mode.")
        locked_global = "hard_lock"

    if mode_global == "safe_mode":
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print (f"[INFO] Safe Mode activated")
        refresh_global= True
        autoCreate = True
        autoLoad = True 
        set_reset = True
        check = True
        check_refresh()
        check_refresh_toggle(cycle=True)
        
    ConfVersion = get ("ConfVersion", group="_header", default=1.0)

    if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print (f"[INFO] Library configuration initialized with MsgtoCons={MsgtoCons_global}, locked={locked_global}, refresh={refresh_global}, mode='{mode_global}', ConfVersion={ConfVersion}")

    if Vers is not None:
        versCheck(Vers,VersHi,VersLow)
    
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
                if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Auto loading config...")
                load()
                if os.path.exists(pfad):
                    passed = True
                else:
                    if MsgtoCons_global <= 2 or MsgtoCons_global == 6:print("[ERROR] No Config found and unable to auto load! Please create a config file or disable 'Config check' in libconfig.")
                    passed = False
            else:
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print("[ERROR] No Config found! Please create a config file or disable 'Config check' in libconfig.")
                passed = False
    
    if not setreset():
        if not config_set_reset:
            if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print ("[WARNING] 'Set reset point' is disabled.")
            if passed:
                pass
        else:
            if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print ("[WARNING] Could not set reset point. Ensure that the config file exists or 'Set reset point' is enabled.")
            passed = False    
    return passed

def versCheck (Vers,VersHi,VersLow):
    """Checks if the config version matches the required version"""
    global lockdown

    if VersHi is None:
        VersHi = Vers

    if VersLow is None:
        VersLow = Vers

    ConfVersion = get ("ConfVersion", group="_header")
    if ConfVersion is None:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print ("""[ERROR] Version not Found. Library is in lockdown. Send versCheck("unlock") to unlock the Libary""")
        lockdown = True
        return False
    elif Vers == "unlock":
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print ("""[INFO] Library is now Unlocked""")
        lockdown = False
        return True
    elif VersLow <= ConfVersion <= VersHi:
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print ("""[INFO] Library version matches required version.""")
        lockdown = False
        return True
    else:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print ("""[ERROR] Config Version dose not match. Library is in lockdown. Send versCheck("unlock") to unlock the Libary""")
        lockdown = True
        return False

def fileName(filename,Full_Path=None):
    """Sets the filename or the absolute path of the configuration file.
Note: Windows paths should be passed as raw strings to avoid escape sequence errors.
Example: filename=r"C:\\Users\\Name\\config.json"
"""

    if lockdown:
        return False
    
    if locked_global != "unlocked":
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"""[ERROR] File is in {locked_global} mode. The filename or path cannot be changed.""")
        return False
    
    global pfad, backup_pfad, reset_pfad, typemap_path
    
    old_pfad = pfad
    old_backup_pfad = backup_pfad
    old_reset_pfad = reset_pfad
    old_typemap_path = typemap_path

    if Full_Path == None:
        pfad = os.path.join(os.path.dirname(__file__), filename)
        backup_pfad = pfad + ".bak"
        reset_pfad = pfad + ".reset"
        typemap_path = pfad + ".typemap"
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] New Filename was set")
    elif Full_Path == True:
        pfad = filename
        backup_pfad = pfad + ".bak"
        reset_pfad = pfad + ".reset"
        typemap_path = pfad + ".typemap"
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] Full Path was set")
    else:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"""[ERROR] Invalid path-indicator was sent. 
Please send 'Full_Path=None' to change the filename or 'Full_Path=True' to set a full path.""")
        return False

    if os.path.exists(pfad):
        return True
    else:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"""[ERROR] File or path ({pfad}) does not exist. The path was changed back.""")
        pfad = old_pfad
        backup_pfad = old_backup_pfad
        reset_pfad = old_reset_pfad
        typemap_path = old_typemap_path
        return False

def backup():
    """Creates a backup/current state of the config file (Config.json.bak)"""

    if lockdown:
        return False
    
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
    
    if lockdown:
        return False
    
    scan_keys()
    if health_check(autoCreate=autoCreate):
        try:
            _daten = _read()
            cfg.__dict__.clear()
            cfg.__dict__.update(_daten)
        except Exception as e:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to load config: {e}")
            return False
        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] Config file loaded into 'cfg' object.")
        return True
    else:
        return False

def setreset(set_reset=None):
    """
    Sets a reset point by creating a .reset backup of the current config file.
         - set_reset=True/None: Enables/disables the ability to set reset points.
    """

    if lockdown:
        return False
    
    if config_set_reset or set_reset:
        if not health_check():
            return False
        try:
            if os.path.exists(pfad):
                shutil.copy(pfad, pfad + ".reset")
                if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] Reset point set successfully. Reset point saved as '{reset_pfad}'")
                return True
            return False
        except Exception as e:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to set reset point: {e}")
            return False
    else:
        return False

def show (Print=None):
    """Returns all loaded variable names as a list.
       If set to 'True', output is displayed in the terminal."""
    
    if lockdown:
        return False
    
    variablen = [name for name in cfg.__dict__ if not name.startswith("__") and name not in donotEdit]
    if Print or config_Print:
        print (variablen)
    else:
        pass
    return variablen

def dump(new_data, group=None):
    """ Updates EXISTING values in the JSON. 
       Prevents accidental creation of new keys."""
    
    if lockdown:
        return False
    
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
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print("[ERROR] File not found.")
        return False
    
    if group == "_header":
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] The '_header' group is reserved and cannot be edited.")
        return False
    elif new_data.keys() & donotEdit:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Attempt to edit reserved keys: {new_data.keys() & donotEdit}.")
        return False
    
    success = False
    try:
        if group:
            if group in daten and isinstance(daten[group], dict):
                for key, wert in new_data[group].items():
                    if key in daten[group]:
                        daten[group][key] = wert
                        if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] Update in '{group}': {key} updated.")
                        success = True
                    else:
                        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Key '{key}' not found in group '{group}'.")
            else:
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Group '{group}' does not exist.")
                return False
        else:
            for key, wert in new_data.items():
                if key in daten:
                    daten[key] = wert
                    if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] Update successful: {key} updated.")
                    success = True
                else:
                    if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Key '{key}' does not exist. Use 'add' or 'addlist' to create new keys.")
    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to update: {e}")
        return False
    
    if success:
        try:
            olddaten = _read()
            olddaten.update(daten)
            _write(daten)
            backup()
            return True
        except Exception as e:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to write updated data: {e}")
            return False
    
    return False

def edit(Var, Val, group=None):
    """Changes an EXISTING value directly via code."""

    if lockdown:
        return False

    if not health_check():
        return False
    
    try:
        if Var in donotEdit:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{Var}' is a Header attribute and cannot be edited.")
            return False
        elif group == "_header":
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] The '_header' group is reserved and cannot be edited.")
            return False
        
        if group:
            payload = {group: {Var: Val}} 
        else:
            payload = {Var: Val}

        return dump(payload, group=group)

    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] {e}")
        return False

def search (Varsearch):
    """Checks if a variable exists in the config (True/False)."""

    if lockdown:
        return False
    
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

    if lockdown:
        return False

    if not health_check():
        return False
    
    if locked_global== 'soft_lock':
        if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARRNING] File is currently soft-locked. Keys cannot be added but existing keys can be edited.")
        return False
    
    for a in ignore:
        if Varname == a or Varname in donotEdit:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{Varname}' is a reserved keyword and cannot be used as a variable name.")
            return False
    newVardata = {Varname: Varvalue}

    daten = _read()

    daten.update(newVardata)

    _write(daten)
    
    if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"Update successful: {list(newVardata.keys())} updated.")
    backup()
    return True

def addlist(newVarlist):
    """Adds multiple NEW data points simultaneously.
       Example: j.addlist({"D1": 10, "D2": 20})"""
    
    if lockdown:
        return False
    
    if not health_check():
        return False

    if locked_global== 'soft_lock':
        if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARRNING] File is currently soft-locked. Keys cannot be added but existing keys can be edited.")
        return False
    
    if newVarlist.keys() & ignore or newVarlist.keys() & donotEdit:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{newVarlist.keys() & ignore}{newVarlist.keys() & donotEdit}' is a reserved keyword and cannot be used as a variable name.")
        return False
        
    daten = _read()

    daten.update(newVarlist)

    _write(daten)
    
    if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"Update successful: {list(newVarlist.keys())} updated.")
    return True

def delete(name):
    """Permanently deletes a data point from the file and memory."""

    if lockdown:
        return False
    
    if not health_check():
        return False
    
    if locked_global== 'soft_lock':
        if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARRNING] File is currently soft-locked. Keys cannot be added or deleted.")
        return False

    try:
        daten = _read()
        
        if name in daten:
            if name in donotEdit:
                if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{name}' is a reserved keyword and cannot be deleted.")
                return False
            del daten[name]
            _write(daten)
            
            if hasattr(cfg, name): 
                delattr(cfg, name)
                
            if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[INFO] '{name}' deleted successfully.")
            backup ()
            return True
        else:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{name}' does not exist and cannot be deleted.")
            return False
            
    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to delete: {e}")
        return False
    
def get(key, group=None, default=None):
    """Secure data access.
        - I = jsonBib.get("Name", group="group", default="DefaultValue")
        - The Key is the name of the data point to retrieve.
        - The Group (optional) specifies a subgroup within the JSON structure.
        - The DefaultValue (optional) is used if "Name" is not in the config file."""
    
    if lockdown:
        return False
    
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
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] get failed for '{key}': {e}")
        return default
    
def getAll():
    """Returns all data points in the config file as a dictionary."""

    if lockdown:
        return False
    
    health_check()
    backup()
    try:
        data = _read()
        return data
    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] getAll failed: {e}")
        return None

def reset():
    """Restores the config file from the .reset backup."""

    if lockdown:
        return False
    
    if locked_global== 'soft_lock':
        if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARRNING] File is currently soft-locked and cannot be reset.")
        return False

    try:
        if os.path.exists(reset_pfad):
            if os.path.exists(pfad):
                os.remove(pfad)
            os.rename(reset_pfad, pfad)
            setreset()
            load()
            if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print("[INFO] Config has been restored and loaded from .reset!")
            return True
        else:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print("[ERROR] No reset file found. Reset failed.")
            return False
    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to reset configuration: {e}")
        return False
    
def validate(Var, Valmin, Valmax=None):
    """Validates if a variable meets specified conditions.
        - For numerical values, both minimum and maximum can be set.
        - For boolean or None values, only Valmin is required."""
    
    if lockdown:
        return False
    
    if not health_check():
        return False
    
    current_val = get(Var)

    if current_val is None:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] The variable '{Var}' does not exist.")
        return False
    if Valmax is not None and isinstance(Valmax, (bool, str, type(None))):
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print("[ERROR] Valmax must be a number.")
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

    if lockdown:
        return False
    
    if not health_check():
        return False
    
    if locked_global== 'soft_lock':
        if MsgtoCons_global <= 1 or MsgtoCons_global == 5: print("[WARRNING] File is currently soft-locked. Keys cannot be renamed.")
        return False
    
    if new_name in ignore or new_name in donotEdit:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{new_name}' is a reserved keyword and cannot be used as a group name.")
        return False
    elif old_name in ignore or old_name in donotEdit:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] '{old_name}' is a reserved keyword and cannot be changed.")
        return False
    
    try:
        backup()
        daten = _read()

        if new_name in daten:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Group '{new_name}' already exists.")
            return False
        if old_name in daten:
            daten[new_name] = daten.pop(old_name)
            
            _write(daten)
            
            if MsgtoCons_global <= 0 or MsgtoCons_global == 4: print(f"[SUCCESS] Group '{old_name}' renamed to '{new_name}'")
            return True
        else:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Group '{old_name}' not found.")
            return False
            
    except Exception as e:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] {e}")
        return False
    
def compare (Filename1=None,Filename2=None):
    """lets you compare the content of two files.
        if no file name is given the function will compare the 
        set config file and the Config.reset file"""
    
    if lockdown:
        return False
    
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
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Failed to compare files: {e}")
        return False

    if MsgtoCons_global <= 0 and dif: print(f"[INFO] The following keys differ between the two files: {dif}")

    if confjson == resetjson:
        return True
    else:
        return False
    
def create(Filename,contentdir,headir=None,Full_Path=None, indent=None, ensure_ascii=None, dataSaver=None):
    """lets you create a new file."""

    if indent is not None:
        pass
    else:
        indent_global = 4

    if ensure_ascii is not None:
        if ensure_ascii == True:
            pass
        else:
            ensure_ascii = False
    else:
        ensure_ascii = False

    if dataSaver is not None:
        print (f"dataSaver not None: {dataSaver}")
        if dataSaver == True:
            pass
        elif dataSaver == False:
            pass
        else:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Invalid value for 'dataSaver'. Please send a boolean value (True/False).")
            dataSaver_global = None
    
    if Full_Path == True:
        json_path = Filename
    else:
        directory, file_name = os.path.split(pfad)
        json_path = directory + "/" + Filename
    
    headir_base = {
        "_header": {
            "ConfVersion": 1.0,
            "mode": "normal",
            "refresh": True,
            "locked": "unlocked",
            "Print": None,
            "MsgtoCons": 0,
            "last_updated": "2000-01-01 00:00:00"
        }}
    
    if headir is not None:
        data = contentdir | headir
    else:
        data = headir_base | contentdir
    
    if not os.path.exists(json_path):
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Creation Failed. '{e}'")
            return False
    else:
        if MsgtoCons_global <= 2 or MsgtoCons_global == 6: print(f"[ERROR] Creation Failed. File '{Filename}' already exists")
        return False

def rename(Filename_old,Filename_new,Full_Path=None):
    """lets you rename and/ore move files."""

    fileName(filename=Filename_old,Full_Path=Full_Path)
    data = _read()

    create(Filename=Filename_new,contentdir=data,Full_Path=Full_Path)
    if Full_Path == True:
        json_path = Filename_old
    else:
        directory, file_name = os.path.split(pfad)
        json_path = directory + "/" + Filename_old
    if os.path.exists(Filename_new):
        if os.path.exists(json_path):
                os.remove(json_path)