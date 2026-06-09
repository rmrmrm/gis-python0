
# Raport

# Przetwarzanie i analiza danych przestrzennych 
# Oracle spatial


---

**Imiona i nazwiska:** Jan Dworak, Miłosz Słowiński

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

![US_STATES — wizualizacja mapowa](imgs/1.1.png)

```sql
SELECT id, state, geom FROM us_states;
```

Wynik pokazuje 51 stanów USA (w tym DC) jako wielokąty na mapie. Widać pełny zarys granic państwa — od wybrzeża Pacyfiku po Atlantyk, z wyraźnie odseparowanymi Hawajami i Alaską.


US_INTERSTATES


> Wyniki, zrzut ekranu, komentarz

![US_INTERSTATES — widok ogólny](imgs/1.2.1.png)

![US_INTERSTATES — powiększenie](imgs/1.2.2.png)

```sql
SELECT id, interstate, geom FROM us_interstates;
```

Autostrady międzystanowe (I-xx) tworzą sieć liniową łączącą główne ośrodki miejskie. Na mapie widać gęstą siatkę na wschodzie i rzadsze połączenia na zachodzie; drugi zrzut pokazuje szczegóły fragmentu sieci.


US_CITIES


> Wyniki, zrzut ekranu, komentarz

![US_CITIES — widok ogólny](imgs/1.3.1.png)

![US_CITIES — powiększenie](imgs/1.3.2.png)

```sql
SELECT id, city, state_abrv, location FROM us_cities;
```

Miasta reprezentowane są punktami (`SDO_POINT_TYPE`). Rozkład jest nierównomierny — największe skupienie na wschodzie i wybrzeżu, mniej punktów w górach i na pustyni.


US_RIVERS


> Wyniki, zrzut ekranu, komentarz

![US_RIVERS — rzeki USA](imgs/1.4.png)

```sql
SELECT id, name, geom FROM us_rivers;
```

Rzeki zapisane jako linie (`SDO_LINE_TYPE`) tworzą naturalną sieć hydrograficzną — widać m.in. Missisipi z dopływami, Kolorado i rzeki wybrzeża wschodniego.


US_COUNTIES


> Wyniki, zrzut ekranu, komentarz

![US_COUNTIES — hrabstwa](imgs/1.5.png)

```sql
SELECT id, county, state_abrv, geom FROM us_counties;
```

Hrabstwa (powiaty) to wielokąty tworzące najdrobniejszą warstwę administracyjną — na mapie widać gęstą mozaikę granic, szczególnie na wschodzie USA.


US_PARKS


> Wyniki, zrzut ekranu, komentarz

![US_PARKS — parki narodowe](imgs/1.6.png)

```sql
SELECT id, name, geom FROM us_parks;
```

Parki narodowe i obszary chronione rozłożone są nierównomiernie — większe kompleksy w górach Zachodu (Yellowstone, Yosemite), mniejsze enklawy na wschodzie.


# Zadanie 2

Znajdź wszystkie stany (us_states) których obszary mają część wspólną ze wskazaną geometrią (prostokątem)

Pokaż wynik na mapie.

prostokąt

```sql
SELECT sdo_geometry (2003, 8307, null,
sdo_elem_info_array (1,1003,3),
sdo_ordinate_array ( -117.0, 40.0, -90., 44.0)) g
FROM dual
```



> Wyniki, zrzut ekranu, komentarz

Prostokąt obejmuje pas od Kalifornii do środkowego Zachodu (lon -117…-90, lat 40…44).


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

![Zad. 2 — SDO_FILTER (16 wierszy)](imgs/2.1.png)

```sql
-- SDO_FILTER zwraca 16 stanów. Funkcja wykorzystuje indeks R-tree (MBR) —
-- szybki filtr wstępny; może zwrócić fałszywe trafienia, gdy prostokąt
-- ograniczający stan przecina prostokąt zapytania, ale geometria właściwa nie.
```


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

![Zad. 2 — SDO_ANYINTERACT (14 wierszy)](imgs/2.2.png)

```sql
-- SDO_ANYINTERACT zwraca 14 stanów — dokładna relacja przestrzenna.
-- SDO_FILTER (16) zwrócił 2 stany więcej (fałszywe trafienia MBR).
-- ANYINTERACT odrzuca stany, których MBR przecina prostokąt, lecz geometria nie.
```

![Zad. 2 — porównanie wyników](imgs/2.3.png)

```sql
-- Różnica: FILTER = szybki, przybliżony; ANYINTERACT = wolniejszy, precyzyjny.
-- W praktyce FILTER stosuje się jako prefiltr przed dokładną analizą.
```

![Zad. 2 — mapa stanów i prostokąta](imgs/2.4.png)

