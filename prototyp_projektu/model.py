# model.py - drzewo decyzyjne, baseline (DummyClassifier) i rekomendacje
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from dane import wczytaj_dane, MIN_OCENA, MIN_LICZBA_OCEN

DLUGOSCI = ["krótka", "średnia", "długa"]
MIN_OCENY_UZYTKOWNIKA = [3.5, 4.0, 4.5]
NAZWY_CECH = ["gatunek_pasuje", "dlugosc_pasuje", "roznica_oceny", "popularnosc"]


def policz_cechy(ksiazki, G, numery, nr_gatunku, dlugosc, min_ocena):
    # Cechy opisujące PARĘ: (preferencje użytkownika, książka)
    # numery - indeksy książek, reszta - preferencje (jedna wartość lub tablica)
    gatunek_pasuje = G[numery, nr_gatunku]
    dlugosc_pasuje = (ksiazki["dlugosc"].values[numery] == dlugosc).astype(int)
    roznica_oceny = ksiazki["rating"].values[numery] - min_ocena
    popularnosc = np.log10(ksiazki["numRatings"].values[numery] + 1)
    return np.column_stack([gatunek_pasuje, dlugosc_pasuje, roznica_oceny, popularnosc])


def policz_etykiete(X):
    # Etykieta 1 = książka pasuje do preferencji:
    # pasuje gatunek, pasuje długość i ocena nie jest niższa niż żądana
    return ((X[:, 0] == 1) & (X[:, 1] == 1) & (X[:, 2] >= 0)).astype(int)


def zbuduj_zbior_treningowy(ksiazki, G, ile_par=100000, ziarno=42):
    losowy = np.random.RandomState(ziarno)
    numery = losowy.randint(0, len(ksiazki), ile_par)
    nr_gatunku = losowy.randint(0, G.shape[1], ile_par)
    dlugosc = losowy.choice(DLUGOSCI, ile_par)
    min_ocena = losowy.choice(MIN_OCENY_UZYTKOWNIKA, ile_par)

    X = policz_cechy(ksiazki, G, numery, nr_gatunku, dlugosc, min_ocena)
    y = policz_etykiete(X)

    # klas jest nierówno (mało pasujących par) - wyrównujemy liczebność
    poz = np.where(y == 1)[0]
    neg = np.where(y == 0)[0]
    neg = losowy.choice(neg, len(poz), replace=False)
    wybrane = np.concatenate([poz, neg])
    return X[wybrane], y[wybrane]


def wytrenuj():
    ksiazki, gatunki, G = wczytaj_dane()
    X, y = zbuduj_zbior_treningowy(ksiazki, G)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    drzewo = DecisionTreeClassifier(max_depth=5, random_state=42)
    drzewo.fit(X_tr, y_tr)

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_tr, y_tr)

    wyniki = {
        "drzewo_accuracy": accuracy_score(y_te, drzewo.predict(X_te)),
        "drzewo_f1": f1_score(y_te, drzewo.predict(X_te)),
        "dummy_accuracy": accuracy_score(y_te, baseline.predict(X_te)),
        "dummy_f1": f1_score(y_te, baseline.predict(X_te), zero_division=0),
    }
    return drzewo, ksiazki, gatunki, G, wyniki


def rekomenduj(drzewo, ksiazki, gatunki, G, gatunek, dlugosc, min_ocena, ile=5):
    # Zwraca 5 książek, które drzewo uznaje za najlepiej dopasowane
    nr_gatunku = gatunki.index(gatunek)
    numery = np.arange(len(ksiazki))
    X = policz_cechy(ksiazki, G, numery, nr_gatunku, dlugosc, min_ocena)

    nr_klasy_1 = list(drzewo.classes_).index(1)
    prawdopodobienstwo = drzewo.predict_proba(X)[:, nr_klasy_1]

    tabela = ksiazki.copy()
    tabela["dopasowanie"] = prawdopodobienstwo
    tabela = tabela[tabela["rating"] >= MIN_OCENA]       # FILTR NISKICH OCEN (ryzyko z karty)
    tabela = tabela[tabela["numRatings"] >= MIN_LICZBA_OCEN]   # tylko książki z sensowną liczbą ocen
    tabela = tabela.sort_values(["dopasowanie", "rating", "numRatings"], ascending=False)
    return tabela.head(ile)


def rekomenduj_baseline(ksiazki, ile=5):
    # Baseline: najpopularniejsze książki, bez patrzenia na preferencje
    tabela = ksiazki[ksiazki["rating"] >= MIN_OCENA]
    tabela = tabela[tabela["numRatings"] >= MIN_LICZBA_OCEN]
    return tabela.sort_values("numRatings", ascending=False).head(ile)


if __name__ == "__main__":
    drzewo, ksiazki, gatunki, G, wyniki = wytrenuj()
    print("Wyniki na zbiorze testowym:")
    for nazwa, wartosc in wyniki.items():
        print(" ", nazwa, round(wartosc, 3))
    print()
    print(rekomenduj(drzewo, ksiazki, gatunki, G, gatunki[0], "średnia", 4.0)[["title", "author", "rating", "pages"]])
