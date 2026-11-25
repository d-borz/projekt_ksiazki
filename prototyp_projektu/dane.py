# dane.py - wczytanie i przygotowanie danych o książkach
# Zbiór: booksFinal.csv (30 428 książek, kolumny: bookId, title, author, genres, pages, year, rating, numRatings, language)
# Plik musi leżeć obok tego pliku.
import os
import ast
from collections import Counter
import numpy as np
import pandas as pd

NAZWA_PLIKU = "booksFinal.csv"
MIN_OCENA = 3.0          # filtr z karty projektu (ryzyko: książki o niskiej ocenie)
LICZBA_GATUNKOW = 15     # ilu gatunków użytkownik może wybierać
MIN_LICZBA_OCEN = 20     # książki z mniejszą liczbą ocen nie są polecane (ocena 5.0 z 2 głosów nic nie znaczy)
PROG_KROTKA = 200        # poniżej tylu stron książka jest krótka
PROG_SREDNIA = 350       # do tylu stron jest średnia, powyżej długa
WYKLUCZONE_GATUNKI = ["Audiobook", "Novels"]   # to formaty/etykiety, a nie gatunki


def wygeneruj_dane_testowe(ile=40000):
    # Dane SZTUCZNE - tylko żeby program dało się uruchomić bez pliku CSV
    losowy = np.random.RandomState(1)
    gatunki = ["Fantasy", "Romance", "Fiction", "Mystery", "Thriller", "Horror",
               "Science Fiction", "Historical", "Young Adult", "Classics",
               "Nonfiction", "Biography", "Humor", "Poetry", "Crime", "Adventure"]
    wiersze = []
    for i in range(ile):
        ile_gat = losowy.randint(1, 5)
        gat = [str(g) for g in losowy.choice(gatunki, ile_gat, replace=False)]
        wiersze.append({
            "title": "Ksiazka " + str(i),
            "author": "Autor " + str(i % 3000),
            "rating": float(np.clip(losowy.normal(3.9, 0.4), 1, 5)),
            "genres": str(gat),
            "pages": int(np.clip(losowy.normal(350, 150), 40, 1500)),
            "numRatings": int(losowy.lognormal(6, 2)),
        })
    return pd.DataFrame(wiersze)


def parsuj_gatunki(tekst):
    # w pliku gatunki wyglądają tak: "['Fantasy', 'Young Adult']"
    try:
        lista = ast.literal_eval(tekst)
        if isinstance(lista, list):
            return lista
    except (ValueError, SyntaxError):
        pass
    return []


def kategoria_dlugosci(strony):
    if strony < PROG_KROTKA:
        return "krótka"
    elif strony <= PROG_SREDNIA:
        return "średnia"
    else:
        return "długa"


def przygotuj(df):
    df = df[["title", "author", "rating", "genres", "pages", "numRatings"]].copy()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["pages"] = pd.to_numeric(df["pages"], errors="coerce")
    df["numRatings"] = pd.to_numeric(df["numRatings"], errors="coerce")
    df = df.dropna()
    df = df[(df["pages"] > 0) & (df["pages"] <= 3000)]
    df = df[df["rating"] >= MIN_OCENA]          # filtr niskich ocen
    df["gatunki"] = df["genres"].apply(parsuj_gatunki)
    df = df[df["gatunki"].apply(len) > 0]
    df["dlugosc"] = df["pages"].apply(kategoria_dlugosci)
    return df.reset_index(drop=True)


def wczytaj_dane():
    # zwraca: ksiazki (tabela), gatunki (lista), G (macierz 0/1: książka x gatunek)
    if os.path.exists(NAZWA_PLIKU):
        df = pd.read_csv(NAZWA_PLIKU)
    else:
        print("UWAGA: brak pliku " + NAZWA_PLIKU + " - używam danych TESTOWYCH (sztucznych).")
        df = wygeneruj_dane_testowe()
    ksiazki = przygotuj(df)

    licznik = Counter()
    for lista in ksiazki["gatunki"]:
        licznik.update(lista)
    for g in WYKLUCZONE_GATUNKI:
        licznik.pop(g, None)
    gatunki = [g for g, ile in licznik.most_common(LICZBA_GATUNKOW)]

    G = np.zeros((len(ksiazki), len(gatunki)), dtype=int)
    for j, g in enumerate(gatunki):
        G[:, j] = ksiazki["gatunki"].apply(lambda lista: g in lista).values
    return ksiazki, gatunki, G


if __name__ == "__main__":
    ksiazki, gatunki, G = wczytaj_dane()
    print("Liczba książek po filtrze:", len(ksiazki))
    print("Gatunki:", gatunki)
    print(ksiazki[["title", "rating", "pages", "dlugosc"]].head())
