import os
import fdxf
import pandas as pd
import time
from datetime import datetime

# Funkcja tworząca plik data z wykazu
def prepare_data(file_path):
    if not os.path.exists("data.csv"):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            df = df[["Nazwa", "Abmess_1", "Abmes_2"]]
            df = df.dropna(subset=["Nazwa"])  # Usuwanie wierszy, gdzie "Nazwa" jest pusta
            df.to_csv("data.csv", index=False)
            print("Plik data utworzony.")
        else:
            print(f"Plik {file_path} nie istnieje. Upewnij się, że jest w katalogu.")

# Funkcja skanowania plików DXF
def scan():
    prepare_data("wykaz.xlsx")
    data = pd.read_csv("data.csv")
    data["Nazwa"] = data["Nazwa"].fillna("")  # Zastąpienie NaN pustymi stringami

    while True:
        latest_file = None
        latest_time = None

        for filename in os.listdir():
            if filename.endswith('.dxf'):
                file_time = os.path.getmtime(filename)
                if latest_time is None or file_time > latest_time:
                    latest_file = filename
                    latest_time = file_time

        if latest_file:
            wys_value = fdxf.wys(latest_file)
            sze_value = fdxf.sze(latest_file)
            date = time.ctime(latest_time)
            date_time_obj = datetime.strptime(date, "%a %b %d %H:%M:%S %Y")

            base_name = "_".join(latest_file.split("_")[:4])
            match = data[data["Nazwa"].str.startswith(base_name)]

            print(f"Nazwa: {latest_file}")

            if not match.empty:
                abmess_1 = match.iloc[0]["Abmess_1"]
                abmess_2 = match.iloc[0]["Abmes_2"]

                if (wys_value in [abmess_1, abmess_2] and
                    sze_value in [abmess_1, abmess_2]):
                    status = "Pasuje"
                    scale = ""
                else:
                    scale = round(max(abmess_1, abmess_2) / max(wys_value, sze_value), 2)
                    status = "Skala różna"

                print(f"dxf: {wys_value}/{sze_value} wykaz: {abmess_1}/{abmess_2} Status: {status}", end="")
                if scale:
                    print(f", Skala: {scale}")
                else:
                    print()
            else:
                print(f"dxf: {wys_value}/{sze_value} wykaz: brak danych Status: Brak w wykazie")

           

        repeat = input("-----------------------").lower()
        if repeat == "c":
            os.system('cls' if os.name == 'nt' else 'clear')

# Uruchomienie skanera
scan()

print("Dziękuję i zapraszam ponownie!")
