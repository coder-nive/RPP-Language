import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import urllib.request
import tempfile
import os


class WindowManager:
    def __init__(self):
        self.windows = {}
        self.button_handlers = {}

    def create(self, name, args=None):
        if name in self.windows:
            return

        created_event = threading.Event()

        def thread_main():
            try:
                root = tk.Tk()
                title = args.get('SetTitle') if args else None
                if title:
                    root.title(title)
                self.windows[name] = {'root': root, 'widgets': {}, 'labels': {}}
                created_event.set()
                root.mainloop()
            except Exception:
                created_event.set()

        thread = threading.Thread(target=thread_main, daemon=False)
        thread.start()
        # wait briefly for the window to be created so subsequent calls can schedule tasks
        created_event.wait(timeout=1.0)
        if name in self.windows:
            # keep reference to thread so caller can wait for it
            self.windows[name]['thread'] = thread

    def size(self, name, value, vars_):
        if name not in self.windows:
            return
        parts = value.split('x')
        w = int(parts[0].strip().strip('"'))
        h = int(parts[1].strip().strip('"'))
        root = self.windows[name].get('root')
        if root:
            root.after(0, lambda: root.geometry(f"{w}x{h}"))

    def text(self, name, value, vars_):
        if name not in self.windows:
            return
        txt = value.strip().strip('"')
        txt = self._interpolate(txt, vars_)
        root = self.windows[name].get('root')
        if not root:
            return
        def create_label():
            lbl = tk.Label(root, text=txt)
            lbl.pack()
        root.after(0, create_label)

    def image(self, name, value, vars_):
        if name not in self.windows:
            return
        url = value.strip().strip('"')
        root = self.windows[name].get('root')
        if not root:
            return
        def do_image():
            try:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(url)[1])
                urllib.request.urlretrieve(url, tmp.name)
                try:
                    img = tk.PhotoImage(file=tmp.name)
                    lbl = tk.Label(root, image=img)
                    lbl.image = img
                    lbl.pack()
                finally:
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass
            except Exception:
                pass
        root.after(0, do_image)

    def input(self, name, value, vars_):
        # show a modal input dialog; tkinter dialogs must run in a Tk instance
        prompt = value.strip().strip('"')
        root = self.windows.get(name, {}).get('root')
        if not root:
            # fallback: use a temporary hidden root
            tmp = tk.Tk()
            tmp.withdraw()
            res = simpledialog.askstring(title='Input', prompt=prompt)
            try:
                tmp.destroy()
            except Exception:
                pass
            return res

        result_holder = {'val': None}
        done = threading.Event()

        def ask():
            result_holder['val'] = simpledialog.askstring(title='Input', prompt=prompt, parent=root)
            done.set()

        root.after(0, ask)
        done.wait()
        return result_holder['val']

    def sendnotification(self, name, value, vars_):
        msg = value.strip().strip('"')
        msg = self._interpolate(msg, vars_)
        root = self.windows.get(name, {}).get('root')
        if root:
            root.after(0, lambda: messagebox.showinfo('Notification', msg, parent=root))
        else:
            messagebox.showinfo('Notification', msg)

    def close(self, name):
        if name in self.windows:
            root = self.windows[name].get('root')
            if root:
                root.after(0, lambda: root.destroy())
            del self.windows[name]

    def button(self, name, value, vars_):
        if name not in self.windows:
            return
        label = value.strip().strip('"')
        root = self.windows[name].get('root')
        if not root:
            return

        def create_btn():
            btn = tk.Button(root, text=label)
            btn.pack()
            def on_click():
                handlers = self.button_handlers.get(label, [])
                for h in handlers:
                    try:
                        h()
                    except Exception:
                        pass
            btn.config(command=on_click)

        root.after(0, create_btn)

    def label(self, name, value, vars_):
        if name not in self.windows:
            return
        text = value.strip().strip('"')
        text = self._interpolate(text, vars_)
        root = self.windows[name].get('root')
        if not root:
            return

        def create_label():
            lbl = tk.Label(root, text=text)
            lbl.pack()
            self.windows[name]['labels'][text] = lbl

        root.after(0, create_label)

    def label_update(self, name, value, vars_):
        if name not in self.windows:
            return
        text = value.strip().strip('"')
        text = self._interpolate(text, vars_)
        root = self.windows[name].get('root')
        if not root:
            return

        def do_update():
            for k,lbl in list(self.windows[name]['labels'].items()):
                lbl.config(text=text)
                break

        root.after(0, do_update)

    def register_button_handler(self, label, handler):
        self.button_handlers.setdefault(label, []).append(handler)

    def register_key_handler(self, key, handler):
        # placeholder for keyboard events
        pass

    def register_mouse_handler(self, handler):
        # placeholder for mouse events
        pass

    def gui_title(self, name, value, vars_):
        if name not in self.windows:
            return
        title = value.strip().strip('"')
        title = self._interpolate(title, vars_)
        root = self.windows[name].get('root')
        if root:
            root.after(0, lambda: root.title(title))

    def gui_textbox(self, name, value, vars_):
        if name not in self.windows:
            return
        placeholder = value.strip().strip('"')
        root = self.windows[name].get('root')
        if not root:
            return
        def create_textbox():
            txtbox = tk.Text(root, height=5, width=40)
            txtbox.pack()
            if placeholder:
                txtbox.insert(tk.END, placeholder)
        root.after(0, create_textbox)

    def gui_checkbox(self, name, value, vars_):
        if name not in self.windows:
            return
        label = value.strip().strip('"')
        root = self.windows[name].get('root')
        if not root:
            return
        def create_checkbox():
            var = tk.BooleanVar()
            cb = tk.Checkbutton(root, text=label, variable=var)
            cb.pack()
            if 'widgets' not in self.windows[name]:
                self.windows[name]['widgets'] = {}
            self.windows[name]['widgets'][label] = var
        root.after(0, create_checkbox)

    def gui_dropdown(self, name, value, vars_):
        if name not in self.windows:
            return
        root = self.windows[name].get('root')
        if not root:
            return
        # parse options from value like "Easy","Medium","Hard"
        opts = [o.strip().strip('"') for o in value.split(',') if o.strip()]
        def create_dropdown():
            from tkinter import ttk
            dd = ttk.Combobox(root, values=opts, state='readonly')
            dd.pack()
            if opts:
                dd.current(0)
            if 'widgets' not in self.windows[name]:
                self.windows[name]['widgets'] = {}
            self.windows[name]['widgets']['dropdown'] = dd
        root.after(0, create_dropdown)

    def gui_progress(self, name, value, vars_):
        if name not in self.windows:
            return

        root = self.windows[name].get('root')
        if not root:
            return
        
        print("Progress value:", value)

        try:
            progress_val = int(float(value))
        except:
            progress_val = 0

        def update_progress():
            from tkinter import ttk

            widgets = self.windows[name].setdefault('widgets', {})

            if 'progress' not in widgets:
                pb = ttk.Progressbar(
                    root,
                    length=300,
                    mode='determinate',
                    maximum=100
                )
                pb.pack()

                widgets['progress'] = pb

            widgets['progress']['value'] = progress_val
            root.update_idletasks()

        root.after(0, update_progress)

    def _interpolate(self, s, vars_):
        # replace {var}
        import re
        def repl(m):
            k = m.group(1)
            return str(vars_.get(k, ''))
        return re.sub(r"\{([^}]+)\}", repl, s)

    def wait_all(self, timeout=None):
        for w in list(self.windows.values()):
            t = w.get('thread')
            if t and t.is_alive():
                try:
                    t.join(timeout)
                except Exception:
                    pass
