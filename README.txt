indeks: 440009
imię i nazwisko: Michał Sobczak

Tutaj znajduje się opis mojego zadania zaliczeniowego z Pythona 2023/2024

Stworzyłem w tym zadaniu kilka folderów:
autobuses - jest to folder, który zawiera pliki z autobusami. Nazwa pliku to id_autobusu.
            w pliku trzymam takie informacje jak linia autobusowa, położenie autobusu o 
            konkretnej godzinie
bus_stations - folder ten zawiera jeden plik csv, który zawiera informacje o wszystkich
               przystankach w Warszawie
schedule  - trzymam tam rozkład jazdy. Dla każdego przystanku trzymam linie które się   
            zatrzymują w tym miejscu i o której godzinie.
myData  - jest to folder, w którym trzymam wszystkie statystyki, które wyprodukuję.

Pliki, które zawierają przedrostk download służą do pobierania danych. 
Pobieranie rozkładu i przystanków zostało wykomentowane, bo trwają stosunkowo długo.
Pobieranie danych o autobusach powinno działać przez godzinę i zapisywać dane to data.
W prezentacji kodu, iteracji będzie tylko 3 i wyniki będą zapisywane do folderu data1
Ta część jest czasochłonna, ale nie jestem w stanie jej zoptymalizować, bo położenie 
autbusów muszę pobierać przez minimum godzinę, natomiast pobieranie rozkładu jest bardzo czasochłonne.
Muszę najpierw pobrać przystanki, potem linie które się na niej zatrzymują, a na końcu rozkład dla danej linii.
Przez to, że jest tyle zapytań, to działa to bardzo długo.

divideById - jest to plik, który odpowiada za to, żeby dane pobrane z wcześniejszej części,
zostały przeanalizowane. Mówimy tutaj o podziale tych danych na pliki o id_autobusu. Dzięki temu
w jednym pliku mam położenie i czas danego autobusu, z którego potem będę korzystał. 
Wykonuję to tylko raz, więc mogę sobie pozwolić na długi czas na działania, ale ku naszego zaskoczeniu,
proces ten trwa stosunkowo krótko i zależy liniowo od liczby wszytskich danych pobranych przez godzinę 


W dalszej części, będę korzystał z danych zebranych od 19:20 do 20:58 13.02.2024

constants to plik który zawiera stałe używane w programie

speedingBuses - plik ten odpowiada, żeby wykryć, które autobusy przekroczyły prędkość
50 km/h. Odległość, będę liczył z twierdzenia Pitagorasa. Założyłem, że autobus, nie 
potrafi pojechać więcej niż 28 metrów na sekundę (dane z internetu), więc wszystkie takie
dane odrzucam. Znalazłem również przelicznik współrzędnych geograficznych na metry i zapisałem 
go w pliku ze stałymi. Analizę ile danych dany autobus przekroczył prędkość zrobiłem tylko raz 
i zapisałem do do pliku csv speed_buses.csv. 
Druga część tego pliku umożliwia tworzenie statystyki i dzięki temu, że dane mam zapisane w pliku csv,
trwa to o wiele szybciej niż jakbym musiał to robić za każdym razem. Parametrem statystki jest 
prędkość i na wykresie będą uwzględnione tylko pojazdy które przekroczyły prędkośc 50 km/h + parametr.
W przypadku zbyt małego parametru wykresy mogą być nieczytelne. warsaw_map_single to mapa, która zawiera punkty
gdzie autobus jechał z prędkością większą niż 50 + parametr. Dla dwóch punktów, jeżeli prędkość wyniosła więcej
niż próg na mapie zostanie zaznaczony późniejszy punkt ( punkt, w którym autubus znalazł się później).
warsaw_map_places dzieli Warszawę na pewne sektory. Następnie w zależności od liczby przekroczeń prędkości
w tym sektorze zamalowuje go w skali od jasno zielonego - do czerownego. Najwięcej przekroczeń jest 
w obszarze gdzie jest kolor bliżej czerwonego. Gdy naciśnie się pole, wyświetla się liczba autobusów,
które przekroczyły prędkość w tym obszarze.