```sql
SELECT state, geom FROM us_states
WHERE sdo_anyinteract (geom,
  sdo_geometry (2003, 8307, null,
    sdo_elem_info_array (1,1003,3),
    sdo_ordinate_array ( -117.0, 40.0, -90., 44.0))
) = 'TRUE'
UNION ALL
SELECT 'RECT' AS state,
  sdo_geometry (2003, 8307, null,
    sdo_elem_info_array (1,1003,3),
    sdo_ordinate_array ( -117.0, 40.0, -90., 44.0)) AS geom
FROM dual;
```

Na mapie widać zaznaczone stany nachodzące na prostokąt zapytania w pasie Rocky Mountains / Wielkich Równin.


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

![Zad. 3 — parki SDO_INSIDE w Wyoming (32)](imgs/3.1.png)

```sql
-- SDO_INSIDE zwraca 32 parki całkowicie zawarte w granicach Wyoming
-- (Yellowstone, Grand Teton, Shoshone NF itd.).
-- Podzapytanie na id umożliwia poprawną wizualizację w SQL Developer Map Viewer.
```


```sql
SELECT state, geom FROM us_states
WHERE state = 'Wyoming'
```



> Wyniki, zrzut ekranu, komentarz

![Zad. 3 — granice stanu Wyoming](imgs/3.2.png)

```sql
-- Wizualizacja samego stanu Wyoming jako kontekst dla parków z poprzedniego zapytania.
```


Porównaj wynik z:

```sql
SELECT p.name, p.geom
FROM us_parks p, us_states s
WHERE s.state = 'Wyoming'
AND SDO_ANYINTERACT (p.geom, s.geom ) = 'TRUE';
```

W celu wizualizacji użyj podzapytania



> Wyniki, zrzut ekranu, komentarz

![Zad. 3 — parki SDO_ANYINTERACT (46)](imgs/3.3.png)

```sql
SELECT pp.name, pp.geom FROM us_parks pp
WHERE id IN (
  SELECT p.id FROM us_parks p, us_states s
  WHERE s.state = 'Wyoming'
    AND SDO_ANYINTERACT (p.geom, s.geom) = 'TRUE'
);
```

```sql
-- SDO_ANYINTERACT zwraca 46 parków — o 14 więcej niż SDO_INSIDE (32).
-- Dodatkowe parki leżą na granicy stanu lub częściowo wchodzą w sąsiednie stany
-- (np. fragment Yellowstone w Montanie/Idaho). INSIDE wymaga pełnego zawarcia.
```


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

![Zad. 4 — hrabstwa New Hampshire, trzy maski SDO_RELATE](imgs/4.1.png)

```sql
-- mask=INSIDE+COVEREDBY: 10 hrabstw (unia obu relacji)
-- mask=INSIDE:            2 hrabstwa (całkowicie wewnątrz NH)
-- mask=COVEREDBY:         8 hrabstw (w całości pokryte przez NH lub stykające się)

SELECT cc.county, cc.state_abrv, cc.geom FROM us_counties cc
WHERE id IN (
  SELECT c.id FROM us_counties c, us_states s
  WHERE s.state = 'New Hampshire'
    AND SDO_RELATE (c.geom, s.geom, 'mask=INSIDE+COVEREDBY') = 'TRUE'
);
```

```sql
-- INSIDE jest najwęższa (tylko w pełni zawarte). COVEREDBY szersza — obejmuje
-- hrabstwa leżące w całości w NH lub na granicy. INSIDE+COVEREDBY = suma obu.
-- New Hampshire ma 10 hrabstw, więc INSIDE+COVEREDBY zwraca wszystkie.
```

# Zadanie 5

Znajdź wszystkie miasta w odległości 50 mili od drogi (us_interstates) I4

Pokaż wyniki na mapie

Analiza wykonana w Pythonie (Folium + oracledb). Kod: [zad5.py](zad5.py)


> Wyniki, zrzut ekranu, komentarz

![Zad. 5 — miasta w 50 mi od I-4 (Python/Folium)](imgs/5.1.png)

```sql
SELECT c.city, c.state_abrv, c.location
FROM us_cities c
WHERE ROWID IN (
  SELECT c.rowid
  FROM us_interstates i, us_cities c
  WHERE i.interstate = 'I4'
    AND sdo_within_distance(c.location, i.geom, 'distance=50 unit=mile') = 'TRUE'
);
```

```sql
-- SDO_WITHIN_DISTANCE zwraca 3 miasta w promieniu 50 mil od I-4:
-- Orlando, St Petersburg, Tampa (wszystkie FL).
-- I-4 biegnie przez centralną Florydę; inne duże miasta (np. Jacksonville)
-- leżą poza tym promieniem od tej autostrady.
```


