==========  JSON LIBRARY - README (v2.1)  ==========

DESCRIPTION:
This library enables easy management of configuration files in Python. 
JSON data can be loaded directly into a class (cfg.) for easy access. 
The file is automatically saved when changes are made, and backups and reset points can be created.

------------------------------------------------------------
MAIN FEATURES
------------------------------------------------------------
* Auto-Load:    Import keys as a class for easy access.
* Self-Healing: Automatic repair via .bak files.
* Editor:       Change values interactively in the terminal.
* Security:     Automatic backup before every write operation.
* Reset:        Enable manual snapshots for config recovery.
* Data Types:   Supports int, float, str, bool, and None.

------------------------------------------------------------
INSTALLATION & START
------------------------------------------------------------
1. Copy the file 'JsonBib.py' into your project directory.
2. Import:       import JsonBib as j
3. Setup:        j.bibconfig(check=True/None,autoLoad=True/None,autoCreate=True/None,Print=True/None,set_reset=True/None,fileName="Filename"/None)
4. Load:         j.load()
5. Info:         j.info()

------------------------------------------------------------
MAIN FUNCTIONS
------------------------------------------------------------
[Functions marked with [X] return 'True' if executed 
    successfully and 'False' upon failure]

1. libconfig(check=True/None,autoLoad=True/None,autoCreate=True/None,Print=True/None,set_reset=True/None,fileName="Filename"/None MsgtoCons=0-3) [X]
   - Configures the library settings.
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

7. editor()
   - Interactive terminal menu for changing values.
      - '/?' shows all keys | 'exit' terminates the mode.

8. edit(Var, Val) [X]
   - Changes an EXISTING value directly via code. 

9. dump(dict) [X]
   - Updates EXISTING values in the JSON. 
      - Prevents accidental creation of new keys.

10. add(Varname, Varvalue) [X]
   - Creates a NEW data point in the JSON file.

11. addlist(dict) [X]
   - Adds multiple NEW data points simultaneously.
      - Example: j.addlist({"D1": 10, "D2": 20})

12. search(Varname) [X]
   - Checks if a variable exists in the config (True/False).

13. delete(name) [X]
   - Permanently deletes a data point from the file and memory.

14. backup() [X]
   - Creates a backup/current state of the config file (Config.json.bak)

15. get(key, group=None, default=None)
   - Secure data access.
      - I = jsonBib.get("Name", group="group", default="DefaultValue")
      - The Key is the name of the data point to retrieve.
      - The Group (optional) specifies a subgroup within the JSON structure.
      - The DefaultValue (optional) is used if "Name" is not in the config file.

16. getAll()
        Returns all data points in the config file as a dictionary.

17. validate(Var, Valmin, Valmax=None) [X]
   - Validates if a variable meets specified conditions.
      - For numerical values, both minimum and maximum can be set.
      - For boolean or None values, only Valmin is required.

18. renameGroup(old_name, new_name) [X]
   - Renames a Group or Key.

19. compare (Filename1=None,Filename2=None) [X]
   - lets you compare the content of two files.
     if no file name is given the function will compare the 
     set config file and the Config.reset file

------------------------------------------------------------
DATA SECURITY (.bak/.reset)
------------------------------------------------------------
The library automatically creates a 'config.json.bak'.
Should the main file become corrupted (e.g., due to errors
during saving), the load() function automatically restores
the last functional state. Additionally, users can manually 
create a dedicated reset point, allowing for a full Config 
recovery to a specifically defined state at any time."

------------------------------------------------------------
CONTROLS
------------------------------------------------------------
- Cancel:    Ctrl+C (inside the editor)
- Null-Values: In Python 'None', type 'None' in the editor.
- Booleans:  Enter 'True' or 'False'.
