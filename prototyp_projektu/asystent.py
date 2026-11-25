# asystent.py - rozmowa z użytkownikiem i wyświetlenie 5 rekomendacji
from model import wytrenuj, rekomenduj, DLUGOSCI, MIN_OCENY_UZYTKOWNIKA
from dane import PROG_KROTKA, PROG_SREDNIA


def zapytaj_o_wybor(pytanie, opcje):
    # pokazuje numerowaną listę i czeka na poprawny numer
    print(pytanie)
    for i, opcja in enumerate(opcje, start=1):
        print("  " + str(i) + ". " + str(opcja))
    while True:
        odpowiedz = input("Twój wybór (numer): ").strip()
        if odpowiedz.isdigit() and 1 <= int(odpowiedz) <= len(opcje):
            return opcje[int(odpowiedz) - 1]
        print("Podaj numer z listy.")


def zbierz_preferencje(gatunki):
    gatunek = zapytaj_o_wybor("\nJaki gatunek Cię interesuje?", gatunki)
    dlugosc = zapytaj_o_wybor("\nJak długa ma być książka? (krótka <" + str(PROG_KROTKA) + " str., średnia do " + str(PROG_SREDNIA) + ", długa powyżej)", DLUGOSCI)
    min_ocena = zapytaj_o_wybor("\nMinimalna ocena czytelników?", MIN_OCENY_UZYTKOWNIKA)
    return gatunek, dlugosc, min_ocena


def pokaz_rekomendacje(wynik):
    print("\nPolecam te 5 książek:")
    i = 1
    for _, ksiazka in wynik.iterrows():
        print("  " + str(i) + ". " + str(ksiazka["title"]) + " - " + str(ksiazka["author"])
              + " (ocena " + str(round(ksiazka["rating"], 2)) + ", " + str(int(ksiazka["pages"])) + " str.)")
        i = i + 1


if __name__ == "__main__":
    print("Trenuję model...")
    drzewo, ksiazki, gatunki, G, wyniki = wytrenuj()
    gatunek, dlugosc, min_ocena = zbierz_preferencje(gatunki)
    wynik = rekomenduj(drzewo, ksiazki, gatunki, G, gatunek, dlugosc, min_ocena)
    pokaz_rekomendacje(wynik)
