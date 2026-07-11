import json
import os
from tkinter import filedialog, Tk
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Label, Input, Tree, TabbedContent, TabPane, Select

class JsonEditorApp(App):
    CSS = """
    Screen { background: $background; }
    .container { height: 1fr; margin: 1; }
    .sidebar { width: 35%; border-right: solid $primary; padding-right: 1; }
    .editor-pane { width: 65%; padding-left: 2; }
    Input, Select { margin-top: 0; margin-bottom: 1; }
    Label { margin-top: 1; text-style: bold; }
    #btn-open { margin-top: 1; margin-bottom: 0; width: 100%; }
    #path-input { margin-bottom: 1; }
    #edit-fields { margin-top: 1; }
    #search-input { margin-bottom: 1; }
    Tree { background: $surface; border: round $accent; height: 1fr; }
    
    .tree-actions { 
        margin-top: 1; 
        height: 3;          /* Fixed height for one row of buttons */
        width: 100%;        /* Uses full width of the sidebar */
    }

    /* Buttons share space flexibly without breaking lines */
    .tree-btn { 
        width: 1fr; 
        min-width: 4;       /* Allows Textual to shrink buttons if needed */
        margin: 0;          /* Remove margins to save space */
        padding: 0;         /* Compact padding */
    }
    
    TabPane { padding: 1; background: $surface-darken-1; }
    .action-btn { margin-top: 1; width: 100%; }

    /* Layout for terminal size warning */
    #warning-screen {
        align: center middle;
        text-align: center;
        background: $error-darken-2;
        color: $text;
        height: 100%;
        width: 100%;
    }
    #warning-title {
        text-style: bold;
        background: $error;
        color: $text;
        padding: 1 2;
        margin-bottom: 1;
    }
    """

    _Type_List = ["INT", "STRING", "FLOAT", "LIST", "BOOLEAN", None]
    _Allow_List = ["RANGE", "LIST", "EXCLUDE", "VALUE", "INT", "STRING", "FLOAT", "BOOLEAN", None]

    def __init__(self):
        super().__init__()
        self.file_path = None
        self.json_data = {}
        self.typemap_data = {}  
        self.current_path = [] 
        self.typemap_exists = False

        # Pre-formatted English quick start guide
        self.welcome_guide = (
            "Welcome to JSON Editor!\n\n"
            "Quick Start Guide:\n"
            "1. Click 'Open JSON File' or type the path manually below it.\n"
            "2. Select any node in the 'JSON Structure' tree to view or edit it.\n"
            "3. Use the '➕ New' and '❌ Delete' buttons to modify the keys.\n"
            "4. If needed, generate or manage validation rules via the 'Typemap' tab."
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Terminal size warning screen
        with Vertical(id="warning-screen") as ws:
            ws.display = False
            yield Label("⚠️ TERMINAL TOO SMALL ⚠️", id="warning-title")
            yield Label("", id="warning-details")
            yield Label("Please resize your terminal window to use this application.")

        # Main layout interface
        with Horizontal(id="main-layout", classes="container") as ml:
            with Vertical(classes="sidebar"):
                yield Button("Open JSON File", id="btn-open", variant="primary")
                # Fallback path input directly below the open button
                yield Input(placeholder="...or type path manually + press Enter", id="path-input")
                
                yield Label("Search:")
                yield Input(placeholder="Filter keys...", id="search-input")
                yield Label("JSON Structure:")
                yield Tree("Root", id="json-tree")
                
                with Horizontal(classes="tree-actions"):
                    yield Button("➕ New", id="btn-add-key", variant="success", classes="tree-btn")
                    yield Button("❌ Delete", id="btn-delete-key", variant="error", classes="tree-btn")
                    yield Button("⚙️ Typemap", id="btn-create-typemap", variant="warning", classes="tree-btn")
            
            with Vertical(classes="editor-pane"):
                yield Label(self.welcome_guide, id="status-msg")
                
                with Vertical(id="edit-fields") as v:
                    v.display = False
                    
                    yield Label("Key Name:")
                    yield Input(id="input-key")
                    
                    with TabbedContent():
                        with TabPane("JSON Value", id="tab-value"):
                            yield Label("Current Value (Leaf nodes only):")
                            yield Input(id="input-value")
                            yield Button("Save Value Changes", id="btn-save-value", variant="success", classes="action-btn")
                        
                        with TabPane("Typemap Rules", id="tab-typemap"):
                            yield Label("Data Type (Type):")
                            type_options = [(str(t) if t is not None else "null", t) for t in self._Type_List]
                            yield Select(type_options, id="tm-type", prompt="Select a type...")
                            
                            yield Label("Validation Mode (Allow):")
                            allow_options = [(str(a) if a is not None else "null", a) for a in self._Allow_List]
                            yield Select(allow_options, id="tm-allow", prompt="Select a mode...")
                            
                            yield Label("Content: e.g. [1, 2, 3] or specific values")
                            yield Input(id="tm-content", placeholder="null")
                            
                            yield Label("Default Value (Def):")
                            yield Input(id="tm-def", placeholder="null")
                            
                            yield Button("Save Typemap Rules", id="btn-save-typemap", variant="warning", classes="action-btn")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#btn-create-typemap").display = False
        self.check_terminal_size()

    def on_resize(self, event) -> None:
        self.check_terminal_size()

    def check_terminal_size(self) -> None:
        min_width = 100
        min_height = 24
        
        current_width = self.size.width
        current_height = self.size.height

        warning_screen = self.query_one("#warning-screen")
        main_layout = self.query_one("#main-layout")

        if current_width < min_width or current_height < min_height:
            main_layout.display = False
            warning_screen.display = True
            self.query_one("#warning-details", Label).update(
                f"Current: {current_width}x{current_height} lines | Required: At least {min_width}x{min_height}"
            )
        else:
            warning_screen.display = False
            main_layout.display = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-open":
            self.open_file_dialog()
        elif event.button.id == "btn-create-typemap":
            self.generate_typemap_file()
        elif event.button.id == "btn-save-value":
            self.save_current_value()
        elif event.button.id == "btn-save-typemap":
            self.save_typemap_fields()
        elif event.button.id == "btn-add-key":
            self.add_new_key_prompt()
        elif event.button.id == "btn-delete-key":
            self.delete_current_key()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "path-input":
            path = event.value.strip()
            if path:
                self.load_json_from_path(path)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input" and self.file_path:
            self.refresh_tree(search_term=event.value)

    def open_file_dialog(self) -> None:
        try:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            file_path = filedialog.askopenfilename(
                title="Select JSON File",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            root.destroy()

            if file_path:
                self.query_one("#path-input", Input).value = file_path
                self.load_json_from_path(file_path)
        except Exception as e:
            self.notify("OS File Dialog failed. Use the text input field below instead!", severity="warning")

    def load_json_from_path(self, file_path: str) -> None:
        """Centralized method to load JSON and Typemap data"""
        if not os.path.exists(file_path):
            self.notify("File does not exist! Please check the path.", severity="error")
            return

        self.file_path = file_path
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.json_data = json.load(f)
            
            typemap_path = f"{file_path}.typemap"
            create_btn = self.query_one("#btn-create-typemap")
            
            if os.path.exists(typemap_path):
                with open(typemap_path, "r", encoding="utf-8") as f_type:
                    self.typemap_data = json.load(f_type)
                self.typemap_exists = True
                create_btn.display = False
                self.notify("Typemap file loaded successfully!", severity="information")
            else:
                self.typemap_data = {}
                self.typemap_exists = False
                create_btn.display = True
                self.notify("No Typemap found. Mode: JSON only.", severity="warning")

            self.query_one("#edit-fields").display = False
            self.current_path = []
            self.query_one("#search-input", Input).value = ""
            self.refresh_tree()
        except Exception as e:
            self.notify(f"Loading error: {e}", severity="error")

    def generate_typemap_file(self) -> None:
        if not self.file_path: return
        
        def extract_keys(data, keys_dict):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k not in keys_dict:
                        keys_dict[k] = {"Type": None, "Allow": None, "Content": None, "Def": None}
                    extract_keys(v, keys_dict)
            elif isinstance(data, list):
                for item in data:
                    extract_keys(item, keys_dict)

        new_typemap = {}
        extract_keys(self.json_data, new_typemap)
        
        self.typemap_data = new_typemap
        self.typemap_exists = True
        
        self.save_files_to_disk()
        
        self.query_one("#btn-create-typemap").display = False
        self.notify(".typemap successfully generated and linked!", severity="success")
        
        if self.current_path:
            self.refresh_current_node_view()

    def refresh_tree(self, search_term: str = "") -> None:
        tree = self.query_one("#json-tree", Tree)
        tree.clear()
        if not self.file_path: return
        
        tree.root.label = os.path.basename(self.file_path)
        tree.root.expand()
        search_term_lower = search_term.lower()

        def add_node_rec(tree_node, data, current_path: list):
            if isinstance(data, dict):
                for key, value in data.items():
                    path_here = current_path + [key]
                    if search_term and search_term_lower not in str(key).lower():
                        if isinstance(value, (dict, list)) and self.has_matching_child(value, search_term_lower): pass
                        else: continue

                    if isinstance(value, dict): display_label = f"📁 {key}"
                    elif isinstance(value, list): display_label = f"📋 {key} []"
                    else: display_label = f"🔑 {key}: {value}"

                    child_node = tree_node.add(display_label, expand=False)
                    child_node.data = {"path": path_here, "is_leaf": not isinstance(value, (dict, list))}
                    add_node_rec(child_node, value, path_here)
            elif isinstance(data, list):
                for index, value in enumerate(data):
                    path_here = current_path + [index]
                    if isinstance(value, dict): display_label = f"📁 [{index}]"
                    elif isinstance(value, list): display_label = f"📋 [{index}] []"
                    else: display_label = f"📄 [{index}]: {value}"

                    child_node = tree_node.add(display_label, expand=False)
                    child_node.data = {"path": path_here, "is_leaf": not isinstance(value, (dict, list))}
                    add_node_rec(child_node, value, path_here)

        add_node_rec(tree.root, self.json_data, [])
        self.query_one("#status-msg", Label).update(f"File loaded: {os.path.basename(self.file_path)}")

    def has_matching_child(self, data, search_term: str) -> bool:
        if isinstance(data, dict):
            for k, v in data.items():
                if search_term in str(k).lower(): return True
                if isinstance(v, (dict, list)) and self.has_matching_child(v, search_term): return True
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)) and self.has_matching_child(item, search_term): return True
        return False

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        if not node.data or "path" not in node.data:
            self.current_path = []
            self.query_one("#edit-fields").display = False
            self.query_one("#status-msg", Label).update("Root directory selected (Ready to add items)")
            return

        self.current_path = node.data["path"]
        self.refresh_current_node_view()

    def refresh_current_node_view(self) -> None:
        if not self.current_path: return
        
        tree = self.query_one("#json-tree", Tree)
        val = self.get_value_by_path(self.current_path)
        is_leaf = not isinstance(val, (dict, list))
        current_key = self.current_path[-1]

        path_str = " -> ".join(str(p) for p in self.current_path)
        self.query_one("#status-msg", Label).update(f"Path: {path_str}")
        self.query_one("#edit-fields").display = True

        input_key = self.query_one("#input-key", Input)
        input_key.value = str(current_key)
        input_key.disabled = isinstance(current_key, int)

        input_value = self.query_one("#input-value", Input)
        if is_leaf:
            input_value.value = str(val)
            input_value.disabled = False
        else:
            input_value.value = "[Nested Object / List]"
            input_value.disabled = True

        if self.typemap_exists:
            key_str = str(current_key)
            tm_info = self.typemap_data.get(key_str, {})
            self.query_one("#tm-type", Select).value = tm_info.get("Type")
            self.query_one("#tm-allow", Select).value = tm_info.get("Allow")

            def to_field_str(v):
                if v is None: return "null"
                if isinstance(v, (dict, list)): return json.dumps(v, ensure_ascii=False)
                if isinstance(v, bool): return "true" if v else "false"
                return str(v)

            self.query_one("#tm-content", Input).value = to_field_str(tm_info.get("Content"))
            self.query_one("#tm-def", Input).value = to_field_str(tm_info.get("Def"))

    def get_value_by_path(self, path):
        current = self.json_data
        for part in path: current = current[part]
        return current

    def add_new_key_prompt(self) -> None:
        if not self.file_path:
            self.notify("Please open a JSON file first!", severity="error")
            return

        from tkinter import simpledialog
        try:
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            new_key = simpledialog.askstring("New Key", "Enter the name for the new key:")
            root.destroy()
        except Exception:
            self.notify("Dialog failed. CLI fallback input not implemented.", severity="error")
            return

        if not new_key: return
        new_key = new_key.strip()

        if not self.current_path:
            target_container = self.json_data
        else:
            current_target = self.get_value_by_path(self.current_path)
            if isinstance(current_target, (dict, list)):
                target_container = current_target
            else:
                parent_path = self.current_path[:-1]
                target_container = self.json_data if not parent_path else self.get_value_by_path(parent_path)

        if isinstance(target_container, dict):
            if new_key in target_container:
                self.notify("Key already exists at this position!", severity="error")
                return
            target_container[new_key] = ""
        elif isinstance(target_container, list):
            target_container.append(new_key)

        if self.typemap_exists and new_key not in self.typemap_data:
            self.typemap_data[new_key] = {
                "Type": None,
                "Allow": None,
                "Content": None,
                "Def": None
            }

        self.save_files_to_disk()
        self.notify(f"Key '{new_key}' successfully added!", severity="information")

    def delete_current_key(self) -> None:
        if not self.file_path or not self.current_path:
            self.notify("Please select a key from the tree view first!", severity="error")
            return

        target_key = self.current_path[-1]
        parent_path = self.current_path[:-1]

        if not parent_path:
            if isinstance(self.json_data, dict): del self.json_data[target_key]
            elif isinstance(self.json_data, list) and isinstance(target_key, int): self.json_data.pop(target_key)
        else:
            parent_obj = self.get_value_by_path(parent_path)
            if isinstance(parent_obj, dict): del parent_obj[target_key]
            elif isinstance(parent_obj, list) and isinstance(target_key, int): parent_obj.pop(target_key)

        key_str = str(target_key)
        if self.typemap_exists and key_str in self.typemap_data:
            del self.typemap_data[key_str]

        self.current_path = []
        self.query_one("#edit-fields").display = False
        
        self.save_files_to_disk()
        self.notify(f"Entry '{key_str}' deleted!", severity="warning")

    def parse_smart_value(self, text: str):
        val_clean = text.strip()
        if val_clean.lower() in ("none", "null", ""): return None
        if val_clean.lower() == "true": return True
        if val_clean.lower() == "false": return False
        
        if val_clean.startswith("[") or val_clean.startswith("{"):
            try: return json.loads(val_clean)
            except json.JSONDecodeError: pass

        try:
            if "." not in val_clean: return int(val_clean)
            return float(val_clean)
        except ValueError:
            if (val_clean.startswith('"') and val_clean.endswith('"')) or (val_clean.startswith("'") and val_clean.endswith("'")):
                return val_clean[1:-1]
            return text

    def handle_key_rename(self, target_key, new_key_text, parent_obj) -> bool:
        if str(target_key) == new_key_text or isinstance(target_key, int): return False
        if not new_key_text:
            self.notify("Key name cannot be empty!", severity="error")
            return False

        new_dict = {}
        for k, v in parent_obj.items():
            if k == target_key: new_dict[new_key_text] = v
            else: new_dict[k] = v
        
        parent_path = self.current_path[:-1]
        if not parent_path: self.json_data = new_dict
        else:
            grandparent = self.get_value_by_path(parent_path[:-1]) if parent_path[:-1] else self.json_data
            grandparent[parent_path[-1]] = new_dict

        old_key_str = str(target_key)
        if self.typemap_exists and old_key_str in self.typemap_data:
            new_tm = {}
            for k, v in self.typemap_data.items():
                if k == old_key_str: new_tm[new_key_text] = v
                else: new_tm[k] = v
            self.typemap_data = new_tm

        self.current_path[-1] = new_key_text
        return True

    def save_current_value(self) -> None:
        if not self.current_path or not self.file_path: return

        new_key_text = self.query_one("#input-key", Input).value.strip()
        new_value_text = self.query_one("#input-value", Input).value

        val = self.get_value_by_path(self.current_path)
        is_leaf = not isinstance(val, (dict, list))
        parent_path = self.current_path[:-1]
        target_key = self.current_path[-1]
        parent_obj = self.json_data if not parent_path else self.get_value_by_path(parent_path)

        if is_leaf and not isinstance(target_key, int):
            parent_obj[target_key] = self.parse_smart_value(new_value_text)

        self.handle_key_rename(target_key, new_key_text, parent_obj)
        self.save_files_to_disk()

    def save_typemap_fields(self) -> None:
        if not self.current_path or not self.file_path: return
        if not self.typemap_exists:
            self.notify("No .typemap file exists for this JSON file!", severity="error")
            return

        new_key_text = self.query_one("#input-key", Input).value.strip()
        parent_path = self.current_path[:-1]
        target_key = self.current_path[-1]
        parent_obj = self.json_data if not parent_path else self.get_value_by_path(parent_path)

        self.handle_key_rename(target_key, new_key_text, parent_obj)
        key_str = str(self.current_path[-1])
        
        if isinstance(target_key, int):
            self.notify("Typemap rules cannot be defined for list indexes.", severity="error")
            return

        selected_type = self.query_one("#tm-type", Select).value
        selected_allow = self.query_one("#tm-allow", Select).value

        if selected_type == Select.BLANK: selected_type = None
        if selected_allow == Select.BLANK: selected_allow = None

        tm_entry = {
            "Type": selected_type,
            "Allow": selected_allow,
            "Content": self.parse_smart_value(self.query_one("#tm-content", Input).value),
            "Def": self.parse_smart_value(self.query_one("#tm-def", Input).value)
        }

        self.typemap_data[key_str] = tm_entry
        self.save_files_to_disk()

    def save_files_to_disk(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.json_data, f, indent=4, ensure_ascii=False)
            
            if self.typemap_exists:
                typemap_path = f"{self.file_path}.typemap"
                with open(typemap_path, "w", encoding="utf-8") as f_tm:
                    json.dump(self.typemap_data, f_tm, indent=4, ensure_ascii=False)

            self.notify("Changes saved successfully!", severity="information")
            current_search = self.query_one("#search-input", Input).value
            self.refresh_tree(search_term=current_search)
        except Exception as e:
            self.notify(f"Error while saving: {e}", severity="error")

if __name__ == "__main__":
    JsonEditorApp().run()