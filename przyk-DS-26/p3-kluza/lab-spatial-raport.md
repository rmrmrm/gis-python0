
# Raport

# Przetwarzanie i analiza danych przestrzennych 
# Oracle spatial


---

**Imiona i nazwiska:** Łukasz Kluza, Mateusz Sacha

--- 

Celem ćwiczenia jest zapoznanie się ze sposobem przechowywania, przetwarzania i analizy danych przestrzennych w bazach danych
(na przykładzie systemu Oracle spatial)

Swoje odpowiedzi wpisuj w miejsca oznaczone jako:

---
> Wyniki, zrzut ekranu, komentarz

```sql
--  ...
```

---

Do wykonania ćwiczenia (zadania 1 – 6) i wizualizacji danych wykorzystaj Oracle SQL Develper. Alternatywnie możesz wykonać analizy w środowisku Python/Jupyter Notebook

Do wykonania zadania 7 wykorzystaj środowisko Python/Jupyter Notebook

Raport należy przesłać w formacie pdf.

Należy też dołączyć raport zawierający kod w formacie źródłowym.

Np.
- plik tekstowy .sql z kodem poleceń
- plik .md zawierający kod wersji tekstowej
- notebook programu jupyter – plik .ipynb

Zamieść kod rozwiązania oraz zrzuty ekranu pokazujące wyniki, (dołącz kod rozwiązania w formie tekstowej/źródłowej)

Zwróć uwagę na formatowanie kodu

<div style="page-break-after: always;"></div>

# Zadanie 1

Zwizualizuj przykładowe dane

US_STATES


> Wyniki, zrzut ekranu, komentarz

```sql
SELECT  sdo_util.to_wktgeometry(geom) FROM us_states 
```

![alt text](_img/image-20.png)


US_INTERSTATES


> Wyniki, zrzut ekranu, komentarz

```sql
SELECT sdo_util.to_wktgeometry(geom) FROM us_interstates
```
![alt text](_img/image-21.png)

US_CITIES


> Wyniki, zrzut ekranu, komentarz

```sql
SELECT  sdo_util.to_wktgeometry(location) FROM us_cities
```
![alt text](_img/image-22.png)

US_RIVERS


> Wyniki, zrzut ekranu, komentarz

```sql
SELECT  sdo_util.to_wktgeometry(geom) FROM us_rivers
```
![alt text](_img/image-23.png)

US_COUNTIES


> Wyniki, zrzut ekranu, komentarz

```sql
SELECT  sdo_util.to_wktgeometry(geom) FROM us_counties
```

![alt text](_img/image-24.png)

US_PARKS


> Wyniki, zrzut ekranu, komentarz

```sql
SELECT sdo_util.to_wktgeometry(geom) FROM us_parks
```
![alt text](_img/image-25.png)

# Zadanie 2

Znajdź wszystkie stany (us_states) których obszary mają część wspólną ze wskazaną geometrią (prostokątem)

Pokaż wynik na mapie.

prostokąt

```sql
SELECT  sdo_geometry (2003, 8307, null,
sdo_elem_info_array (1,1003,3),
sdo_ordinate_array ( -117.0, 40.0, -90., 44.0)) g
FROM dual
```

> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-1.png)

> Mamy narysowany prostokąt jednak bez użycia jakiejkolwiek funkcji stany trzba by liczyć osobno co może być niedokładne.

Użyj funkcji SDO_FILTER

```sql
SELECT state, geom FROM us_states
WHERE sdo_filter (geom,
sdo_geometry (2003, 8307, null,
sdo_elem_info_array (1,1003,3),
sdo_ordinate_array ( -117.0, 40.0, -90., 44.0))
) = 'TRUE';
```

Zwróć uwagę na liczbę zwróconych wierszy (16)


> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-2.png)

> Wynik faktycznie zawiera 16 stanów, widać jednak że niektóre z nich są zaznaczone nieprawidłowo i w żaden sposób nie dotykają prostokąta.

Użyj funkcji  SDO_ANYINTERACT

```sql
SELECT state, geom FROM us_states
WHERE sdo_anyinteract (geom,
sdo_geometry (2003, 8307, null,
sdo_elem_info_array (1,1003,3),
sdo_ordinate_array ( -117.0, 40.0, -90., 44.0))
) = 'TRUE';
```

