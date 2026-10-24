"""
Clone fonctionnel d'utilitaires de compression : BZIP2, LZMA et 7-Zip.
Python 3.x ; interface Tkinter.
Note : BZIP2 et LZMA utilisent les bibliothèques standard de Python.
Le mode 7-Zip utilise l'exécutable 7z/7zz installé séparément.
"""
import bz2
import lzma
import os
import shutil
import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "CompressLab — BZIP2 / LZMA / 7-Zip"


def main():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print("Erreur : impossible d'ouvrir une fenêtre Tkinter.")
        print("Vérifie que Python a Tkinter installé et que tu exécutes l'application dans un environnement graphique.")
        if os.name != "nt" and not os.environ.get("DISPLAY"):
            print("Sur Linux/macOS, assure-toi qu'un serveur X11 ou Wayland est disponible et que DISPLAY est défini.")
        print(f"Détail : {exc}")
        return 1

    try:
        CompressionApp(root)
        root.mainloop()
        return 0
    except Exception as exc:
        print(f"Erreur au démarrage de l'application : {exc}")
        return 1

def human_size(size):
    units = ("o", "Ko", "Mo", "Go", "To")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} o"

def compress_builtin(source, algorithm, level):
    with open(source, "rb") as f:
        data = f.read()
    if algorithm == "BZIP2":
        result = bz2.compress(data, compresslevel=max(1, min(9, level)))
        destination = source + ".bz2"
    else:
        result = lzma.compress(data, preset=max(0, min(9, level)))
        destination = source + ".xz"
    with open(destination, "wb") as f:
        f.write(result)
    return destination

def decompress_builtin(source, algorithm):
    with open(source, "rb") as f:
        data = f.read()
    if algorithm == "BZIP2":
        result = bz2.decompress(data)
        suffix = ".bz2"
    else:
        result = lzma.decompress(data)
        suffix = ".xz"
    destination = source[:-len(suffix)] if source.lower().endswith(suffix) else source + ".decompressed"
    if os.path.abspath(destination) == os.path.abspath(source):
        destination = source + ".decompressed"
    with open(destination, "wb") as f:
        f.write(result)
    return destination

def find_7zip():
    for executable in ("7zz", "7z", "7za", "7z.exe"):
        path = shutil.which(executable)
        if path:
            return path
    return None

def compress_7z(source, level):
    executable = find_7zip()
    if not executable:
        raise RuntimeError("Exécutable 7-Zip introuvable. Installe 7-Zip puis vérifie que 7z/7zz est dans le PATH.")
    destination = source + ".7z"
    subprocess.run([executable, "a", f"-mx={max(0, min(9, level))}", destination, source],
                   check=True, capture_output=True, text=True)
    return destination

def decompress_7z(source):
    executable = find_7zip()
    if not executable:
        raise RuntimeError("Exécutable 7-Zip introuvable. Installe 7-Zip puis vérifie que 7z/7zz est dans le PATH.")
    destination_dir = os.path.dirname(source) or "."
    subprocess.run([executable, "x", "-y", f"-o{destination_dir}", source],
                   check=True, capture_output=True, text=True)
    return destination_dir

class CompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("900x700")
        self.root.minsize(700, 600)
        self.file_path = tk.StringVar()
        self.algorithm = tk.StringVar(value="BZIP2")
        self.level = tk.IntVar(value=6)
        self.status = tk.StringVar(value="Choisis un fichier pour commencer.")
        self.level_hint = tk.StringVar()
        self._configure_style()
        self._build_ui()
        self._on_algorithm_change()

    def _configure_style(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.colors = {
            "background": "#f3f6fb",
            "surface": "#ffffff",
            "header": "#172554",
            "primary": "#2563eb",
            "primary_active": "#1d4ed8",
            "text": "#172033",
            "muted": "#64748b",
            "border": "#dbe3ef",
            "success": "#15803d",
        }
        style.configure("App.TFrame", background=self.colors["background"])
        style.configure("Header.TFrame", background=self.colors["header"])
        style.configure("Body.TFrame", background=self.colors["surface"])
        style.configure(
            "HeaderTitle.TLabel",
            background=self.colors["header"],
            foreground="#ffffff",
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "HeaderSub.TLabel",
            background=self.colors["header"],
            foreground="#cbd5e1",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Eyebrow.TLabel",
            background=self.colors["header"],
            foreground="#93c5fd",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Section.TLabelframe",
            background=self.colors["surface"],
            bordercolor=self.colors["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Section.TLabelframe.Label",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Section.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Hint.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Primary.TButton",
            background=self.colors["primary"],
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", self.colors["primary_active"]), ("disabled", "#94a3b8")],
            foreground=[("disabled", "#ffffff")],
        )
        style.configure(
            "Secondary.TButton",
            background="#e8eef8",
            foreground=self.colors["text"],
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#d8e2f1")])
        style.configure(
            "Status.TLabel",
            background=self.colors["background"],
            foreground=self.colors["success"],
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "TEntry",
            fieldbackground="#f8fafc",
            foreground=self.colors["text"],
            padding=9,
        )
        style.configure(
            "TCombobox",
            fieldbackground="#f8fafc",
            foreground=self.colors["text"],
            padding=6,
        )
        style.configure("TSpinbox", padding=6)

    def _build_ui(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=24)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="Header.TFrame", padding=(22, 18))
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(
            header, text="OUTIL DE COMPRESSION", style="Eyebrow.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            header, text="CompressLab", style="HeaderTitle.TLabel"
        ).pack(anchor="w", pady=(3, 0))
        ttk.Label(
            header,
            text="Compresse, décompresse et compare tes fichiers en quelques clics.",
            style="HeaderSub.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        file_frame = ttk.LabelFrame(
            outer, text="  1  ·  Fichier à traiter  ", style="Section.TLabelframe", padding=14
        )
        file_frame.pack(fill="x", pady=(0, 12))
        row = ttk.Frame(file_frame, style="Body.TFrame")
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.file_path).pack(
            side="left", fill="x", expand=True, padx=(0, 10)
        )
        ttk.Button(
            row, text="Parcourir…", command=self.choose_file, style="Secondary.TButton"
        ).pack(side="right")

        options = ttk.LabelFrame(
            outer, text="  2  ·  Paramètres  ", style="Section.TLabelframe", padding=14
        )
        options.pack(fill="x", pady=(0, 12))
        options.columnconfigure(1, weight=1)
        ttk.Label(options, text="Algorithme", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 18), pady=(0, 5)
        )
        self.algorithm_combo = ttk.Combobox(
            options,
            textvariable=self.algorithm,
            values=("BZIP2", "LZMA", "7-Zip"),
            state="readonly",
            width=18,
        )
        self.algorithm_combo.grid(row=0, column=1, sticky="ew", pady=(0, 5))
        self.algorithm_combo.bind("<<ComboboxSelected>>", self._on_algorithm_change)

        ttk.Label(options, text="Niveau de compression", style="Section.TLabel").grid(
            row=1, column=0, sticky="w", padx=(0, 18), pady=(5, 0)
        )
        level_row = ttk.Frame(options, style="Body.TFrame")
        level_row.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        self.level_spinbox = ttk.Spinbox(
            level_row, from_=1, to=9, textvariable=self.level, width=6
        )
        self.level_spinbox.pack(side="left", padx=(0, 10))
        ttk.Label(level_row, textvariable=self.level_hint, style="Hint.TLabel").pack(
            side="left", fill="x", expand=True
        )

        actions = ttk.Frame(outer, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 12))
        ttk.Button(
            actions, text="Compresser", command=self.compress, style="Primary.TButton"
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            actions, text="Décompresser", command=self.decompress, style="Secondary.TButton"
        ).pack(side="left")
        ttk.Button(
            actions, text="Effacer les résultats", command=self.clear, style="Secondary.TButton"
        ).pack(side="right")

        results = ttk.LabelFrame(
            outer,
            text="  3  ·  Résultats  ",
            style="Section.TLabelframe",
            padding=12,
        )
        results.pack(fill="both", expand=True)
        results.rowconfigure(0, weight=1)
        results.columnconfigure(0, weight=1)
        self.output = tk.Text(
            results,
            height=10,
            wrap="word",
            state="disabled",
            font=("Consolas", 10),
            background="#f8fafc",
            foreground=self.colors["text"],
            insertbackground=self.colors["text"],
            selectbackground="#bfdbfe",
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["primary"],
        )
        self.output.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(results, orient="vertical", command=self.output.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.output.configure(yscrollcommand=scrollbar.set)

        footer = ttk.Frame(outer, style="App.TFrame")
        footer.pack(fill="x", pady=(12, 0))
        ttk.Label(footer, textvariable=self.status, style="Status.TLabel").pack(
            side="left"
        )
        ttk.Label(
            footer,
            text="Formats déjà compressés : la taille peut peu diminuer.",
            background=self.colors["background"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        ).pack(side="right")

    def _on_algorithm_change(self, event=None):
        if event is not None and event.widget is not self.algorithm_combo:
            return
        is_bzip2 = self.algorithm.get() == "BZIP2"
        minimum = 1 if is_bzip2 else 0
        self.level_spinbox.configure(from_=minimum, to=9)
        if self.level.get() < minimum:
            self.level.set(minimum)
        if is_bzip2:
            self.level_hint.set("BZIP2 : de 1 (rapide) à 9 (meilleure compression).")
        else:
            self.level_hint.set("De 0 (rapide) à 9 (meilleure compression).")

    def choose_file(self):
        path = filedialog.askopenfilename(title="Sélectionner un fichier")
        if path:
            self.file_path.set(path)
            self.status.set("Fichier sélectionné.")

    def log(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def clear(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.status.set("Résultats effacés.")

    def compress(self):
        source = self.file_path.get().strip()
        if not source or not os.path.isfile(source):
            messagebox.showwarning("Fichier manquant", "Sélectionne d'abord un fichier valide.")
            return
        algorithm = self.algorithm.get()
        level = int(self.level.get())
        try:
            original_size = os.path.getsize(source)
            start = time.perf_counter()
            if algorithm == "7-Zip":
                destination = compress_7z(source, level)
            else:
                destination = compress_builtin(source, algorithm, level)
            elapsed = time.perf_counter() - start
            compressed_size = os.path.getsize(destination) if os.path.isfile(destination) else None
            self.log(f"Compression réussie — {algorithm}")
            self.log(f"Source      : {source}")
            self.log(f"Résultat    : {destination}")
            self.log(f"Taille source : {human_size(original_size)}")
            if compressed_size is not None:
                self.log(f"Taille compressée : {human_size(compressed_size)}")
                ratio = (1 - compressed_size / original_size) * 100 if original_size else 0
                self.log(f"Réduction de taille : {ratio:.2f}%")
                self.log("Remarque : une valeur négative signifie que le fichier compressé est plus grand.")
            self.log(f"Temps écoulé : {elapsed:.3f} s")
            self.log("-" * 58)
            self.status.set("Compression terminée.")
        except Exception as exc:
            messagebox.showerror("Erreur de compression", str(exc))
            self.status.set("La compression a échoué.")

    def decompress(self):
        source = self.file_path.get().strip()
        if not source or not os.path.isfile(source):
            messagebox.showwarning("Fichier manquant", "Sélectionne d'abord un fichier compressé valide.")
            return
        algorithm = self.algorithm.get()
        try:
            start = time.perf_counter()
            if algorithm == "7-Zip":
                destination = decompress_7z(source)
            else:
                destination = decompress_builtin(source, algorithm)
            elapsed = time.perf_counter() - start
            self.log(f"Décompression terminée — {algorithm}")
            self.log(f"Entrée : {source}")
            self.log(f"Sortie : {destination}")
            self.log(f"Temps écoulé : {elapsed:.3f} s")
            self.log("-" * 58)
            self.status.set("Décompression terminée.")
        except Exception as exc:
            messagebox.showerror("Erreur de décompression", str(exc))
            self.status.set("La décompression a échoué.")

if __name__ == "__main__":
    raise SystemExit(main())
