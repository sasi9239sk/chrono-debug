# ChronoDebug — Python Time-Travel Debugger ([C-01] CODE TIME MACHINE)

ChronoDebug is a deterministic reverse-debugging tool for Python inspired by tools like `rr`. It records scope execution frame-by-frame at every line, allowing developers to step backward and forward in time to inspect past variable states without re-running execution.

---

## 🏗️ Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                          Target Python Script                           |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  1. Runtime Interception (sys.settrace)                 |
|            Hooks line events dynamically during script execution         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                    2. Scope Capture & Merging Engine                    |
|                Merges local & module scopes: {**globals, **locals}      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                   3. Object Safety & State Serialization                |
|           Performs copy.deepcopy(); falls back safely to repr()          |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                     4. Timeline Replay Buffer                           |
|           Stores array of immutable frame snapshots sequentially        |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                     5. Synchronized UI Rendering                        |
|        - Native Tkinter Desktop Application                             |
+-------------------------------------------------------------------------+