punctualityBuses - Dla każdego autobusu najpierw sprawdzam czy znajduje się na przystanku. Zakładam, że autobus
znajduje się na przystanku gdy pierwsze 4 pozycje (dokładnośc 0.0001 stopnia czyli 10 metrów) po przecinku zgadzają się z położeniem przystanka.
Następnie dla danego przystanka sprawdzam rozkład i znajduję pierwszą najwcześniejszą godzinę pasującą
do przyjazdu autobusu. Niestety, jeżeli jakiś autobus spóźni się 15 minut na pierwszy przystanek to potem te
opóźnienie będzie na każdym przystanku, więc zostanie policzony wielokrotnie. Preferuje się, więc dobierać trochę
większe dane do statystyki. Możemy mieć sytuację gdzie autobus przez jakiś czas stał na przystanku.
Wtedy chciałbym wziąć czas najwcześniejszy, ponieważ ten czas będzie najbardziej rzetelny do opóźnienia.
Wszystkie czasy do 2 minut od pierwszego pojawienia się na przystanku pomijam.

experiment - ta część to część własna, którą uznałem za ciekawą. Pierwsza z nich to zależność wypadków
od miejsc, gdzie autobusy jeżdżą najszybciej. Pierwszym parametrem jest dopuszczalna prędkość,
która można przekroczyć ponad 50 km/h. Dane te pobrałem ze stron :
https://zdm.waw.pl/wp-content/uploads/2020/07/Raport-BRD-2019__ZDM.pdf
https://ksp.policja.gov.pl/wrd/o-nas/statystyki/2023/123361,STYCZEN-CZERWIEC-2023.html
https://ksp.policja.gov.pl/wrd/o-nas/statystyki/2022/117239,STYCZEN-GRUDZIEN-2022.html 
Mimo tego, że część ta wydaje się prosta, wymagała one ode mnie dużo reasearchu. Komunikowałem
się z wydziałem ruchu drogowego oraz Zarządem Dróg Warszawskich o te dane. Część z nich
jest niedostępna dla zwykłego śmiertlenika bądź ZDM dopiero planuje udostępnić dane.
Stąd dostałem kilka linków i danych od nich, więc są potwierdzone

Drugi eksperyment nazywa się, najbardziej turystyczne autobusy w Warszawie, co uznaję również 
za ciekawe. Są dwie możliwości zbadania tego, pierwsza po odległości, druga po współrzędnych.
W tym ekperymencie poszukuję takich linii, dzięki którym będę mógł zwiedzić jak najwięcej 
rzeczy w Warszawie. Pierwszy sposób, gdzie wyniki są ciekawsze, ale czas wykonania jest większy,
oblicza czy odległość od położenia jest mniejsza od danego miejsca. Korzystam z gotowej
biblioteki pythonowskiej i założyłem, że do budynku musi być mniej niż 500 metrów, a do parków 
i większych placów musi być 800 metrów. Są to oczywiście parametry które można wprowadzać

Kod został ma również załączone 27 testy, które sprawdzają najważniejsze rzeczy.  Nie obejmują maina, ponieważ
main jest głównie do dowodzenia kodem i nic konkretnego nie robi. Kod również spełnia wymagania PEP - 8.
Za pomocą profilera znalazłem pewne miejsce, które wykonują się bardzo często,
są to głównie miejsce gdzie sprawdzam położenie autobusów i przystanków. Dla każdego autobusu muszę sprawdzić 
czy jego położenie jest równe położeniu przystanku. Złożoność tego skutkuje, że wykonuje się to tyle razy.
Analogiczny problem jest dla ekperymentu, aczkolwiek tam działa to o wiele szybciej. Udostępniłem mniej 
skuteczną opcję ze współrzędnymi w eksperymencie, głównie dlatego, że pierwsza działa stosunkowo wolno.
Za słabością w tym projekcie można uznać wykresy. Niestety jeżeli wybierzemy za małą wartość, to te wykresy
stają się bardzo nieczytelne, co uznaję za zrozumiałe , przy takiej liczbie danych.
