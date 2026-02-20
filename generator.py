import argparse
import csv
import json
import sys
from faker import Faker
from datetime import datetime

# Inicjalizacja Faker z polskimi danymi
fake = Faker('pl_PL')

# MAPOWANIE PÓŁ
# Tu dodajesz nowe typy danych, jeśli potrzebujesz
FIELD_MAPPING = {
    "imie": fake.first_name,
    "nazwisko": fake.last_name,
    "pesel": fake.pesel,
    "telefon": fake.phone_number,
    "nip": fake.nip,
    "regon": fake.regon,
    "miasto": fake.city,
    "adres": fake.address,
    "nazwa_firmy": fake.company,
    "email": fake.email,
    "data": fake.date,
    "tekst": fake.sentence
}

def load_schemas(filename="schemas.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {filename}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Błąd: Plik {filename} nie jest poprawnym JSON-em")
        sys.exit(1)

def generate_row_data(fields):
    """Zwraca listę wygenerowanych wartości dla danego wiersza"""
    row = []
    for field in fields:
        generator = FIELD_MAPPING.get(field)
        if generator:
            # Wywołujemy funkcję Fakera
            row.append(generator())
        else:
            # Fallback jeśli w JSON jest literówka
            row.append(f"MISSING_{field}")
    return row

def main():
    parser = argparse.ArgumentParser(description="Generator plików CSV (format techniczny)")
    parser.add_argument("typ_pliku", help="Klucz z pliku schemas.json")
    parser.add_argument("liczba_linii", type=int, help="Liczba rekordów danych (bez nagłówka)")
    
    args = parser.parse_args()
    schemas = load_schemas()
    
    if args.typ_pliku not in schemas:
        print(f"Nieznany typ pliku: {args.typ_pliku}. Dostępne: {list(schemas.keys())}")
        sys.exit(1)

    # Konfiguracja
    schema = schemas[args.typ_pliku]
    version = schema.get("wersja", "1.0")
    fields_list = schema.get("pola", [])
    
    # Obliczenia: Liczba danych
    data_count = args.liczba_linii
    total_lines = data_count
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{args.typ_pliku}_{timestamp}.txt" # Zmieniam na .txt, bo to format niestandardowy

    print(f"Tworzenie {filename}...")

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        # Używamy csv.writer do obsługi separatora i ew. znaków specjalnych w danych
        writer = csv.writer(f, delimiter='|', quoting=csv.QUOTE_MINIMAL)

        # 1. Zapis NAGŁÓWKA TECHNICZNEGO (ręcznie, by uniknąć cudzysłowów csv writera w prostym stringu)
        # Format: WERSJA|LICZBA_LINII
        f.write(f"{version}|{total_lines}\n")

        # 2. Zapis REKORDÓW
        for i in range(1, data_count + 1):
            # Generujemy dane
            raw_data = generate_row_data(fields_list)
            
            # Sklejamy: [Numer linii] + [Dane]
            # Numer linii jest w pierwszej kolumnie
            final_row = [i] + raw_data
            
            writer.writerow(final_row)

    print("Zakończono sukcesem.")

if __name__ == "__main__":
    main()