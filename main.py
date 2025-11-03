# main_app.py - Enhanced Version
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, simpledialog
import json
import os
from datetime import datetime
from tool_definitions import TOOLS
from command_runner import CommandRunner
from enhanced_features import EnhancedNetworkApp

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Tools Pro v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.iconbitmap('hub.ico')
        
        self.setup_modern_theme()
        
        self.widgets = {}
        self.is_running = False
        self.command_history = []
        self.current_tool = None
        
        self.setup_styles()
        
        self.runner = CommandRunner(
            self.root,
            output_callback=self.append_output,
            finished_callback=self.on_command_finished
        )
        
        self.create_interface()
        self.setup_keyboard_shortcuts()
        self.load_last_tool()

    def setup_modern_theme(self):
        self.colors = {
            'bg_primary': '#1e1e1e', 'bg_secondary': '#2d2d2d', 'bg_tertiary': '#3e3e3e',
            'accent': '#007acc', 'accent_hover': '#1a8cdb', 'success': '#28a745',
            'danger': '#dc3545', 'text_primary': '#ffffff', 'text_secondary': '#cccccc',
            'text_muted': '#999999', 'terminal_bg': '#0c0c0c', 'terminal_fg': '#d3d3d3'
        }
        self.root.configure(bg=self.colors['bg_primary'])

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TNotebook', background=self.colors['bg_primary'], borderwidth=0)
        style.configure('Modern.TNotebook.Tab', background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'], padding=[20, 10], focuscolor='none')
        style.map('Modern.TNotebook.Tab', background=[('selected', self.colors['accent']),
                                                      ('active', self.colors['accent_hover'])])

    def create_interface(self):
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tools_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(self.tools_frame, text="🔧 Herramientas")
        
        self.history_frame = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
        self.notebook.add(self.history_frame, text="📋 Historial")
        
        self.create_tools_tab()
        self.create_history_tab()
        self.create_status_bar()

    def create_tools_tab(self):
        main_pane = tk.PanedWindow(self.tools_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED, bg=self.colors['bg_primary'])
        main_pane.pack(fill=tk.BOTH, expand=True)
        top_frame = tk.Frame(main_pane, bg=self.colors['bg_primary'])
        main_pane.add(top_frame, height=350)
        control_pane = tk.PanedWindow(top_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, bg=self.colors['bg_primary'])
        control_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.create_tool_list(control_pane)
        self.create_tool_details(control_pane)
        self.create_terminal(main_pane)

    def create_tool_list(self, parent):
        tool_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief=tk.RAISED, bd=1)
        header = tk.Frame(tool_frame, bg=self.colors['bg_secondary'])
        header.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(header, text="🔧 Herramientas de Red", font=("Segoe UI", 12, "bold"),
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor="w")
        
        search_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        search_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(search_frame, text="🔍", bg=self.colors['bg_secondary'], fg=self.colors['text_muted']).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=self.colors['bg_tertiary'],
                                   fg=self.colors['text_primary'], relief=tk.FLAT, bd=5)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.search_var.trace('w', self.filter_tools)
        
        list_frame = tk.Frame(tool_frame, bg=self.colors['bg_secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tool_listbox = tk.Listbox(list_frame, exportselection=False, font=("Segoe UI", 11),
                                      bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                                      selectbackground=self.colors['accent'], relief=tk.FLAT, bd=0, highlightthickness=0)
        self.tool_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.populate_tool_list()
        self.tool_listbox.bind("<<ListboxSelect>>", self.on_tool_select)
        parent.add(tool_frame, width=250)

    def create_tool_details(self, parent):
        self.tool_detail_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief=tk.RAISED, bd=1)
        parent.add(self.tool_detail_frame)

    def create_terminal(self, parent):
        terminal_container = tk.Frame(parent, bg=self.colors['terminal_bg'], relief=tk.RAISED, bd=1)
        
        terminal_toolbar = tk.Frame(terminal_container, bg=self.colors['bg_secondary'])
        terminal_toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        tk.Button(terminal_toolbar, text="Limpiar", command=self.clear_output, bg=self.colors['accent'],
                 fg='white', font=("Segoe UI", 8)).pack(side=tk.RIGHT, padx=5)

        self.output_area = scrolledtext.ScrolledText(
            terminal_container, wrap=tk.WORD, state=tk.DISABLED, bg=self.colors['terminal_bg'],
            fg=self.colors['terminal_fg'], font=("Courier New", 10), relief=tk.FLAT, bd=0)
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        parent.add(terminal_container, height=300)

    def create_history_tab(self):
        tk.Label(self.history_frame, text="📋 Historial de Comandos", font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack(pady=10)
        self.history_listbox = tk.Listbox(self.history_frame, bg=self.colors['bg_tertiary'],
                                         fg=self.colors['text_primary'], selectbackground=self.colors['accent'],
                                         font=("Segoe UI", 10))
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=self.colors['bg_tertiary'], relief=tk.SUNKEN, bd=1, height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(self.status_bar, text="✅ Listo", bg=self.colors['bg_tertiary'],
                                   fg=self.colors['text_secondary'], font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        signature_label = tk.Label(self.status_bar, text="Created by: Ez07-Code", bg=self.colors['bg_tertiary'],
                                   fg=self.colors['text_muted'], font=("Segoe UI", 9))
        signature_label.pack(side=tk.RIGHT, padx=10, pady=2)
    
    def populate_tool_list(self):
        self.tool_listbox.delete(0, tk.END)
        search_term = self.search_var.get().lower()
        emoji_map = {
            'PING': '📡', 'TRACERT': '🛤️', 'NSLOOKUP': '🔍', 'NETSTAT': '🌐', 
            'IPCONFIG': '⚙️', 'ARP': '🏷️', 'SCANNER': '🔎', 'SUBNET': '🧮', 
            'WOL': '⚡', 'WHOIS': '🌎'
        }
        for tool_name in TOOLS.keys():
            if not search_term or search_term in tool_name.lower():
                emoji = emoji_map.get(tool_name, '🔧')
                self.tool_listbox.insert(tk.END, f"{emoji} {tool_name}")

    def filter_tools(self, *args):
        self.populate_tool_list()

    def on_tool_select(self, event):
        if self.is_running or not self.tool_listbox.curselection(): return
        selected_text = self.tool_listbox.get(self.tool_listbox.curselection()[0])
        tool_key = selected_text.split(' ', 1)[1]
        self.current_tool = tool_key
        self.update_tool_details(tool_key)
        self.save_last_tool(tool_key)

    def update_tool_details(self, tool_key):
        for widget in self.tool_detail_frame.winfo_children(): widget.destroy()
        self.widgets = {}
        tool_info = TOOLS[tool_key]
        
        tk.Label(self.tool_detail_frame, text=f"🔧 {tool_key}", font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor="w", padx=10, pady=5)
        
        desc_frame = tk.LabelFrame(self.tool_detail_frame, text="📋 Descripción", bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_primary'], font=("Segoe UI", 10, "bold"))
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        desc_text = tk.Text(desc_frame, height=4, wrap=tk.WORD, bg=self.colors['bg_tertiary'],
                           fg=self.colors['text_secondary'], font=("Segoe UI", 9), relief=tk.FLAT, bd=5)
        desc_text.insert('1.0', tool_info["description"])
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X, padx=5, pady=5)

        params_frame = tk.LabelFrame(self.tool_detail_frame, text="⚙️ Parámetros", bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_primary'], font=("Segoe UI", 10, "bold"))
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for param in tool_info["parameters"]:
            param_frame = tk.Frame(params_frame, bg=self.colors['bg_secondary'])
            param_frame.pack(fill=tk.X, padx=5, pady=3)
            label_text = f"{'🔹' if param['required'] else '🔸'} {param['name']}:"
            tk.Label(param_frame, text=label_text, width=25, anchor="e", bg=self.colors['bg_secondary'],
                    fg=self.colors['text_primary'], font=("Segoe UI", 9)).pack(side=tk.LEFT)
            entry = tk.Entry(param_frame, width=40, bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                           relief=tk.FLAT, bd=5)
            if param.get('default'): entry.insert(0, param['default'])
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.widgets[param['name']] = entry
            
        self.create_action_buttons(tool_key)

    def create_action_buttons(self, tool_key):
        action_frame = tk.Frame(self.tool_detail_frame, bg=self.colors['bg_secondary'])
        action_frame.pack(fill=tk.X, padx=10, pady=15)
        self.execute_button = tk.Button(action_frame, text=f"▶️ Ejecutar {tool_key}", command=self.build_and_run_command,
                                       bg=self.colors['success'], fg='white', font=("Segoe UI", 10, "bold"))
        self.execute_button.pack(side=tk.LEFT, padx=5)

    def setup_keyboard_shortcuts(self):
        self.root.bind('<Control-Return>', lambda e: self.build_and_run_command())
        self.root.bind('<F5>', lambda e: self.build_and_run_command())

    def build_and_run_command(self):
        if self.is_running or not self.current_tool: return
        tool_info = TOOLS[self.current_tool]
        
        params = {}
        for param_def in tool_info["parameters"]:
            widget = self.widgets.get(param_def['name'])
            if not widget: continue
            value = widget.get().strip()
            if param_def["required"] and not value:
                messagebox.showerror("Error", f"El parámetro '{param_def['name']}' es obligatorio.")
                return
            params[param_def['arg']] = value

        if tool_info.get("internal"):
            self.execute_command(tool_info["command"], internal=True, params=params)
        else:
            command_list = list(tool_info["command"])
            for param_def in tool_info["parameters"]:
                value = params.get(param_def['arg'])
                if value:
                    if param_def["arg"]: command_list.extend([param_def["arg"], value])
                    else: command_list.extend(value.split())
            self.execute_command(command_list)

    def execute_command(self, command, internal=False, params={}):
        self.is_running = True
        self.set_ui_state(False)
        self.update_status("⏳ Ejecutando...", "warning")
        self.clear_output()
        
        if internal:
            cmd_str = f"{command} with params {params}"
            self.runner.run_command(command, internal=True, params=params)
        else:
            cmd_str = ' '.join(command)
            self.runner.run_command(command)

        self.append_output(f"[{datetime.now().strftime('%H:%M:%S')}]> {cmd_str}\n\n")
        self.add_to_history(cmd_str)

    def on_command_finished(self):
        self.is_running = False
        self.set_ui_state(True)
        self.update_status("✅ Comando completado", "success")

    def set_ui_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        if hasattr(self, 'execute_button'): self.execute_button.config(state=state)
        self.tool_listbox.config(state=state)
        for widget in self.widgets.values(): widget.config(state=state)

    def append_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def clear_output(self):
        if self.is_running: return
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state=tk.DISABLED)

    def add_to_history(self, command):
        self.command_history.insert(0, f"[{datetime.now().strftime('%H:%M')}] {command}")
        if len(self.command_history) > 100: self.command_history.pop()
        self.update_history_display()

    def update_history_display(self):
        self.history_listbox.delete(0, tk.END)
        for entry in self.command_history: self.history_listbox.insert(tk.END, entry)

    def load_last_tool(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    tool = json.load(f).get('last_tool')
                    if tool and tool in TOOLS:
                        for i, item in enumerate(self.tool_listbox.get(0, tk.END)):
                            if tool in item:
                                self.tool_listbox.selection_set(i)
                                self.on_tool_select(None)
                                return
        except: pass
        self.tool_listbox.selection_set(0)
        self.on_tool_select(None)

    def save_last_tool(self, tool_name):
        with open('config.json', 'w') as f: json.dump({'last_tool': tool_name}, f)

    def update_status(self, message, status_type="primary"):
        color_map = {'success': self.colors['success'], 'warning': '#ffc107', 'danger': self.colors['danger']}
        self.status_label.config(text=message, fg=color_map.get(status_type, self.colors['text_secondary']))
        if status_type != 'primary': self.root.after(5000, lambda: self.update_status("✅ Listo"))

if __name__ == "__main__":
    try:
        root = tk.Tk()
        base_app = NetworkApp(root)
        # Inicializa y vincula las características mejoradas
        enhanced_app = EnhancedNetworkApp(base_app)
        
        root.mainloop()
    except Exception as e:
        # Manejo de errores a nivel de aplicación para depuración
        import traceback
        error_msg = f"Ha ocurrido un error fatal:\n\n{traceback.format_exc()}"
        print(error_msg)
        # Intenta mostrar un messagebox si tkinter todavía funciona
        try:
            messagebox.showerror("Error Fatal", error_msg)
        except:
            pass
