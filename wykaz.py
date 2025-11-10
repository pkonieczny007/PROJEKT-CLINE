import os
import pandas as pd

def process_value(value):
    if isinstance(value, str):
        # Split by comma, take first part, remove dots
        parts = value.split(',')
        if len(parts) > 0:
            processed = parts[0].replace('.', '')
            try:
                return int(processed)
            except ValueError:
                return value  # If not convertible, keep original
        else:
            return value
    else:
        return value

def main():
    # List Excel files
    excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xlsm'))]
    if not excel_files:
        print("Brak plików Excel (.xlsx lub .xlsm) w folderze.")
        return

    # Choose file
    if len(excel_files) == 1:
        chosen_file = excel_files[0]
    else:
        print("Dostępne pliki Excel:")
        for i, f in enumerate(excel_files, 1):
            print(f"{i}. {f}")
        while True:
            try:
                choice = int(input("Wybierz numer pliku: ")) - 1
                if 0 <= choice < len(excel_files):
                    chosen_file = excel_files[choice]
                    break
                else:
                    print("Nieprawidłowy wybór.")
            except ValueError:
                print("Wprowadź liczbę.")

    # Read Excel - tylko pierwsza zakładka
    try:
        df = pd.read_excel(chosen_file, sheet_name=0)
    except Exception as e:
        print(f"Błąd podczas odczytu pliku: {e}")
        return

    # Find Nazwa column
    nazwa_col = None
    for col in df.columns:
        if col.lower() == 'nazwa':
            nazwa_col = col
            break
    if not nazwa_col:
        print("Nie znaleziono kolumny 'Nazwa' lub 'NAZWA'.")
        return

    # Required columns
    required_cols = ['Abmess_1', 'ME', 'Abmes_2', 'Zeinr', 'ZAKUPY', nazwa_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Brakujące kolumny: {missing_cols}")
        return

    # Filter rows where ZAKUPY is 'blacha' (case insensitive)
    df_filtered = df[df['ZAKUPY'].str.lower() == 'blacha'].copy()

    # Process Abmess_1 and Abmes_2
    df_filtered['Abmess_1'] = df_filtered['Abmess_1'].apply(process_value)
    df_filtered['Abmes_2'] = df_filtered['Abmes_2'].apply(process_value)

    # Select columns
    df_output = df_filtered[required_cols]

    # Save to wykaz.xlsx
    df_output.to_excel('wykaz.xlsx', index=False)
    print("Plik 'wykaz.xlsx' został utworzony.")

if __name__ == "__main__":
    main()