Porównaj wyniki sdo_filter i sdo_anyinteract

Pokaż wynik na mapie


> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-3.png)

![alt text](_img/image-4.png)

> Funkcja sdo_anyinteract poradziła sobie lepiej, poprawnie wskazując 14 stanów, które mają część wspólną z prostokątem, na porównaniu widać, że faktycznie dwa stany zostały oznaczone nadmiarowo przez funkcję sdo_filter.

# Zadanie 3

Znajdź wszystkie parki (us_parks) których obszary znajdują się wewnątrz stanu Wyoming

Użyj funkcji SDO_INSIDE

```sql
SELECT p.name, p.geom
FROM us_parks p, us_states s
WHERE s.state = 'Wyoming'
      AND SDO_INSIDE (p.geom, s.geom ) = 'TRUE';
```

W przypadku wykorzystywania narzędzia SQL Developer, w celu wizualizacji na mapie użyj podzapytania

```sql
SELECT pp.name, pp.geom FROM us_parks pp  
WHERE id IN  
(  
      SELECT p.id  
      FROM us_parks p, us_states s  
      WHERE s.state = 'Wyoming'  
            AND SDO_INSIDE (p.geom, s.geom ) = 'TRUE'  
)
```

> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-5.png)

> Widać parki znajdujące się w stanie Wyoming. Jest ich 32.

```sql
SELECT state, geom FROM us_states
WHERE state = 'Wyoming'
```

> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-6.png)

> Dorzucamy jeszcze kontur stanu tak aby było widać, że faktycznie są tylko parki narodowe znajdujące się w obrębie stanu.

Porównaj wynik z:

```sql
SELECT p.name, p.geom
FROM us_parks p, us_states s
WHERE s.state = 'Wyoming'
AND SDO_ANYINTERACT (p.geom, s.geom ) = 'TRUE';
```

W celu wizualizacji użyj podzapytania

> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-7.png)

> Funkcja sdo_anyinteract zaznaczyła wszystkie parki które znajdują się w stanie Wyoming a także wszystkie parki, jest ich 48.

![alt text](_img/image-8.png)

> Na porównaniu widać, że różnica między wynikami jest spora, szczególnie, że parki które są na graniach stanów są duże.

# Zadanie 4

Znajdź wszystkie jednostki administracyjne (us_counties) wewnątrz stanu New Hampshire

```sql
SELECT c.county, c.state_abrv, c.geom
FROM us_counties c, us_states s
WHERE s.state = 'New Hampshire'
AND SDO_RELATE ( c.geom,s.geom, 'mask=INSIDE+COVEREDBY') = 'TRUE';

SELECT c.county, c.state_abrv, c.geom
FROM us_counties c, us_states s
WHERE s.state = 'New Hampshire'
AND SDO_RELATE ( c.geom,s.geom, 'mask=INSIDE') = 'TRUE';

SELECT c.county, c.state_abrv, c.geom
FROM us_counties c, us_states s
WHERE s.state = 'New Hampshire'
AND SDO_RELATE ( c.geom,s.geom, 'mask=COVEREDBY') = 'TRUE';
```

W przypadku wykorzystywania narzędzia SQL Developer, w celu wizualizacji danych na mapie należy użyć podzapytania (podobnie jak w poprzednim zadaniu)

> Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-14.png)

> Maska Inside zwróicła 2 powiaty, maska Inside + Converdby łącznie 10 powiatów, a maska Touch - 11.

# Zadanie 5

Znajdź wszystkie miasta w odległości 50 mili od drogi (us_interstates) I4

Pokaż wyniki na mapie

```sql
SELECT * FROM us_interstates
WHERE interstate = 'I4'

SELECT * FROM us_states
WHERE state_abrv = 'FL'

SELECT c.city, c.state_abrv, c.location 
FROM us_cities c
WHERE ROWID IN 
( 
SELECT c.rowid
FROM us_interstates i, us_cities c 
WHERE i.interstate = 'I4'
AND sdo_within_distance (c.location, i.geom,'distance=50 unit=mile') = 'TRUE'
)
```

> Wyniki, zrzut ekranu, komentarz

```python
Wszystkie miasta w odległości do 50 mil od I4:
ROWID              CITY                 STATE  DISTANCE (km)
AABH/ZAAHAADNOHABA St Petersburg        FL     18.43 km
AABH/ZAAHAADNOHAA2 Tampa                FL     1.93 km
AABH/ZAAHAADNOHABn Orlando              FL     1.15 km
```

