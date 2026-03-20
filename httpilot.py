"""
HTTPilot - Cliente HTTP com pastas, salvamento e autenticação
Requisitos: pip install requests cryptography
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import json
import os
import requests
import base64
import hashlib
import hmac
import time
import threading
import urllib.parse
import copy

DATA_DIR = os.path.join(os.path.expanduser("~"), ".httpilot")
COLLECTIONS_FILE = os.path.join(DATA_DIR, "collections.json")


class HTTPilot:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 PyPostman")
        self.root.geometry("1360x860")
        self.root.configure(bg="#1e1e2e")
        self.root.minsize(1100, 700)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.colors = {
            "bg": "#1e1e2e", "bg2": "#181825", "surface": "#313244",
            "overlay": "#45475a", "fg": "#cdd6f4", "subtle": "#a6adc8",
            "accent": "#89b4fa", "green": "#a6e3a1", "red": "#f38ba8",
            "yellow": "#f9e2af", "peach": "#fab387", "mauve": "#cba6f7",
            "teal": "#94e2d5", "btn_fg": "#1e1e2e",
        }
        self._configure_styles()

        self.collections = {}  # {folder_name: {req_name: {...config}}}
        self._load_collections()

        self._build_ui()
        self._refresh_tree()

    # ── Estilos ──────────────────────────────────────────────
    def _configure_styles(self):
        c = self.colors
        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("Sidebar.TFrame", background=c["bg2"])
        self.style.configure("TLabel", background=c["bg"], foreground=c["fg"], font=("Segoe UI", 10))
        self.style.configure("Sidebar.TLabel", background=c["bg2"], foreground=c["fg"], font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=c["bg2"], foreground=c["accent"],
                             font=("Segoe UI", 13, "bold"))
        self.style.configure("Status.TLabel", background=c["bg"], foreground=c["green"],
                             font=("Consolas", 10, "bold"))
        self.style.configure("TNotebook", background=c["bg"])
        self.style.configure("TNotebook.Tab", background=c["surface"], foreground=c["fg"],
                             padding=[14, 6], font=("Segoe UI", 9, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", c["accent"])],
                       foreground=[("selected", c["btn_fg"])])
        self.style.configure("Send.TButton", background=c["accent"], foreground=c["btn_fg"],
                             font=("Segoe UI", 11, "bold"), padding=[18, 7])
        self.style.map("Send.TButton", background=[("active", "#74c7ec")])
        self.style.configure("Save.TButton", background=c["green"], foreground=c["btn_fg"],
                             font=("Segoe UI", 10, "bold"), padding=[14, 6])
        self.style.map("Save.TButton", background=[("active", "#80d89a")])
        self.style.configure("Side.TButton", background=c["overlay"], foreground=c["fg"],
                             font=("Segoe UI", 9), padding=[8, 4])
        self.style.map("Side.TButton", background=[("active", c["surface"])])
        self.style.configure("Small.TButton", background=c["overlay"], foreground=c["fg"],
                             font=("Segoe UI", 9), padding=[10, 4])
        self.style.map("Small.TButton", background=[("active", "#585b70")])
        self.style.configure("Danger.TButton", background=c["red"], foreground=c["btn_fg"],
                             font=("Segoe UI", 9), padding=[8, 4])
        self.style.map("Danger.TButton", background=[("active", "#e06080")])
        self.style.configure("TCombobox", fieldbackground=c["surface"], background=c["surface"],
                             foreground=c["fg"], font=("Consolas", 11))
        self.style.configure("TEntry", fieldbackground=c["surface"], foreground=c["fg"],
                             font=("Consolas", 11))

    def _make_text(self, parent, h=10):
        c = self.colors
        return scrolledtext.ScrolledText(
            parent, height=h, bg=c["surface"], fg=c["fg"],
            insertbackground=c["fg"], font=("Consolas", 10),
            relief="flat", bd=0, wrap="word")

    # ── Persistência ─────────────────────────────────────────
    def _load_collections(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(COLLECTIONS_FILE):
            try:
                with open(COLLECTIONS_FILE, "r", encoding="utf-8") as f:
                    self.collections = json.load(f)
            except Exception:
                self.collections = {}
        else:
            # Coleção de exemplo
            self.collections = {
                "Fornecedor/Company": {
                    "Dados do Cliente": {
                        "method": "POST",
                        "url": "https://api.empresa.com/v1/clientes",
                        "params": "",
                        "headers": "Content-Type: application/json\nAccept: application/json",
                        "body_type": "json",
                        "body": json.dumps({
                            "usuario": "admin@empresa.com",
                            "senha": "sua_senha_aqui",
                            "cliente_id": "12345",
                            "campos": ["nome", "email", "telefone", "endereco"]
                        }, indent=2, ensure_ascii=False),
                        "auth_type": "bearer",
                        "auth_data": {"token": "seu_token_jwt_aqui"}
                    },
                    "Login API": {
                        "method": "POST",
                        "url": "https://api.empresa.com/v1/auth/login",
                        "params": "",
                        "headers": "Content-Type: application/json",
                        "body_type": "json",
                        "body": json.dumps({
                            "usuario": "admin@empresa.com",
                            "senha": "sua_senha_aqui"
                        }, indent=2, ensure_ascii=False),
                        "auth_type": "none",
                        "auth_data": {}
                    }
                }
            }
            self._save_collections()

    def _save_collections(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(COLLECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.collections, f, indent=2, ensure_ascii=False)

    # ── Interface principal ──────────────────────────────────
    def _build_ui(self):
        main_pw = tk.PanedWindow(self.root, orient="horizontal", bg=self.colors["bg"],
                                 sashwidth=4, sashrelief="flat")
        main_pw.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ttk.Frame(main_pw, style="Sidebar.TFrame", width=300)
        main_pw.add(sidebar, minsize=250, width=300)
        self._build_sidebar(sidebar)

        # Área principal
        main_area = ttk.Frame(main_pw)
        main_pw.add(main_area, minsize=600)
        self._build_main_area(main_area)

    # ── Sidebar ──────────────────────────────────────────────
    def _build_sidebar(self, parent):
        c = self.colors

        # Header
        hdr = ttk.Frame(parent, style="Sidebar.TFrame")
        hdr.pack(fill="x", padx=10, pady=(12, 6))
        ttk.Label(hdr, text="📁 Coleções", style="Title.TLabel").pack(side="left")

        # Botões
        btn_bar = ttk.Frame(parent, style="Sidebar.TFrame")
        btn_bar.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Button(btn_bar, text="+ Pasta", style="Side.TButton",
                   command=self._new_folder).pack(side="left", padx=(0, 4))
        ttk.Button(btn_bar, text="+ Request", style="Side.TButton",
                   command=self._new_request).pack(side="left", padx=(0, 4))
        ttk.Button(btn_bar, text="🗑", style="Danger.TButton",
                   command=self._delete_selected).pack(side="right")

        # Treeview
        tree_frame = ttk.Frame(parent, style="Sidebar.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True)

        # Estilo do Treeview
        self.tree.configure(style="Sidebar.Treeview")
        self.style.configure("Sidebar.Treeview",
                             background=c["bg2"], foreground=c["fg"], fieldbackground=c["bg2"],
                             font=("Segoe UI", 10), rowheight=28, borderwidth=0)
        self.style.map("Sidebar.Treeview",
                       background=[("selected", c["surface"])],
                       foreground=[("selected", c["accent"])])
        self.style.configure("Sidebar.Treeview.Heading", background=c["bg2"])

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)

        # Importar / Exportar
        io_bar = ttk.Frame(parent, style="Sidebar.TFrame")
        io_bar.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(io_bar, text="📤 Exportar", style="Side.TButton",
                   command=self._export_collections).pack(side="left", padx=(0, 4))
        ttk.Button(io_bar, text="📥 Importar", style="Side.TButton",
                   command=self._import_collections).pack(side="left")

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for folder, reqs in sorted(self.collections.items()):
            method_counts = {}
            for r in reqs.values():
                m = r.get("method", "GET")
                method_counts[m] = method_counts.get(m, 0) + 1
            folder_id = self.tree.insert("", "end", text=f"📁 {folder}",
                                         values=("folder", folder), open=True)
            for req_name in sorted(reqs.keys()):
                req = reqs[req_name]
                method = req.get("method", "GET")
                colors_map = {
                    "GET": "🟢", "POST": "🟡", "PUT": "🔵",
                    "PATCH": "🟠", "DELETE": "🔴", "HEAD": "⚪", "OPTIONS": "⚫"
                }
                icon = colors_map.get(method, "⚪")
                self.tree.insert(folder_id, "end",
                                 text=f"  {icon} {method}  {req_name}",
                                 values=("request", folder, req_name))

    # ── Área principal ───────────────────────────────────────
    def _build_main_area(self, parent):
        # Header
        hdr = ttk.Frame(parent)
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        ttk.Label(hdr, text="🚀 PyPostman", style="Title.TLabel",
                  background=self.colors["bg"]).pack(side="left")
        self.status_label = ttk.Label(hdr, text="Pronto", style="Status.TLabel")
        self.status_label.pack(side="right")
        self.current_label = ttk.Label(hdr, text="", foreground=self.colors["subtle"],
                                       font=("Segoe UI", 9))
        self.current_label.pack(side="right", padx=16)

        # Barra de requisição
        req_bar = ttk.Frame(parent)
        req_bar.pack(fill="x", padx=16, pady=8)

        self.method_var = tk.StringVar(value="GET")
        ttk.Combobox(req_bar, textvariable=self.method_var, width=9,
                     values=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
                     state="readonly").pack(side="left", padx=(0, 6))

        self.url_var = tk.StringVar(value="https://httpbin.org/get")
        ttk.Entry(req_bar, textvariable=self.url_var).pack(
            side="left", fill="x", expand=True, padx=(0, 6), ipady=4)

        ttk.Button(req_bar, text="▶  Enviar", style="Send.TButton",
                   command=self._send_request).pack(side="left", padx=(0, 6))
        ttk.Button(req_bar, text="💾 Salvar", style="Save.TButton",
                   command=self._save_current_request).pack(side="left")

        # Notebook
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=16, pady=(4, 4))

        # Params
        frm_p = ttk.Frame(nb)
        nb.add(frm_p, text="  Params  ")
        self.params_text = self._make_text(frm_p, h=5)
        self.params_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.params_text.insert("1.0", "# chave=valor (uma por linha)\n# page=1\n# limit=10")

        # Headers
        frm_h = ttk.Frame(nb)
        nb.add(frm_h, text="  Headers  ")
        self.headers_text = self._make_text(frm_h, h=5)
        self.headers_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.headers_text.insert("1.0", "# Chave: Valor\n# Content-Type: application/json")

        # Body
        frm_b = ttk.Frame(nb)
        nb.add(frm_b, text="  Body  ")
        body_top = ttk.Frame(frm_b)
        body_top.pack(fill="x", padx=8, pady=(8, 4))
        self.body_type_var = tk.StringVar(value="json")
        for txt, val in [("JSON", "json"), ("Form Data", "form"), ("Raw", "raw"), ("Nenhum", "none")]:
            ttk.Radiobutton(body_top, text=txt, variable=self.body_type_var, value=val).pack(side="left", padx=6)
        self.body_text = self._make_text(frm_b, h=7)
        self.body_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.body_text.insert("1.0", '{\n  "nome": "exemplo",\n  "valor": 123\n}')

        # Auth
        frm_a = ttk.Frame(nb)
        nb.add(frm_a, text="  Auth  ")
        self._build_auth_tab(frm_a)

        # ── Resposta ─────────────────────────────────────────
        resp_frame = ttk.Frame(parent)
        resp_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        resp_bar = ttk.Frame(resp_frame)
        resp_bar.pack(fill="x", pady=(0, 4))
        ttk.Label(resp_bar, text="Resposta", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.resp_info = ttk.Label(resp_bar, text="", style="Status.TLabel")
        self.resp_info.pack(side="left", padx=12)
        btn_r = ttk.Frame(resp_bar)
        btn_r.pack(side="right")
        ttk.Button(btn_r, text="Copiar", style="Small.TButton",
                   command=self._copy_response).pack(side="left", padx=2)
        ttk.Button(btn_r, text="Salvar Arquivo", style="Small.TButton",
                   command=self._save_response_file).pack(side="left", padx=2)
        ttk.Button(btn_r, text="Limpar", style="Small.TButton",
                   command=self._clear_response).pack(side="left", padx=2)

        self.resp_nb = ttk.Notebook(resp_frame)
        self.resp_nb.pack(fill="both", expand=True)

        frm_rb = ttk.Frame(self.resp_nb)
        self.resp_nb.add(frm_rb, text="  Body  ")
        self.response_text = self._make_text(frm_rb, h=10)
        self.response_text.pack(fill="both", expand=True, padx=4, pady=4)

        frm_rh = ttk.Frame(self.resp_nb)
        self.resp_nb.add(frm_rh, text="  Headers  ")
        self.resp_headers_text = self._make_text(frm_rh, h=10)
        self.resp_headers_text.pack(fill="both", expand=True, padx=4, pady=4)

    # ── Auth Tab ─────────────────────────────────────────────
    def _build_auth_tab(self, parent):
        top = ttk.Frame(parent)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Tipo:").pack(side="left")
        self.auth_type_var = tk.StringVar(value="none")
        cb = ttk.Combobox(top, textvariable=self.auth_type_var, width=22, state="readonly",
                          values=["none", "basic", "bearer", "api_key", "digest", "hmac_sha256"])
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", self._on_auth_change)
        self.auth_container = ttk.Frame(parent)
        self.auth_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.auth_widgets = {}
        self._on_auth_change(None)

    def _clear_auth_container(self):
        for w in self.auth_container.winfo_children():
            w.destroy()
        self.auth_widgets.clear()

    def _add_auth_field(self, label, key, show=None, default=""):
        f = ttk.Frame(self.auth_container)
        f.pack(fill="x", pady=4)
        ttk.Label(f, text=label, width=20, anchor="e").pack(side="left", padx=(0, 8))
        var = tk.StringVar(value=default)
        kw = dict(textvariable=var, style="TEntry")
        if show:
            kw["show"] = show
        ttk.Entry(f, **kw).pack(side="left", fill="x", expand=True, ipady=3)
        self.auth_widgets[key] = var

    def _on_auth_change(self, _event):
        self._clear_auth_container()
        t = self.auth_type_var.get()
        if t == "basic":
            self._add_auth_field("Usuário:", "username")
            self._add_auth_field("Senha:", "password", show="•")
        elif t == "bearer":
            self._add_auth_field("Token:", "token", show="•")
        elif t == "api_key":
            self._add_auth_field("Nome da Chave:", "key_name")
            self._add_auth_field("Valor:", "key_value", show="•")
            f = ttk.Frame(self.auth_container)
            f.pack(fill="x", pady=4)
            ttk.Label(f, text="Adicionar em:", width=20, anchor="e").pack(side="left", padx=(0, 8))
            self.auth_widgets["key_in"] = tk.StringVar(value="header")
            ttk.Combobox(f, textvariable=self.auth_widgets["key_in"], width=18,
                         values=["header", "query"], state="readonly").pack(side="left")
        elif t == "digest":
            self._add_auth_field("Usuário:", "username")
            self._add_auth_field("Senha:", "password", show="•")
        elif t == "hmac_sha256":
            self._add_auth_field("Secret Key:", "secret", show="•")
            self._add_auth_field("Header Name:", "header_name")

    def _get_auth_data(self):
        data = {}
        for key, var in self.auth_widgets.items():
            data[key] = var.get() if isinstance(var, tk.StringVar) else str(var)
        return data

    def _set_auth_data(self, auth_type, auth_data):
        self.auth_type_var.set(auth_type)
        self._on_auth_change(None)
        for key, val in auth_data.items():
            if key in self.auth_widgets:
                self.auth_widgets[key].set(val)

    # ── Coleções: CRUD ───────────────────────────────────────
    def _new_folder(self):
        name = simpledialog.askstring("Nova Pasta", "Nome da pasta (ex: Fornecedor/Company):",
                                      parent=self.root)
        if name and name.strip():
            name = name.strip()
            if name not in self.collections:
                self.collections[name] = {}
                self._save_collections()
                self._refresh_tree()

    def _new_request(self):
        folders = list(self.collections.keys())
        if not folders:
            messagebox.showwarning("Aviso", "Crie uma pasta primeiro.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Request")
        dialog.geometry("420x200")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Pasta:").pack(anchor="w", padx=20, pady=(16, 4))
        folder_var = tk.StringVar(value=folders[0])

        # Pré-seleciona pasta se uma estiver selecionada na tree
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            if vals and len(vals) >= 2:
                folder_var.set(vals[1])

        ttk.Combobox(dialog, textvariable=folder_var, values=folders,
                     state="readonly", width=40).pack(padx=20, pady=(0, 8))
        ttk.Label(dialog, text="Nome do Request:").pack(anchor="w", padx=20, pady=(4, 4))
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=42).pack(padx=20, ipady=3)

        def confirm():
            n = name_var.get().strip()
            fld = folder_var.get()
            if n and fld:
                if fld not in self.collections:
                    self.collections[fld] = {}
                self.collections[fld][n] = self._capture_current_state()
                self._save_collections()
                self._refresh_tree()
                self.current_label.configure(text=f"📌 {fld} / {n}")
                dialog.destroy()

        ttk.Button(dialog, text="✓ Criar", style="Save.TButton", command=confirm).pack(pady=16)

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return

        if vals[0] == "folder":
            folder = vals[1]
            if messagebox.askyesno("Confirmar",
                                   f'Excluir pasta "{folder}" e todos os requests?'):
                del self.collections[folder]
                self._save_collections()
                self._refresh_tree()
        elif vals[0] == "request":
            folder, req_name = vals[1], vals[2]
            if messagebox.askyesno("Confirmar", f'Excluir request "{req_name}"?'):
                del self.collections[folder][req_name]
                self._save_collections()
                self._refresh_tree()

    def _on_tree_select(self, _event):
        pass  # single click não carrega (evita acidentais)

    def _on_tree_double_click(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals or vals[0] != "request":
            return
        folder, req_name = vals[1], vals[2]
        req = self.collections.get(folder, {}).get(req_name)
        if req:
            self._load_request(req)
            self.current_label.configure(text=f"📌 {folder} / {req_name}")

    def _capture_current_state(self):
        return {
            "method": self.method_var.get(),
            "url": self.url_var.get(),
            "params": self.params_text.get("1.0", "end").strip(),
            "headers": self.headers_text.get("1.0", "end").strip(),
            "body_type": self.body_type_var.get(),
            "body": self.body_text.get("1.0", "end").strip(),
            "auth_type": self.auth_type_var.get(),
            "auth_data": self._get_auth_data(),
        }

    def _load_request(self, req):
        self.method_var.set(req.get("method", "GET"))
        self.url_var.set(req.get("url", ""))

        self.params_text.delete("1.0", "end")
        self.params_text.insert("1.0", req.get("params", ""))

        self.headers_text.delete("1.0", "end")
        self.headers_text.insert("1.0", req.get("headers", ""))

        self.body_type_var.set(req.get("body_type", "json"))
        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", req.get("body", ""))

        self._set_auth_data(req.get("auth_type", "none"), req.get("auth_data", {}))

    def _save_current_request(self):
        """Salva o estado atual no request selecionado ou cria novo."""
        sel = self.tree.selection()
        vals = self.tree.item(sel[0], "values") if sel else None

        if vals and vals[0] == "request":
            folder, req_name = vals[1], vals[2]
            self.collections[folder][req_name] = self._capture_current_state()
            self._save_collections()
            self._refresh_tree()
            self.status_label.configure(text=f"💾 Salvo em {folder}/{req_name}", foreground=self.colors["green"])
        else:
            self._new_request()

    # ── Importar / Exportar ──────────────────────────────────
    def _export_collections(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")],
            title="Exportar Coleções")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.collections, f, indent=2, ensure_ascii=False)
            self.status_label.configure(text="📤 Exportado!", foreground=self.colors["green"])

    def _import_collections(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")], title="Importar Coleções")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for folder, reqs in data.items():
                    if folder not in self.collections:
                        self.collections[folder] = {}
                    self.collections[folder].update(reqs)
                self._save_collections()
                self._refresh_tree()
                self.status_label.configure(text="📥 Importado!", foreground=self.colors["green"])
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar: {e}")

    # ── Parsing ──────────────────────────────────────────────
    def _parse_params(self):
        params = {}
        for line in self.params_text.get("1.0", "end").strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                params[k.strip()] = v.strip()
        return params

    def _parse_headers(self):
        headers = {}
        for line in self.headers_text.get("1.0", "end").strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
        return headers

    def _get_body(self):
        bt = self.body_type_var.get()
        raw = self.body_text.get("1.0", "end").strip()
        if bt == "none" or not raw:
            return None, None
        if bt == "json":
            return raw, "application/json"
        if bt == "form":
            data = {}
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip()
            return urllib.parse.urlencode(data), "application/x-www-form-urlencoded"
        return raw, "text/plain"

    # ── Autenticação na requisição ───────────────────────────
    def _apply_auth_data(self, headers, params, body, t, data):
        """Aplica auth usando dados puros (sem acessar widgets — seguro para threads)."""
        if t == "basic":
            cred = base64.b64encode(f"{data.get('username','')}:{data.get('password','')}".encode()).decode()
            headers["Authorization"] = f"Basic {cred}"
        elif t == "bearer":
            headers["Authorization"] = f"Bearer {data.get('token', '')}"
        elif t == "api_key":
            name, val = data.get("key_name", ""), data.get("key_value", "")
            if data.get("key_in", "header") == "header":
                headers[name] = val
            else:
                params[name] = val
        elif t == "digest":
            return "digest"
        elif t == "hmac_sha256":
            secret = data.get("secret", "").encode()
            payload = (body or "").encode()
            sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
            h_name = data.get("header_name") or "X-Signature"
            headers[h_name] = sig
        return None

    def _apply_auth(self, headers, params, body):
        t = self.auth_type_var.get()
        w = self.auth_widgets
        if t == "basic":
            cred = base64.b64encode(f"{w['username'].get()}:{w['password'].get()}".encode()).decode()
            headers["Authorization"] = f"Basic {cred}"
        elif t == "bearer":
            headers["Authorization"] = f"Bearer {w['token'].get()}"
        elif t == "api_key":
            name, val = w["key_name"].get(), w["key_value"].get()
            if w["key_in"].get() == "header":
                headers[name] = val
            else:
                params[name] = val
        elif t == "digest":
            return "digest"
        elif t == "hmac_sha256":
            secret = w["secret"].get().encode()
            payload = (body or "").encode()
            sig = hmac.new(secret, payload, hashlib.sha256).hexdigest()
            h_name = w["header_name"].get() or "X-Signature"
            headers[h_name] = sig
        return None

    # ── Enviar ───────────────────────────────────────────────
    def _send_request(self):
        # Captura todos os dados da UI na thread principal antes de iniciar a thread
        method = self.method_var.get()
        url = self.url_var.get().strip()
        params = self._parse_params()
        headers = self._parse_headers()
        body, ct = self._get_body()
        if ct and "Content-Type" not in headers:
            headers["Content-Type"] = ct

        auth_type = self.auth_type_var.get()
        auth_data = self._get_auth_data()

        self.status_label.configure(text="⏳ Enviando...", foreground=self.colors["yellow"])
        threading.Thread(
            target=self._do_request,
            args=(method, url, params, headers, body, auth_type, auth_data),
            daemon=True
        ).start()

    def _do_request(self, method, url, params, headers, body, auth_type, auth_data):
        try:
            if not url:
                raise ValueError("URL vazia.")

            auth_flag = self._apply_auth_data(headers, params, body, auth_type, auth_data)
            kwargs = dict(method=method, url=url, headers=headers, params=params, timeout=30)
            if method in ("POST", "PUT", "PATCH"):
                kwargs["data"] = body
            if auth_flag == "digest":
                from requests.auth import HTTPDigestAuth
                kwargs["auth"] = HTTPDigestAuth(
                    auth_data.get("username", ""), auth_data.get("password", ""))

            t0 = time.time()
            resp = requests.request(**kwargs)
            elapsed = time.time() - t0
            self.root.after(0, self._show_response, resp, elapsed)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_response(self, resp, elapsed):
        code = resp.status_code
        c = self.colors
        color = c["green"] if 200 <= code < 300 else c["red"] if code >= 400 else c["yellow"]
        size = len(resp.content)
        size_str = f"{size / 1024:.1f} KB" if size > 1024 else f"{size} B"

        self.status_label.configure(text="✓ Concluído", foreground=c["green"])
        self.resp_info.configure(
            text=f"Status: {code} {resp.reason}  │  {elapsed:.3f}s  │  {size_str}",
            foreground=color)

        self.response_text.delete("1.0", "end")
        try:
            self.response_text.insert("1.0", json.dumps(resp.json(), indent=2, ensure_ascii=False))
        except (ValueError, TypeError):
            self.response_text.insert("1.0", resp.text)

        self.resp_headers_text.delete("1.0", "end")
        self.resp_headers_text.insert("1.0",
                                      "\n".join(f"{k}: {v}" for k, v in resp.headers.items()))

    def _show_error(self, msg):
        self.status_label.configure(text="✗ Erro", foreground=self.colors["red"])
        self.resp_info.configure(text="")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", f"❌ Erro: {msg}")

    # ── Ações resposta ───────────────────────────────────────
    def _copy_response(self):
        txt = self.response_text.get("1.0", "end").strip()
        if txt:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.status_label.configure(text="📋 Copiado!", foreground=self.colors["green"])

    def _save_response_file(self):
        txt = self.response_text.get("1.0", "end").strip()
        if not txt:
            return
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json"), ("Texto", "*.txt")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            self.status_label.configure(text="💾 Salvo!", foreground=self.colors["green"])

    def _clear_response(self):
        self.response_text.delete("1.0", "end")
        self.resp_headers_text.delete("1.0", "end")
        self.resp_info.configure(text="")
        self.status_label.configure(text="Pronto", foreground=self.colors["green"])


if __name__ == "__main__":
    root = tk.Tk()
    HTTPilot(root)
    root.mainloop()
