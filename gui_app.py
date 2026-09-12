import sys
import copy
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class TimeTravelDebuggerEngine:
    """Core tracing engine integrated into GUI."""
    def __init__(self):
        self.history = []
        self.target_file = ""

    def run_target(self, filepath):
        self.history.clear()
        self.target_file = filepath
        with open(filepath, 'r') as f:
            code_content = f.read()
            
        compiled_code = compile(code_content, filepath, 'exec')
        
        def _trace_func(frame, event, arg):
            if event == 'line' and frame.f_code.co_filename == self.target_file:
                line_no = frame.f_lineno
                combined_vars = {**frame.f_globals, **frame.f_locals}
                safe_locals = {}
                for k, v in combined_vars.items():
                    if not k.startswith('__') and k not in ('sys', 'copy', 'tk', 'ttk'):
                        try:
                            safe_locals[k] = copy.deepcopy(v)
                        except Exception:
                            safe_locals[k] = repr(v)
                            
                self.history.append({'line': line_no, 'locals': safe_locals})
            return _trace_func

        sys.settrace(_trace_func)
        try:
            exec(compiled_code, {'__name__': '__main__'})
        finally:
            sys.settrace(None)

class DebuggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Time-Travel Debugger (ChronoDebug)")
        self.root.geometry("900x600")
        
        self.engine = TimeTravelDebuggerEngine()
        self.file_lines = []
        self.current_step = 0

        # UI Setup
        self._build_widgets()
        
    def _build_widgets(self):
        # Top toolbar
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="📁 Open File", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="▶️ Run Debugger", command=self.run_debugger).pack(side=tk.LEFT, padx=5)
        
        self.btn_back = ttk.Button(toolbar, text="← Step Back (a / ←)", command=self.step_back, state=tk.DISABLED)
        self.btn_back.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = ttk.Button(toolbar, text="Step Forward (d / →) →", command=self.step_forward, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.lbl_step = ttk.Label(toolbar, text="Step: 0/0", font=("Arial", 10, "bold"))
        self.lbl_step.pack(side=tk.RIGHT, padx=10)

        # Main Paned Window (Left: Code, Right: Variables)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Code View Frame
        code_frame = ttk.Labelframe(paned, text=" Source Code ", padding=5)
        self.code_list = tk.Listbox(code_frame, font=("Consolas", 11), selectbackground="#007acc", selectforeground="white")
        self.code_list.pack(fill=tk.BOTH, expand=True)
        paned.add(code_frame, weight=3)

        # Variables Frame
        vars_frame = ttk.Labelframe(paned, text=" Variable Scope ", padding=5)
        self.vars_table = ttk.Treeview(vars_frame, columns=("Variable", "Value"), show="headings")
        self.vars_table.heading("Variable", text="Variable")
        self.vars_table.heading("Value", text="Value")
        self.vars_table.column("Variable", width=100)
        self.vars_table.column("Value", width=200)
        self.vars_table.pack(fill=tk.BOTH, expand=True)
        paned.add(vars_frame, weight=2)

        # Keyboard Navigation Shortcuts (Letter Keys + Arrow Keys)
        self.root.bind('<a>', lambda e: self.step_back())
        self.root.bind('<Left>', lambda e: self.step_back())
        
        self.root.bind('<d>', lambda e: self.step_forward())
        self.root.bind('<Right>', lambda e: self.step_forward())

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if filepath:
            self.filepath = filepath
            with open(filepath, 'r') as f:
                self.file_lines = f.readlines()
            
            self.code_list.delete(0, tk.END)
            for i, line in enumerate(self.file_lines, 1):
                self.code_list.insert(tk.END, f"{i:3d} | {line.rstrip()}")

    def run_debugger(self):
        if hasattr(self, 'filepath'):
            self.engine.run_target(self.filepath)
            if self.engine.history:
                self.current_step = 0
                self.btn_back.config(state=tk.NORMAL)
                self.btn_next.config(state=tk.NORMAL)
                self.update_ui()
        else:
            messagebox.showwarning("Warning", "Please select a Python file first.")

    def update_ui(self):
        if not self.engine.history:
            return
            
        snap = self.engine.history[self.current_step]
        max_steps = len(self.engine.history)
        
        # Update Step Label
        self.lbl_step.config(text=f"Step: {self.current_step + 1}/{max_steps}")
        
        # Highlight Source Code Line
        self.code_list.selection_clear(0, tk.END)
        line_idx = snap['line'] - 1
        self.code_list.selection_set(line_idx)
        self.code_list.see(line_idx)

        # Update Variables Table
        for row in self.vars_table.get_children():
            self.vars_table.delete(row)
            
        for var, val in sorted(snap['locals'].items()):
            self.vars_table.insert("", tk.END, values=(var, repr(val)))

    def step_back(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.update_ui()

    def step_forward(self):
        if self.current_step < len(self.engine.history) - 1:
            self.current_step += 1
            self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = DebuggerGUI(root)
    root.mainloop()