![alt text](_img/image-29.png)

Dodatkowo:


a)    Znajdz wszystkie drogi które przecinają rzekę Mississippi

b)    Znajdz wszystkie miasta w odlegości od 15 do 30 mil od drogi 'I275'

c)      Itp. (własne przykłady)


> Wyniki, zrzut ekranu, komentarz
> (dla każdego z podpunktów)

__a)__

Najpierw zapytanie o współrzędne rzeki **Mississippi**.
```sql
    SELECT sdo_util.to_wktgeometry(geom) 
    FROM us_rivers 
    WHERE name = 'Mississippi'
```
Później dodaję wszystkie drogi, które tą rzekę przecinają.

```sql
SELECT sdo_util.to_wktgeometry(i.geom), 
           i.interstate
    FROM us_interstates i, us_rivers r
    WHERE r.name = 'Mississippi'
      AND SDO_RELATE(i.geom, r.geom, 'mask=ANYINTERACT') = 'TRUE
```

```python
Drogi przecinające rzekę Mississippi:
- Autostrada I270
- Autostrada I74
- Autostrada I57
- Autostrada I10
- Autostrada I55
- Autostrada I20
- Autostrada I35E
- Autostrada I35W
- Autostrada I40
- Autostrada I255
- Autostrada I55/I70
- Autostrada I80
- Autostrada I94
- Autostrada I90
- Autostrada I494
```

![alt text](_img/image-30.png)

__b)__

Ponownie najpierw wyświetlenie interesującej nas drogi. (Ponieważ **I275** to tak naprawdę zbiór obwodnic więc na mapie widzimy trzy różne kształty)
```sql
    SELECT sdo_util.to_wktgeometry(geom) 
    FROM us_interstates  
    WHERE interstate = 'I275'
```

Póżniej dodanie miast spełniających kryteria:

```sql
    SELECT sdo_util.to_wktgeometry(c.location), 
           c.city
    FROM us_cities c, us_interstates i
    WHERE i.interstate = 'I275'
      AND SDO_WITHIN_DISTANCE(c.location, i.geom, 'distance=30 unit=mile') = 'TRUE'
      AND SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.5, 'unit=mile') >= 15
```

![alt text](_img/image-31.png)

```python
Miasta znajdujące się w pobliżu autostrady I275:
- Toledo
- Detroit
- Warren
- Sterling Heights
```

c)
**Analiza nuklearna:** Poniższa mapa przedstawia symulację stref skażenia tylko i wyłącznie w celach informacyjnych.

* **Obszar czerwony (do 40 mil):** Strefa bezwzględnego zagrożenia życia. Przebywanie w tym sektorze w ciągu pierwszej doby od momentu zdarzenia wiąże się z otrzymaniem śmiertelnej dawki promieniowania.
* **Obszar pomarańczowy (do 120 mil):** Strefa wysokiego ryzyka i zagrożenia zdrowia.

![alt text](_img/image-32.png)


# Zadanie 6

Znajdz 5 miast najbliższych drogi I4

```sql
SELECT c.city, c.state_abrv, c.location
FROM us_interstates i, us_cities c 
WHERE i.interstate = 'I4'
AND sdo_nn(c.location, i.geom, 'sdo_num_res=5') = 'TRUE';
```

>Wyniki, zrzut ekranu, komentarz

![alt text](_img/image-9.png)

> Znalezione miasta to:
> * Orlando, FL – 1.8 km
> * Tampa, FL – 3.1 km  
> * St Petersburg, FL – 29.7 km
> * Jacksonville, FL – 142.3 km
> * Fort Lauderdale, FL – 275.8 km

Dodatkowo:

a) Podaj 3 parki narodowe do których jest najbliżej z Nowego Jorku, oblicz odległości do tych parków

b) Znajdz 5 najbliższych dużych miast (o populacji powyżej 300 tys) od drogi  'I170'

c)  Itp. (własne przykłady). 
- np. przetestuj działanie funkcji 
	- sdo_intersection, sdo_union, sdo_difference
	- sdo_buffer
	- sdo_centroid, sdo_mbr, sdo_convexhull, sdo_simplify


