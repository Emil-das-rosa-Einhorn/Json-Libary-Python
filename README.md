==========  JSON LIBRARY - README (v3.2)  ==========

DESCRIPTION:
This library enables easy management of configuration files in Python. 
JSON data can be loaded directly into a class (cfg.) for easy access. 
The file is automatically saved when changes are made, and backups and reset points can be created.

------------------------------------------------------------
NEW IN VERSION 3.2
------------------------------------------------------------

**Data Saver Mode:** Minimizes file size by stripping whitespaces to save disk space and bandwidth.

**Downward Compatibility:** Version 3.2 is fully backward compatible down to Version 2.0.

------------------------------------------------------------
MAIN FEATURES
------------------------------------------------------------
**Auto-Load:**    Import keys as a class for easy access.

**Self-Healing:** Automatic repair via .bak files.

**Security:**     Automatic backup before every write operation.

**Reset:**        Enable manual snapshots for config recovery.

**Data Types:**   Supports int, float, str, bool, and None.

**Live Refresh:** Background monitoring for manual file changes.

**Atomic Writes:** Prevents file corruption during crashes or power loss.

**File Locking:** Multi-process safety using cross-platform locking.

**System Header:** Integrated metadata for versioning and state control.

------------------------------------------------------------
INSTALLATION & START
------------------------------------------------------------
1. Copy the file 'JsonBib.py' into your project directory.
2. download and Install Portalocker (https://github.com/wolph/portalocker.git)
3. Import: - import JsonBib as j
4. Setup: - j.libconfig( [...] )
5. Load: - j.load()
6. Info: - j.info()
7. Access: - print(j.cfg.Version)  # Access your data directly

------------------------------------------------------------
FUNCTIONS
------------------------------------------------------------
[Functions marked with [X] return 'True' if executed 
    successfully and 'False' upon failure]

1. libconfig(setup=None,check=None,autoLoad=True,autoCreate=None,Print=None,set_reset=None,filename=None,MsgtoCons = 0,Vers=None,VersHi=None,VersLow=None,mode=None,refresh=None,locked=None, indent=None, ensure_ascii=None, dataSaver=None) [X]
   - Configures the library settings.
      - setup=None/dict: Enables you to send all config variables as a dict
         - dict = {"check":None,"autoLoad":None,"autoCreate":None,"Print":None,"set_reset":None,"filename":"files/config.json","MsgtoCons":0,"Vers":None,"VersHi":None,"VersLow":None,"mode":None,"refresh":None,"locked":None} 
      - check=True/None: Enables/disables config file existence check on initialization.
      - autoLoad=True/None: Enables/disables automatic loading of the config file on initialization
         - This option is True on default
      - autoCreate=True/None: Enables/disables automatic creation of a base config if none exists.
      - Print=True/None: Enables/disables terminal output
      - set_reset=True/None: Enables/disables the ability to set reset points.
      - fileName="Filename"/None: Sets a custom name for the Json file.
      - MsgtoCons=0-3 controls which messages are printed to the console.
          - MsgtoCons=0: All messages are printed.
          - MsgtoCons=1: [WARNING] & [ERROR] are printed.
          - MsgtoCons=2: [ERROR] is printed.
          - MsgtoCons=3: No messages are printed.
          - MsgtoCons="INFO": Only [Info] mesages
          - MsgtoCons="WARNING": Only [WARNING] mesages
          - MsgtoCons="ERROR": Only [ERROR] mesages
      - Vers: Sets a specific version range. If VersHi or VersLow is None, it defines the exact supported config version. 
              If the version does not match, the library enters lockdown mode.
          - Lockdown: Once engaged, no functions can be accessed. This ensures the integrity of both the program and your configuration file.
          - Vers=1.0/None: Sets the exact supported config version.
          - VersHi=1.0/None: Sets the highest supported config version.
          - VersLow=1.0/None: Sets the lowest supported config version.
     - This function reads the header data and sets the options accordingly. 
     - NOTE: Ensure a directory named 'files' exists, or use autoCreate=True in libconfig.

2. filename(filename) [X]
    - Sets the name of the config file.

3. setreset(set_reset=TrueNone) [X]
    - Sets a reset point by creating a .reset backup of the current config file.
      - set_reset=True/None: Enables/disables the ability to set reset points.
    
4. reset() [X]
    - Restores the config file from the .reset backup.
    
5. load(autoCreate=True/None) [X]
    - Loads JSON data into global memory.
      - autoCreate=True: Creates a base config if none exists or restors it form the Backup. If the argument is omitted, no config file is created.
    - Should the config file be corrupted, the function attempts to restore the file from the backup.

6. show(Print=True/None)
    - Returns all loaded variable names as a list. If set to 'True', output is displayed in the terminal.

7. edit(Var, Val) [X]
    - Changes an EXISTING value directly via code. 

8. dump(dict) [X]
    - Updates EXISTING values in the JSON. 
      - Prevents accidental creation of new keys.

9. add(Varname, Varvalue) [X]
    - Creates a NEW data point in the JSON file.

10. addlist(dict) [X]
    - Adds multiple NEW data points simultaneously.
      - Example: j.addlist({"D1": 10, "D2": 20})

11. search(Varname) [X]
    - Checks if a variable exists in the config (True/False).

12. delete(name) [X]
    - Permanently deletes a data point from the file and memory.

13. backup() [X]
    - Creates a backup/current state of the config file (Config.json.bak)

14. get(key, group=None, default=None)
    - Secure data access.
      - I = jsonBib.get("Name", group="group", default="DefaultValue")
      - The Key is the name of the data point to retrieve.
      - The Group (optional) specifies a subgroup within the JSON structure.
      - The DefaultValue (optional) is used if "Name" is not in the config file.

15. getAll()
    - Returns all data points in the config file as a dictionary.

16. validate(Var, Valmin, Valmax=None) [X]
   - Validates if a variable meets specified conditions.
      - For numerical values, both minimum and maximum can be set.
      - For boolean or None values, only Valmin is required.

17. renameGroup(old_name, new_name) [X]
    - Renames a Group or Key.

18. compare (Filename1=None,Filename2=None) [X]
    - lets you compare the content of two files.
     if no file name is given the function will compare the 
     set config file and the Config.reset file

19. scan_keys(daten=None) [X]
    - Checks if a group name or key is on the ignore list.
        - if daten is None, the function checks all keys in the config file and prints a warning for any conflicts.
        - if daten is provided, the function checks only the keys in the provided dictionary and returns 'True' if no conflicts are found or 'False' if conflicts exist.

20. check_refresh(interval=5)

    - Starts a background daemon thread to monitor file integrity.

    - Automatically reloads keys into j.cfg if refresh=True is set in libconfig.

21. check_refresh_toggle(cycle=None)

    - Controls the refresh cycle during runtime without killing the thread.

        - cycle=True: Resumes monitoring.

        - cycle=False: Pauses monitoring (Thread enters idle state).

        - cycle=None: Toggles the current state.

22. versCheck (Vers,VersHi,VersLow):
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

24. rename(Filename_old, Filename_new, Full_Path=None, indent=None, ensure_ascii=None, dataSaver=None)
    - Renames or moves a file.
        - It reads the data from the old file, creates a new file with that data using create(), and subsequently deletes the original file.


------------------------------------------------------------
DATA SECURITY (.bak/.reset)
------------------------------------------------------------
To ensure maximum data integrity, the library uses multiple strategys:

- Atomic Write Operations: Instead of overwriting the config file directly, the library writes to a temporary file first. Only after the data is safely on the disk is the original file replaced (os.replace). This prevents "half-written" or empty files if the program crashes or the power fails.

- Hardware Persistence: Each save operation uses os.fsync() to force the operating system to physically write the data to the storage medium, preventing data loss held in volatile cache.

- File Locking: To prevent race conditions in multi-process environments, the library uses portalocker to lock the file during the write process, ensuring that only one instance can modify the configuration at a time.

- Self-Healing (Auto-Backup): The library automatically maintains a config.json.bak. If the main file becomes corrupted or unreadable, the load() function automatically restores the last known functional state.

- Manual Snapshots: Users can create dedicated .reset points to freeze a specific configuration state, allowing for a full recovery to that defined baseline at any time.

- Protected System Header (_header):
Every config includes a reserved metadata section:
    - ConfVersion: Tracks the configuration schema version.
    - mode: 'normal' or 'safe_mode' (Safe mode enforces auto-recovery).
    - locked: 'unlocked', 'soft_lock' (no new keys), or 'hard_lock' (read-only).