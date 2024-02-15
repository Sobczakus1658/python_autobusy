import webbrowser
from speedingBuses import statistic, speeding
from experiment import accidents, warsaw_tour, show
from downloadData import prepare_data
from divideById import divide
from PIL import Image
from punctualityBuses import statistic_punctuality, punctuality


def download_data():
    prepare_data()


def divide_data():
    divide()


def speeding_bus_process():
    speeding()


def punctuality_buses():
    punctuality()


def open_punctuality_buses(late_tolerance, min_count):
    statistic_punctuality(late_tolerance, min_count)
    print("Wygenerowano plik line_late.csv")
    image = Image.open("myData/punctualityBuses.png")
    image.show()
    print("Wygenerowano plik punctualityBuses.png w folderze myData")


def open_speeding_statistic(speed_tolerance):
    speed_tolerance = int(int(speed_tolerance) / 3.6)
    statistic(speed_tolerance)
    webbrowser.open("myData/warsaw_map_places.html")
    webbrowser.open("myData/warsaw_map_single.html")
    image = Image.open("myData/buses_velocity.png")
    image.show()
    print("Wygenerowano plik speed_buses.csv w folderze myData")
    print("Wygenerowano plik buses_velocity.png w folderze myData")


def experiment_accidents(speed_tolerance):
    speed_tolerance = int(int(speed_tolerance) / 3.6)
    accidents(speed_tolerance)
    webbrowser.open("myData/warsaw_map_with_accidents.html")


def experiment_tour():
    print("Czy wolisz opcję z odległością")
    print("czy opcję ze współrzędnymi geograficznymi?")
    print("Uwaga, opcja z odległością może potrwać do 30 minut!")
    response = input("Wybierz 1 jak chcesz odległość,2 w przeciwnym przypadku")
    if response == '1':
        b_tol = input("Wpisz odległość do budynków jaka będzie tolerowana")
        p_tol = input("Wpisz odległość do miejsc jaka będzię tolerowana")
        warsaw_tour(b_tol, p_tol)
        show(1)
        image = Image.open("myData/top_lines_info1.jpeg")
        image.show()

    if response == '2':
        warsaw_tour()
        show(2)
        image = Image.open("myData/top_lines_info2.jpeg")
        image.show()
    print("Zakończono experyment")
    print("Dane zapisane są w MyData tour.csv")


def welcome_message():
    print("Witaj użytkowniku na prezentacji projektu z Pythona!")


def display_options():
    print("Wybierz opcję:")
    print("1. Pobierz dane")
    print("2. Podziel dane")
    print("3. Przeanalizuj prędkość autobusów")
    print("4. Wyświetl dane o prędkości autobusów")
    print("5. Przeanalizuj punktualność autobusów")
    print("6. Wyświetl dane o punktualności autobusów")
    print("7. Eksperyment - Zależność prędkości od miejsc wypadków")
    print("8. Eksperyment - Najbardziej turystyczne autobusy")


def handle_option(option):
    try:
        option = int(option)
    except ValueError:
        print("Nie podano liczby całkowitej.")
        return
    if option == 1:
        print("Wybrano pobieranie danych")
        print("Uwaga to może potrwać naprawdę długo")
        print("Czy na pewno potrzebujesz danych ?")
        response = input("Czy na pewno chcesz kontynuować? (tak/nie): ")
        if response.lower() != "tak":
            print("Anulowano pobieranie danych.")
            return
        else:
            print("Rozpoczynam pobieranie danych...")
            download_data()
            print("Pobieranie danych zakończone.")
    elif option == 2:
        print("Wybrano podział danych")
        divide_data()
        print("Podział danych zakończony pomyślnie!")
    elif option == 3:
        print("Wybrano analizę prędkości autobusów")
        speeding_bus_process()
        print("Analiza prędkości autobusów zakończona pomyślnie!")
    elif option == 4:
        print("Wybrano wyświetlenie danych o prędkości")
        print("Zakładamy, że dopuszczalna prędkość to 50 km/h")
        print("Proszę podać zakres od 0 do 46")
        print("Podaj do ilu km/h autobus może przekroczyć prędkość")
        response = input()
        open_speeding_statistic(response)
    elif option == 5:
        print("Wybrano analizę punktualności autobusów.")
        print("Uwaga to może potrwać koło 5 minut")
        print("Czy na pewno potrzebujesz danych ?")
        response = input("Czy na pewno chcesz kontynuować? (tak/nie): ")
        if response.lower() != "tak":
            print("Anulowano pobieranie danych.")
            return
        else:
            print("Rozpoczynam analizę punktualności")
            punctuality_buses()
        print("Analiza punktualności zakończona pomyślnie!")
    elif option == 6:
        print("Wybrano wyświetlenie danych o punktualności")
        print("Proszę wprowadzić:")
        late_tolerance = input("tolerancję spóźnienia ")
        message = "liczba spóźnień linii,żeby została uwzględniona na wykresie"
        min_count = input(message)
        open_punctuality_buses(int(late_tolerance), int(min_count))
        print("Zakończono wizualizację danych")

    elif option == 7:
        print("Wybrano zależnośc prędkości do miejsc wypadków")
        print("Zakładamy, że dopuszczalna prędkość to 50 km/h")
        print("Proszę podać zakres od 0 do 46")
        response = input("Podaj do ilu km/h autobus może przekroczyć prędkość")
        experiment_accidents(response)
    elif option == 8:
        print("Wybrano najbardziej turystyczne autobusy")
        experiment_tour()
        print("Zakończono analizę najbardziej turystycznych autobusów !")
    else:
        print("Nieprawidłowa opcja. Wybierz opcję od 1 do 8.")


def main():
    welcome_message()
    while True:
        display_options()
        option = input("Podaj numer opcji: ")
        handle_option(option)


if __name__ == "__main__":
    main()