> Wyniki, zrzut ekranu, komentarz
> (dla każdego z podpunktów)

a)

![alt text](_img/image-10.png)

> Z racji, że Nowy Jork jest oznaczony konkretną współrzędną to 3 najbliższe parki narodowe znajdują się w Nowym Jorku:
> * Institute Park – 1.5 km
> * Prospect Park – 1.7 km
> * Thompkins Park – 2.1 km

b)

![alt text](_img/image-11.png)

> Znalezionych 5 najbliższych dużych miast o populacji powyżej 300 tys to:
> * St Louis, MO – 8.6 km
> * Springfield, IL – 126.8 km
> * Peoria, IL – 227.7 km
> * Evansville, IN – 254.6 km
> * Springfield, MO – 303.4 km

c)

> Pierwszą funckją, którą wypróbuję będzię sdo_bufer - która wokół danego obiektu tworzy obszar o wybranej szerokości.

![alt text](_img/image-12.png)

> Wybrałem bufor o szerokości 80km, widać że funkcja dobrze sobie z tym poradziła, oznaczjąc nawet część wody, ponieważ znajdowała się w obszarze.

---

> Kolejną funkcją będzie sdo_convexhull - która dla danej geometrii zwraca jej otoczkę wypukłą, czyli najmniejszy wypukły poligon, który całkowicie ją otacza.

![alt text](_img/image-13.png)

> Można zobaczyć, że faktycznie poligon idealnie otacza stan Michigan, razem z wodą znajdującą się miedzy wyspami. Jest do znacznie większy obszar niż sam stan.

# Zadanie 7

### 7a Mapa dostępu do głównych rzek w USA
Najpierw zdefiniowałem 15 największych rzek w USA i naniosłem je na mapę

```sql
SELECT sdo_util.to_wktgeometry(geom) FROM us_rivers WHERE name IN 
    ('Missouri', 'Mississippi', 'Yukon', 'Rio Grande', 'Colorado', 
    'Arkansas', 'Columbia', 'Ohio', 'Red River', 'Tennessee', 'Snake', 
    'Tennessee', 'Canadian', 'Brazos', 'Green', 'Pecos')
```

W kolejnym etapie za pomocą operacji `SDO_GEOM.SDO_DIFFERENCE` wyznaczyłem strefę buforową w kształcie pierścienia, która zobrazowała zewnętrzny obszar dostępności do rzek w zakresie od 50 do 150 mil.

```sql
SELECT sdo_util.to_wktgeometry(
      SDO_GEOM.SDO_DIFFERENCE(
            SDO_GEOM.SDO_BUFFER(SDO_AGGR_UNION(SDOAGGRTYPE(geom, 0.5)), 150, 0.5, 'unit=mile'),
            SDO_GEOM.SDO_BUFFER(SDO_AGGR_UNION(SDOAGGRTYPE(geom, 0.5)), 50, 0.5, 'unit=mile'),
            0.5
      )
)
FROM us_rivers
WHERE name IN ('Missouri', 'Mississippi', 'Yukon', 'Rio Grande', 'Colorado', 
'Arkansas', 'Columbia', 'Ohio', 'Red River', 'Tennessee', 'Snake', 
'Tennessee', 'Canadian', 'Brazos', 'Green', 'Pecos')
```

W ostatnim kroku dołożyłem strefę buforową o rozpiętości 50 mil.

```sql
SELECT sdo_util.to_wktgeometry(
        SDO_GEOM.SDO_BUFFER(SDO_AGGR_UNION(SDOAGGRTYPE(geom, 0.5)), 50, 0.5, 'unit=mile')
    )
    FROM us_rivers
    WHERE name IN ('Missouri', 'Mississippi', 'Yukon', 'Rio Grande', 'Colorado', 
    'Arkansas', 'Columbia', 'Ohio', 'Red River', 'Tennessee', 'Snake', 
    'Tennessee', 'Canadian', 'Brazos', 'Green', 'Pecos')
```

![alt text](_img/image-26.png)

### 7b Mapa parków atrakcyjnych dla kierowców

Najpierw naniosłem na mapę granicę stanów aby wyniki były bardzej czytelne.

```sql
SELECT sdo_util.to_wktgeometry(geom) FROM us_states
```

