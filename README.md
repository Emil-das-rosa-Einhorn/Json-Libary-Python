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
* Data Types:   Supports int, float, str, bool, and None.

------------------------------------------------------------
INSTALLATION & START
------------------------------------------------------------
1. Copy the file 'JsonBib.py' into your project directory.
2. Import:       import JsonBib as j
3. Setup:        j.bibconfig(autoCreate=True, Print=False)
4. Load:         j.load()

------------------------------------------------------------
MAIN FUNCTIONS
------------------------------------------------------------

[X] = Returns True/False for success status.

1. j.get(Name, DefaultValue)
     - Secure access. Returns the DefaultValue if the
     - Name is missing in the config.

2. j.edit(Variable, Value) [X]
     - Changes an existing value in memory and the file.

3. j.editor()
     - Opens the interactive menu. 
     - Editor commands: '/?' (Show list), 'exit' (Quit).

4. j.add(Name, Value) [X]
     - Creates a completely new data point.

5. addlist(dict) [X]
   - Adds multiple NEW data points simultaneously.
   - Example: j.addlist({"D1": 10, "D2": 20})

6. search(Varname) [X]
   - Checks if a variable exists in the config (True/False).

7. delete(name) [X]
   - Permanently deletes a data point from the file and memory.

8. backup() [X]
    - Creates a backup of the config file (Config.json.bak).

9. j.show(Print=True)
   - Returns a list of all loaded variables.

10. j.info()
   - Displays detailed help directly in the terminal.

------------------------------------------------------------
DATA SECURITY (.bak)
------------------------------------------------------------
The library automatically creates a 'config.json.bak'.
Should the main file become corrupted (e.g., due to errors
during saving), the load() function automatically restores
the last functional state.

------------------------------------------------------------
CONTROLS
------------------------------------------------------------
- Cancel:    Ctrl+C (inside the editor)
- Null-Values: In Python 'None', type 'None' in the editor.
- Booleans:  Enter 'True' or 'False'.