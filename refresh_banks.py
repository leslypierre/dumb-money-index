import os
import csv
import pandas as pd

BANKS = ["FED", "ECB", "BOE", "BOC", "RBA", "RBNZ", "SNB", "BOJ"]

OVERVIEW_COLUMNS = [
    "Bank",
    "Next move",
    "Change by",
    "Probability",
    "Other move",
    "Other change by",
    "Other probability",
    "Next meeting date",
    "Current rate"
]

STIR_COLUMNS = ["Date", "Week Ago", "Now"]

DATA_DIR = "policy_data"
os.makedirs(DATA_DIR, exist_ok=True)

def setup_overview():
    print("\n--- Remplissage du tableau principal ---")
    overview_path = os.path.join(DATA_DIR, "central_banks_overview.csv")

    with open(overview_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(OVERVIEW_COLUMNS)

        for bank in BANKS:
            print(f"\nSaisie pour {bank}:")
            row = [bank]
            for col in OVERVIEW_COLUMNS[1:]:
                val = input(f"  {col} : ")
                row.append(val)
            writer.writerow(row)

    print(f"✅ Fichier '{overview_path}' mis à jour.")

def setup_stir():
    print("\n--- Remplissage des fichiers STIR ---")
    for bank in BANKS:
        stir_path = os.path.join(DATA_DIR, f"{bank}_STIR.csv")

        with open(stir_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(STIR_COLUMNS)

            print(f"\nAjout des projections pour {bank}:")
            while True:
                date = input("  Date (ou 'stop' pour finir) : ")
                if date.lower() == "stop":
                    break
                week_ago = input("    Rate a week ago : ")
                now = input("    Rate now        : ")
                writer.writerow([date, week_ago, now])

        print(f"✅ Fichier '{stir_path}' mis à jour.")

def main():
    print("\n=== Initialisation des données politiques monétaires ===")
    setup_overview()
    setup_stir()
    print("\n✅ Tous les fichiers ont été générés avec succès !")

if __name__ == "__main__":
    main()
