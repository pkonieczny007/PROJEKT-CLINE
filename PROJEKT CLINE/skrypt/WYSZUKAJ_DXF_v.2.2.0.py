import tkinter as tk
from tkinter import filedialog
import os
import shutil
import datetime

# ===========================================================
# Zmienne globalne / domyślne
# ===========================================================
default_destination_folder_name = "Dxf_Pobrane"
chosen_destination_folder = None
chosen_data_file = None  # ścieżka do wybranego pliku txt (np. dane.txt)

# ===========================================================
# Funkcje interfejsu
# ===========================================================
def choose_data_file():
    """
    Pozwala wybrać plik z listą nazw do wyszukania (np. dane.txt).
    """
    global chosen_data_file
    file_path = filedialog.askopenfilename(
        title="Wybierz plik z danymi (txt)",
        filetypes=[('Pliki tekstowe', '*.txt'), ('Wszystkie pliki', '*.*')],
        initialdir="."
    )
    if file_path:
        chosen_data_file = file_path
        data_file_label.config(text=f"Wybrany plik: {os.path.basename(file_path)}")
    else:
        chosen_data_file = None
        data_file_label.config(text="Brak (nie wybrano)")

def choose_destination_folder():
    """
    Pozwala wybrać folder docelowy, do którego będą kopiowane pliki.
    """
    global chosen_destination_folder
    folder_path = filedialog.askdirectory(
        initialdir=".",
        title="Wybierz folder docelowy"
    )
    if folder_path:
        chosen_destination_folder = folder_path
        destination_folder_entry.delete(0, tk.END)
        destination_folder_entry.insert(0, chosen_destination_folder)