Później znalazłem trójstyki stanów, aby to osiągnąc musiałem dwa razy skorzystać z `SDO_GEOM.SDO_INTERSECTION`. Pierwsze użycie posłużyło temu aby znależć część współną (linię) między dwoma stanami. Z kolei drugie użycie `SDO_GEOM.SDO_INTERSECTION` dołozyło to tego trzeci punkt (stan). 

```sql
SELECT sdo_util.to_wktgeometry(
               SDO_GEOM.SDO_INTERSECTION(
                   SDO_GEOM.SDO_INTERSECTION(s1.geom, s2.geom, 0.5),
                   s3.geom, 
                   0.5
               )
           ),
           s1.state_abrv, s2.state_abrv, s3.state_abrv
    FROM us_states s1, us_states s2, us_states s3
    WHERE s1.state_abrv < s2.state_abrv 
      AND s2.state_abrv < s3.state_abrv
      AND sdo_relate(s1.geom, s2.geom, 'mask=TOUCH') = 'TRUE'
      AND sdo_relate(s2.geom, s3.geom, 'mask=TOUCH') = 'TRUE'
      AND sdo_relate(s1.geom, s3.geom, 'mask=TOUCH') = 'TRUE'
```
Taka mapa może być ciekawą inspiracja dla osób szukajacych fascynujących miejsc do odwiedzenia.
![alt text](_img/image-27.png)

### 7c Poszukiwanie odpowiednich miast do stworzenia hubu logistycznego

__Założenia:__
- Miasto powinno znajdować się w stanie `Floryda` lub `Georgia`
- Do najbliższej autostrady powinno być niewięcej niż `15 mil` (transport lądowy)
- Do najbliższej rzeki również powinno być niewięcej niż `15 mil` (transport wodny)

__Zapytanie__
Zapytanie składa się z dwóch podzapytań pomocniczych oraz zapytania głównego. Pierwsze podzapytanie odpowiada za wyciągnięcie wszystkich autostrad, które znajdują się w stanach `Floryda` lub `Georgia`, i wygenerowanie wokół nich 15-milowego bufora. Podobne zadanie ma drugie podzapytanie, z tą różnicą, że skupia się ono na rzekach. Zapytanie główne rozpoczyna analizę od znalezienia miast z dwóch wyżej wymienionych stanów, a następnie za pomocą operatorów przestrzennych sprawdza, które z nich leżą jednocześnie w obszarach wyznaczonych przez oba podzapytania.

```sql
    WITH highway_buf AS (
        SELECT SDO_AGGR_UNION(SDOAGGRTYPE(SDO_GEOM.SDO_BUFFER(i.geom, 15, 0.5, 'unit=mile'), 0.5)) AS geom
        FROM us_interstates i, us_states s
        WHERE s.state_abrv IN ('FL', 'GA')
          AND sdo_anyinteract(i.geom, s.geom) = 'TRUE'
    ),
    river_buf AS (
        SELECT SDO_AGGR_UNION(SDOAGGRTYPE(SDO_GEOM.SDO_BUFFER(r.geom, 15, 0.5, 'unit=mile'), 0.5)) AS geom
        FROM us_rivers r, us_states s
        WHERE s.state_abrv IN ('FL', 'GA')
          AND sdo_anyinteract(r.geom, s.geom) = 'TRUE'
    )
    SELECT c.city, 
           c.state_abrv,
           sdo_util.to_wktgeometry(c.location),
           sdo_util.to_wktgeometry(h.geom),
           sdo_util.to_wktgeometry(r.geom)
    FROM us_cities c, highway_buf h, river_buf r, us_states s
    WHERE s.state_abrv IN ('FL', 'GA')
      AND sdo_anyinteract(c.location, s.geom) = 'TRUE' 
      AND sdo_anyinteract(c.location, h.geom) = 'TRUE'
      AND sdo_anyinteract(c.location, r.geom) = 'TRUE'
```

![alt text](_img/image-28.png)
Miasta wytypowane jako Huby Logistyczne:
- Jacksonville, FL
- Savannah, GA
- Atlanta, GA
  
---

Punktacja

|       |     |
| ----- | --- |
| zad   | pkt |
| 1     | 0,5 |
| 2     | 0,5 |
| 3     | 0,5 |
| 4     | 0,5 |
| 5     | 1   |
| 6     | 2   |
| 7     | 2   |
| razem | 7   |
