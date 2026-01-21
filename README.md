==========  JSON LIBRARY - README (v2.1)  ==========

DESCRIPTION:
This library enables easy management of configuration 
files in Python. JSON data is loaded directly into 
global variables and automatically saved when changes 
are made.

------------------------------------------------------------
MAIN FEATURES
------------------------------------------------------------
* Auto-Load:    JSON keys become Python variables.
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
3. Setup:        j.bibconfig(autoCreate=True/None, Print=True/None, set_reset=True/None)
4. Load:         j.load()
5. Info:         j.info()

------------------------------------------------------------
MAIN FUNCTIONS
------------------------------------------------------------
[Functions marked with [X] return 'True' if executed 
    successfully and 'False' upon failure]

1. libconfig(check=True/None,autoLoad=True/None,autoCreate=True/None,Print=True/None,set_reset=True/None) [X]
   - Configures the library settings.
      - check=True/None: Enables/disables config file existence check on initialization.
      - autoLoad=True/None: Enables/disables automatic loading of the config file on initialization
      - autoCreate=True/None: Enables/disables automatic creation of a base config if none exists.
      - Print=True/None: Enables/disables terminal output
      - set_reset=True/None: Enables/disables the ability to set reset points.

2. setreset(set_reset=TrueNone) [X]
   - Sets a reset point by creating a .reset backup of the current config file.
      - set_reset=True/None: Enables/disables the ability to set reset points.
    
3. reset() [X]
   - Restores the config file from the .reset backup.
    
4. load(autoCreate=True/None) [X]
   - Loads JSON data into global memory.
      - autoCreate=True: Creates a base config if none exists or restors it form the Backup. If the argument is omitted, no config file is created.
   - Should the config file be corrupted, the function attempts to restore the file from the backup.

5. show(Print=True/None)
   - Returns all loaded variable names as a list. If set to 'True', output is displayed in the terminal.

6. editor()
   - Interactive terminal menu for changing values.
      - '/?' shows all keys | 'exit' terminates the mode.

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

14. get(Var, DefaultValue)
   - Secure data access.
      - I = jsonBib.get("Name", DefaultValue)
      - The DefaultValue (optional) is used if "Name" is not in the config file.

15. validate(Var, Valmin, Valmax=None) [X]
   - Validates if a variable meets specified conditions.
      - For numerical values, both minimum and maximum can be set.
      - For boolean or None values, only Valmin is required.

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