Dodatkowo:


a) Znajdz wszystkie drogi które przecinają rzekę Mississippi

b) Znajdz wszystkie miasta w odlegości od 15 do 30 mil od drogi 'I275'

c) Itp. (własne przykłady)


> Wyniki, zrzut ekranu, komentarz
> (dla każdego z podpunktów)

**a)** ![Zad. 5a — drogi i Mississippi](imgs/5a.png)

```sql
SELECT i.interstate
FROM us_interstates i, us_rivers r
WHERE r.name = 'Mississippi'
  AND SDO_ANYINTERACT(i.geom, r.geom) = 'TRUE'
ORDER BY i.interstate;
```

```sql
-- 15 autostrad przecina rzekę Mississippi (I10, I20, I40, I55, I90 itd.).
-- SDO_ANYINTERACT wykrywa wspólną geometrię linii drogi i rzeki.
```

**b)** ![Zad. 5b — miasta 15–30 mi od I-275](imgs/5b.png)

```sql
SELECT c.city, c.state_abrv,
       ROUND(SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE'), 1) AS dist_mile
FROM us_interstates i, us_cities c
WHERE i.interstate = 'I275'
  AND sdo_within_distance(c.location, i.geom, 'distance=30 unit=mile') = 'TRUE'
  AND SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE') > 15
ORDER BY dist_mile;
```

```sql
-- 4 miasta w pierścieniu 15–30 mil od I-275: Detroit (16.9 mi),
-- Warren (21.8), Sterling Heights (24.3), Toledo (26.2).
-- Oracle nie obsługuje SDO_WITHIN_DISTANCE = 'FALSE' — użyto SDO_DISTANCE > 15.
```

**c)** ![Zad. 5c — miasta w 300 mi od Yellowstone NP](imgs/5c.png)

```sql
SELECT c.city, c.state_abrv
FROM us_cities c, us_parks p
WHERE p.name = 'Yellowstone NP'
  AND sdo_within_distance(c.location, p.geom, 'distance=300 unit=mile') = 'TRUE';
```

```sql
-- W promieniu 300 mil od Yellowstone NP tylko 2 miasta: Salt Lake City i Boise City.
-- Najbliższe duże miasto (Salt Lake City) jest w ~236 mil — stąd brak wyników dla 100 mil.
```


# Zadanie 6

Znajdz 5 miast najbliższych drogi I4

Analiza wykonana w Pythonie. Kod: [zad6.py](zad6.py)


>Wyniki, zrzut ekranu, komentarz

![Zad. 6 — 5 miast najbliżej I-4 (SDO_NN)](imgs/6.1.png)

```sql
SELECT c.city, c.state_abrv, c.location
FROM us_interstates i, us_cities c
WHERE i.interstate = 'I4'
  AND sdo_nn(c.location, i.geom, 'sdo_num_res=5') = 'TRUE';
```

```sql
-- SDO_NN zwraca 5 najbliższych miast wzdłuż I-4:
-- Fort Lauderdale, Jacksonville, Orlando, St Petersburg, Tampa.
-- Operator NN korzysta z indeksu przestrzennego — wydajne wyszukiwanie KNN.
```


Dodatkowo:


a) Podaj 3 parki narodowe do których jest najbliżej z Nowego Jorku, oblicz odległości do tych parków

b) Znajdz 5 najbliższych dużych miast (o populacji powyżej 300 tys) od drogi 'I170'

c) Itp. (własne przykłady)


>Wyniki, zrzut ekranu, komentarz
> (dla każdego z podpunktów)

**a)** ![Zad. 6a — 3 parki narodowe najbliżej NYC](imgs/6a.png)

```sql
SELECT name, dist_mile FROM (
  SELECT p.name,
         ROUND(SDO_GEOM.SDO_DISTANCE(c.location, p.geom, 0.005, 'unit=MILE'), 1) AS dist_mile
  FROM us_parks p, us_cities c
  WHERE c.city = 'New York' AND c.state_abrv = 'NY'
    AND p.name LIKE '% NP'
  ORDER BY dist_mile
) WHERE ROWNUM <= 3;
```

```sql
-- 3 najbliższe parki narodowe od NYC: Shenandoah NP (255.9 mi),
-- Acadia NP (354.8 mi), Great Smoky Mountains NP (601.2 mi).
-- Filtrowanie po sufiksie ' NP' wyklucza lokalne parki miejskie.
-- Odległości obliczone funkcją SDO_GEOM.SDO_DISTANCE.
```

**b)** ![Zad. 6b — duże miasta przy I-170](imgs/6b.png)

