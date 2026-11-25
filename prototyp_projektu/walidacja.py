# walidacja.py - sprawdzenie jakości rekomendacji
# Użycie:
#   python walidacja.py symulacja      - szybki test na losowych "użytkownikach" (tylko pomocniczy)
#   python walidacja.py ankieta        - test z prawdziwym użytkownikiem (powtórz min. 5 razy)
#   python walidacja.py podsumowanie   - liczy wynik z zebranych ankiet
import sys
import os
import csv
import random
import numpy as np

from model import (wytrenuj, rekomenduj, rekomenduj_baseline, policz_cechy,
                   policz_etykiete, DLUGOSCI, MIN_OCENY_UZYTKOWNIKA)
from asystent import zbierz_preferencje, pokaz_rekomendacje

PLIK_WYNIKOW = "wyniki_ankiety.csv"
PROG_TRAFNOSCI = 4        # ocena 4 lub 5 = trafna rekomendacja
PROG_SUKCESU = 3          # min. 3 z 5 trafnych
MIN_UZYTKOWNIKOW = 5


def symulacja():
    drzewo, ksiazki, gatunki, G, wyniki = wytrenuj()
    random.seed(1)
    trafne_drzewo = []
    trafne_baseline = []
    for i in range(200):
        gatunek = random.choice(gatunki)
        dlugosc = random.choice(DLUGOSCI)
        min_ocena = random.choice(MIN_OCENY_UZYTKOWNIKA)
        nr_gatunku = gatunki.index(gatunek)

        wynik = rekomenduj(drzewo, ksiazki, gatunki, G, gatunek, dlugosc, min_ocena)
        X = policz_cechy(ksiazki, G, wynik.index.values, nr_gatunku, dlugosc, min_ocena)
        trafne_drzewo.append(policz_etykiete(X).sum())

        wynik_b = rekomenduj_baseline(ksiazki)
        X_b = policz_cechy(ksiazki, G, wynik_b.index.values, nr_gatunku, dlugosc, min_ocena)
        trafne_baseline.append(policz_etykiete(X_b).sum())

    print("Średnia liczba trafnych książek z 5 (200 symulowanych użytkowników):")
    print("  Drzewo decyzyjne:", round(np.mean(trafne_drzewo), 2))
    print("  Baseline (najpopularniejsze):", round(np.mean(trafne_baseline), 2))
    print("Dokładność modeli na zbiorze testowym:", {k: round(v, 3) for k, v in wyniki.items()})
    print("UWAGA: to symulacja, a nie test z ludźmi - nie zastępuje ankiety.")


def ankieta():
    drzewo, ksiazki, gatunki, G, wyniki = wytrenuj()
    imie = input("Imię testera: ").strip()
    gatunek, dlugosc, min_ocena = zbierz_preferencje(gatunki)
    wynik = rekomenduj(drzewo, ksiazki, gatunki, G, gatunek, dlugosc, min_ocena)
    pokaz_rekomendacje(wynik)

    print("\nOceń każdą rekomendację w skali 1-5:")
    oceny = []
    for i in range(1, 6):
        while True:
            odp = input("  Ocena książki " + str(i) + ": ").strip()
            if odp in ["1", "2", "3", "4", "5"]:
                oceny.append(int(odp))
                break
            print("  Podaj liczbę 1-5.")

    nowy_plik = not os.path.exists(PLIK_WYNIKOW)
    with open(PLIK_WYNIKOW, "a", newline="", encoding="utf-8") as plik:
        zapis = csv.writer(plik)
        if nowy_plik:
            zapis.writerow(["imie", "gatunek", "dlugosc", "min_ocena", "o1", "o2", "o3", "o4", "o5"])
        zapis.writerow([imie, gatunek, dlugosc, min_ocena] + oceny)
    print("Zapisano. Dziękuję!")


def podsumowanie():
    if not os.path.exists(PLIK_WYNIKOW):
        print("Brak pliku " + PLIK_WYNIKOW + " - najpierw przeprowadź ankiety.")
        return
    trafne_na_osobe = []
    with open(PLIK_WYNIKOW, encoding="utf-8") as plik:
        for wiersz in csv.DictReader(plik):
            oceny = [int(wiersz["o" + str(i)]) for i in range(1, 6)]
            trafne = len([o for o in oceny if o >= PROG_TRAFNOSCI])
            print(wiersz["imie"] + ": trafnych " + str(trafne) + " z 5")
            trafne_na_osobe.append(trafne)

    liczba = len(trafne_na_osobe)
    srednia = sum(trafne_na_osobe) / liczba
    print("\nLiczba użytkowników:", liczba)
    print("Średnia liczba trafnych z 5:", round(srednia, 2))
    if liczba < MIN_UZYTKOWNIKOW:
        print("Za mało użytkowników - potrzeba co najmniej " + str(MIN_UZYTKOWNIKOW) + ".")
    elif srednia >= PROG_SUKCESU:
        print("SUKCES: średnio co najmniej 3 z 5 trafnych rekomendacji.")
    else:
        print("BRAK SUKCESU: średnia poniżej 3 z 5.")


if __name__ == "__main__":
    tryb = sys.argv[1] if len(sys.argv) > 1 else ""
    if tryb == "symulacja":
        symulacja()
    elif tryb == "ankieta":
        ankieta()
    elif tryb == "podsumowanie":
        podsumowanie()
    else:
        print("Użycie: python walidacja.py [symulacja | ankieta | podsumowanie]")