def copy_files():
    """
    Główna funkcja kopiująca pliki:
      1) Pobiera z pola tekstowego listę folderów do przeszukania
      2) Pobiera zaznaczone / wpisane rozszerzenia
      3) (opcjonalnie) Wczytuje dane z pliku TXT i filtruje nazwy
      4) Rekurencyjnie szuka pasujących plików i kopiuje je do folderu docelowego
      5) Tworzy wpis w pliku logu
    """
    global chosen_destination_folder
    global chosen_data_file

    # --- 1) Lista folderów do przeszukania ---
    folders_text = folders_text_box.get("1.0", tk.END).strip()
    if not folders_text:
        _log("Nie podano żadnych ścieżek folderów do przeszukania.\n")
        return

    folder_paths = [line.strip() for line in folders_text.splitlines() if line.strip()]

    # --- 2) Ustalenie rozszerzeń do wyszukiwania ---
    ext_list = []

    if dxf_var.get():
        ext_list.append(".dxf")
    if tif_var.get():
        ext_list.append(".tif")

    custom_extension = custom_ext_entry.get().strip()
    # Jeśli użytkownik wpisał np. "pdf" zamiast ".pdf", dodaj kropkę:
    if custom_extension:
        if not custom_extension.startswith("."):
            custom_extension = "." + custom_extension
        ext_list.append(custom_extension)

    # Jeśli lista rozszerzeń pusta - nie ma czego szukać
    if not ext_list:
        _log("Nie wybrano żadnych rozszerzeń do wyszukiwania.\n")
        return

    # --- 3) (opcjonalnie) Wczytanie danych z pliku TXT ---
    use_data = use_data_file_var.get()
    patterns_list = []  # wzorce nazw z pliku dane.txt
    # Dodatkowo słownik do zliczania wystąpień każdego wzorca
    pattern_counts = {}

    if use_data:
        if chosen_data_file and os.path.isfile(chosen_data_file):
            with open(chosen_data_file, "r", encoding="utf-8") as f:
                for line in f:
                    line_clean = line.strip()
                    if line_clean:
                        patterns_list.append(line_clean)
                        pattern_counts[line_clean.lower()] = 0  # startowo 0 wystąpień
        else:
            _log("Zaznaczono 'Używaj pliku danych', ale nie wybrano poprawnego pliku.\n")
            return

    # --- 4) Folder docelowy ---
    destination_folder = destination_folder_entry.get().strip()
    if not destination_folder:
        # jeśli nie wskazano, tworzymy domyślny w miejscu uruchomienia
        destination_folder = os.path.join(os.getcwd(), default_destination_folder_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    # --- 5) Rekurencyjne wyszukiwanie i kopiowanie plików ---
    copied_files_count = 0
    not_found_folders = []

    for folder in folder_paths:
        if not os.path.isdir(folder):
            not_found_folders.append(folder)
            continue

        for root, dirs, files in os.walk(folder):
            for file in files:
                fname, fext = os.path.splitext(file.lower())
                # sprawdzamy rozszerzenie
                if fext in ext_list:
                    # jeśli NIE używamy pliku danych -> kopiujemy wszystko
                    if not use_data:
                        _copy_file(root, file, destination_folder)
                        copied_files_count += 1
                    else:
                        # filtr wg patterns_list
                        for pattern in patterns_list:
                            # Zwróć uwagę na wielkość liter:
                            # w pliku może być "ABC", nazwa pliku "xyz_ABC_123" => pattern.lower() in fname
                            if pattern.lower() in fname:
                                _copy_file(root, file, destination_folder)
                                copied_files_count += 1
                                # Zwiększamy licznik wystąpień
                                pattern_counts[pattern.lower()] += 1
                                # Przerywamy pętlę, żeby nie kopiować wielokrotnie
                                break

    # --- 6) Podsumowanie w polu wyników + przygotowanie logu ---
    msg_lines = []
    msg_lines.append(f"Folder docelowy: {destination_folder}")
    msg_lines.append(f"Znalezione rozszerzenia: {', '.join(ext_list)}")
    msg_lines.append(f"Liczba skopiowanych plików: {copied_files_count}")

    if not_found_folders:
        msg_lines.append("\nNieprawidłowe ścieżki folderów:")
        for nf in not_found_folders:
            msg_lines.append(f" - {nf}")

    # Jeśli użyto pliku danych – sprawdź, które patterny w ogóle nie wystąpiły
    not_found_patterns = []
    if use_data and pattern_counts:
        for pat, count in pattern_counts.items():
            if count == 0:
                not_found_patterns.append(pat)
        if not_found_patterns:
            msg_lines.append("\nNie znaleziono żadnego pliku dla wzorców:")
            for p in not_found_patterns:
                msg_lines.append(f" - {p}")

    # Komunikat w oknie
    _log("\n".join(msg_lines) + "\n\n")

    # --- 7) Zapis do pliku logu ---
    write_log_to_file(
        destination_folder=destination_folder,
        ext_list=ext_list,
        copied_files_count=copied_files_count,
        not_found_folders=not_found_folders,
        not_found_patterns=not_found_patterns
    )

# ===========================================================
# Funkcje pomocnicze
# ===========================================================
def _copy_file(root, file, destination_folder):
    """
    Kopiuje pojedynczy plik do folderu docelowego (z zachowaniem nazwy).
    """
    source_path = os.path.join(root, file)
    dest_path = os.path.join(destination_folder, file)
    try:
        shutil.copy2(source_path, dest_path)
    except shutil.Error:
        # W razie problemów można dopisać szczegóły
        pass

def _log(message):
    """
    Wypisuje komunikat do okna (pole tekstowe) w trybie tylko do odczytu.
    """
    result_box.config(state=tk.NORMAL)
    result_box.insert(tk.END, message)
    result_box.see(tk.END)
    result_box.config(state=tk.DISABLED)

def write_log_to_file(destination_folder, ext_list, copied_files_count, not_found_folders, not_found_patterns):
    """
    Zapisuje najważniejsze informacje do pliku log_kopiowania.txt.
    - Data i godzina
    - Folder docelowy
    - Wybrane rozszerzenia
    - Liczba skopiowanych plików
    - Foldery niedostępne
    - Wzorce nazw (patterns), dla których nie znaleziono pliku
    """
    log_filename = "log_kopiowania.txt"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write("========================================\n")
        log_file.write(f"Data i godzina: {now_str}\n")
        log_file.write(f"Folder docelowy: {destination_folder}\n")
        log_file.write(f"Wybrane rozszerzenia: {', '.join(ext_list)}\n")
        log_file.write(f"Liczba skopiowanych plików: {copied_files_count}\n")

        if not_found_folders:
            log_file.write("Nieprawidłowe foldery (brak dostępu / nie istnieją):\n")
            for nf in not_found_folders:
                log_file.write(f" - {nf}\n")

        if not_found_patterns:
            log_file.write("Niewystępujące wzorce nazw (ani razu nie znaleziono):\n")
            for p in not_found_patterns:
                log_file.write(f" - {p}\n")

        log_file.write("========================================\n\n")

# ===========================================================
# Konfiguracja głównego okna
# ===========================================================
window = tk.Tk()
window.title("Kopiowanie plików – DXF / TIF / Inne + LOG")
window.geometry("700x600")

# -------------------------------
# 1) Instrukcja / label
# -------------------------------
instruction_label = tk.Label(
    window,
    text=(
        "1. Wklej listę folderów (każdy w nowej linii), które chcesz przeszukać.\n"
        "2. Zaznacz rozszerzenia / wpisz własne (np. .pdf, .dwg itp.).\n"
        "3. (Opcjonalnie) użyj pliku dane.txt i kopiuj tylko wybrane pliki.\n"
        "4. Wskaż (lub zostaw domyślny) folder docelowy.\n"
        "5. Kliknij „Kopiuj pliki”. Informacje zostaną zapisane w logu."
    )
)
instruction_label.pack(pady=5)

# -------------------------------
# 2) Pole tekstowe – ścieżki
# -------------------------------
folders_text_box = tk.Text(window, height=6, width=85)
folders_text_box.pack(pady=5)

# -------------------------------
# 3) Rozszerzenia (checkboxy + pole)
# -------------------------------
extensions_frame = tk.LabelFrame(window, text="Rozszerzenia do wyszukania")
extensions_frame.pack(padx=10, pady=5, fill="x")

dxf_var = tk.BooleanVar(value=True)
tif_var = tk.BooleanVar(value=False)

dxf_check = tk.Checkbutton(extensions_frame, text=".dxf", variable=dxf_var)
dxf_check.pack(side=tk.LEFT, padx=5)

tif_check = tk.Checkbutton(extensions_frame, text=".tif", variable=tif_var)
tif_check.pack(side=tk.LEFT, padx=5)

tk.Label(extensions_frame, text="Inne (np. \".pdf\"):").pack(side=tk.LEFT, padx=5)

custom_ext_entry = tk.Entry(extensions_frame, width=8)
custom_ext_entry.pack(side=tk.LEFT, padx=5)
custom_ext_entry.insert(0, "")  # można zostawić puste

# -------------------------------
# 4) Użycie pliku TXT (checkbox + przycisk)
# -------------------------------
data_file_frame = tk.LabelFrame(window, text="Opcjonalnie: użyj pliku tekstowego do filtrowania")
data_file_frame.pack(padx=10, pady=5, fill="x")

use_data_file_var = tk.BooleanVar(value=False)
use_data_check = tk.Checkbutton(data_file_frame, text="Używaj pliku z danymi (np. dane.txt)", variable=use_data_file_var)
use_data_check.pack(side=tk.LEFT, padx=5)

choose_data_button = tk.Button(data_file_frame, text="Wybierz plik", command=choose_data_file)
choose_data_button.pack(side=tk.LEFT, padx=5)

data_file_label = tk.Label(data_file_frame, text="Brak (nie wybrano)")
data_file_label.pack(side=tk.LEFT, padx=5)

# -------------------------------
# 5) Folder docelowy
# -------------------------------
destination_frame = tk.Frame(window)
destination_frame.pack(pady=5)

destination_label = tk.Label(destination_frame, text="Folder docelowy:")
destination_label.pack(side=tk.LEFT, padx=5)

destination_folder_entry = tk.Entry(destination_frame, width=50)
destination_folder_entry.insert(0, "")  # domyślnie puste => utworzy "Dxf_Pobrane"
destination_folder_entry.pack(side=tk.LEFT, padx=5)

choose_dest_button = tk.Button(destination_frame, text="Wybierz...", command=choose_destination_folder)
choose_dest_button.pack(side=tk.LEFT, padx=5)

# -------------------------------
# 6) Przycisk kopiowania
# -------------------------------
copy_button = tk.Button(window, text="Kopiuj pliki", command=copy_files, bg="lightgreen")
copy_button.pack(pady=10)

# -------------------------------
# 7) Pole tekstowe z wynikami
# -------------------------------
result_box = tk.Text(window, height=10, width=85, state=tk.DISABLED)
result_box.pack(pady=5)

window.mainloop()