```sql
SELECT city, state_abrv, pop90, dist_mile FROM (
  SELECT c.city, c.state_abrv, c.pop90,
         ROUND(SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE'), 1) AS dist_mile
  FROM us_cities c, us_interstates i
  WHERE i.interstate = 'I170'
    AND c.pop90 > 300000
    AND SDO_NN(c.location, i.geom, 'sdo_num_res=100') = 'TRUE'
  ORDER BY dist_mile
) WHERE ROWNUM <= 5;
```

```sql
-- 5 najbliższych dużych miast (pop90 > 300k) przy I-170:
-- St Louis (5.4 mi), Kansas City (227.4 mi), Indianapolis (234.7 mi),
-- Memphis (244.2 mi), Chicago (253.5 mi).
-- Kolumna populacji to POP90 (spis 1990). Przy sdo_num_res=5 NN zwracał
-- tylko 1 miasto — zwiększono parametr i posortowano po SDO_DISTANCE.
```

**c)** ![Zad. 6c — SDO_BUFFER wokół Denver (20 mi)](imgs/6c.png)

```sql
SELECT c.city,
       ROUND(SDO_GEOM.SDO_LENGTH(
         SDO_GEOM.SDO_BUFFER(c.location, 20, 0.005, 'unit=MILE'),
         0.005, 'unit=MILE'), 1) AS buffer_perimeter_mile
FROM us_cities c
WHERE c.city = 'Denver' AND c.state_abrv = 'CO';
```

```sql
-- SDO_BUFFER tworzy okrąg o promieniu 20 mil wokół Denver.
-- Obwód bufora ≈ 125.7 mil (2πr). Na mapie widać punkt miasta i wielokąt bufora.
-- Funkcja przydatna do analiz stref wpływu (np. zasięg usług od punktu).
```


# Zadanie 7

Wykonaj kilka własnych przykładów/analiz

Analiza wykonana w Pythonie (Folium + oracledb). Kod: [zad7.py](zad7.py)


>Wyniki, zrzut ekranu, komentarz

**7.1** ![Zad. 7.1 — SDO_CONTAINS: Austin w Teksasie](imgs/7.1.png)

```sql
SELECT c.city,
       SDO_CONTAINS(s.geom, c.location) AS inside_texas
FROM us_cities c, us_states s
WHERE c.city = 'Austin' AND c.state_abrv = 'TX'
  AND s.state = 'Texas';
```

```sql
-- SDO_CONTAINS zwraca TRUE — Austin leży w granicach Teksasu.
-- Funkcja sprawdza, czy wielokąt stanu zawiera punkt miasta (test „punkt w poligonie”).
```

**7.2** ![Zad. 7.2 — SDO_TOUCH: sąsiedzi Arizony](imgs/7.2.png)

```sql
SELECT s2.state
FROM us_states s1, us_states s2
WHERE s1.state = 'Arizona'
  AND s2.state <> 'Arizona'
  AND SDO_TOUCH(s1.geom, s2.geom) = 'TRUE'
ORDER BY s2.state;
```

```sql
-- SDO_TOUCH zwraca 5 stanów graniczących z Arizoną:
-- California, Colorado, Nevada, New Mexico, Utah (punkt Four Corners).
-- Relacja TOUCH wymaga wspólnej krawędzi, ale bez nachodzenia obszarów.
```

**7.3** ![Zad. 7.3 — SDO_AREA: Yellowstone vs Yosemite](imgs/7.3.png)

```sql
SELECT name,
       ROUND(SDO_GEOM.SDO_AREA(geom, 0.005, 'unit=SQ_MILE'), 0) AS area_sq_mile
FROM us_parks
WHERE name IN ('Yellowstone NP', 'Yosemite NP')
ORDER BY area_sq_mile DESC;
```

```sql
-- Yellowstone NP (3435 mi²) jest ~3× większy od Yosemite NP (1170 mi²).
-- SDO_GEOM.SDO_AREA oblicza powierzchnię wielokąta w wybranej jednostce.
```

**7.4** ![Zad. 7.4 — SDO_INTERSECTION: I-80 w Nebraska](imgs/7.4.png)

```sql
SELECT ROUND(SDO_GEOM.SDO_LENGTH(
         SDO_GEOM.SDO_INTERSECTION(i.geom, s.geom),
         0.005, 'unit=MILE'), 1) AS i80_len_in_ne
FROM us_interstates i, us_states s
WHERE i.interstate = 'I80' AND s.state = 'Nebraska';
```

```sql
-- SDO_INTERSECTION wycina fragment linii I-80 wewnątrz Nebraska (455.3 mi).
-- SDO_LENGTH mierzy długość tego przecięcia — przydatne przy analizie infrastruktury w granicach administracyjnych.
```

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
