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
        self.root.geometry("760x560")
        self.root.minsize(650, 500)
        self.file_path = tk.StringVar()
        self.algorithm = tk.StringVar(value="BZIP2")
        self.level = tk.IntVar(value=6)
        self.status = tk.StringVar(value="Choisis un fichier pour commencer.")
        self._build_ui()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=22)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="CompressLab", font=("Arial", 23, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Compression • Décompression • Mesures", font=("Arial", 11)).pack(anchor="w", pady=(0, 18))

        file_frame = ttk.LabelFrame(outer, text="1. Fichier à traiter", padding=12)
        file_frame.pack(fill="x", pady=6)
        row = ttk.Frame(file_frame)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.file_path).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(row, text="Parcourir…", command=self.choose_file).pack(side="right")

        opts = ttk.LabelFrame(outer, text="2. Paramètres", padding=12)
        opts.pack(fill="x", pady=6)
        ttk.Label(opts, text="Algorithme :").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        combo = ttk.Combobox(opts, textvariable=self.algorithm, values=("BZIP2", "LZMA", "7-Zip"), state="readonly", width=16)
        combo.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(opts, text="Niveau (0–9 pour LZMA/7-Zip, 1–9 pour BZIP2) :").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Spinbox(opts, from_=0, to=9, textvariable=self.level, width=6).grid(row=1, column=1, sticky="w", pady=4)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Compresser", command=self.compress).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Décompresser", command=self.decompress).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Effacer les résultats", command=self.clear).pack(side="left")

        results = ttk.LabelFrame(outer, text="3. Résultats", padding=12)
        results.pack(fill="both", expand=True, pady=4)
        self.output = tk.Text(results, height=10, wrap="word", state="disabled", font=("Consolas", 10))
        self.output.pack(fill="both", expand=True)

        ttk.Label(outer, textvariable=self.status, foreground="#245a38").pack(anchor="w", pady=(10, 0))
        ttk.Label(outer, text="Conseil : teste un fichier texte, un audio, une image et une vidéo.", font=("Arial", 9)).pack(anchor="w", pady=(5, 0))

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
