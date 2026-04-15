# ICE Middleware - Laboratorium 3 - Odpowiedzi i Dokumentacja

## Sekcja 2.2 - ZeroC ICE

### Zadanie 1-2: Analiza projektu i pliku ICE

**Zawartość pliku `slice/calculator.ice`:**
- Moduł `Demo` zawierający:
  - Enum `operation` z wartościami MIN, MAX, AVG
  - Wyjątek `NoInput` (bez parametrów)
  - Strukturę `A` z polami: short a, long b, float c, string d
  - Interfejs `Calc` z operacjami: add, subtract, op

**Status:** ✅ Przeanalizowano

---

### Zadanie 3: Kompilacja pliku .ice

**Polecenia kompilacji dla różnych języków:**

1. **Java:**
   ```bash
   slice2java --output-dir generated slice/calculator.ice
   ```

2. **Python:**
   ```bash
   slice2py --output-dir generated slice/calculator.ice
   ```

3. **C++:**
   ```bash
   slice2cpp --output-dir generated slice/calculator.ice
   ```

**Wynik:** Generowane są pliki źródłowe w katalogu `generated/Demo/`:
- `Calc.java` - interfejs
- `CalcPrx.java` - proxy
- `_CalcPrxI.java` - implementacja proxy
- `A.java` - struktura
- `NoInput.java` - wyjątek
- `operation.java` - enum

**Zmiany w kodzie:** Brak (tylko kompilacja)

---

### Zadanie 4: Analiza wygenerowanego kodu

**Struktura katalogów:**
- `slice/` - definicje interfejsów IDL
- `generated/Demo/` - wygenerowany kod Java
- `src/sr/ice/` - kod źródłowy aplikacji (client, server)

**Klasy w katalogu generated:**
- `Calc` - interfejs serwanta (pochodzi z nazwy interfejsu w .ice)
- `CalcPrx` - proxy klienta (Prx = Proxy)
- `_CalcPrxI` - wewnętrzna implementacja proxy
- `A` - klasa struktury (nazwa z .ice)
- `NoInput` - klasa wyjątku (nazwa z .ice)
- `operation` - enum (nazwa z .ice)

**Pochodzenie nazw:** Nazwy klas pochodzą bezpośrednio z definicji w pliku .ice, z dodaniem sufiksów:
- Interfejsy → nazwa bez zmian
- Proxy → nazwa + "Prx"
- Implementacja proxy → "_" + nazwa + "PrxI"

---

### Zadanie 5: Analiza kodu źródłowego

**Kolejność analizy:**

1. **CalcI.java (serwant):**
   - Implementuje interfejs `Demo.Calc`
   - Metoda `add()` - dodawanie z opóźnieniem dla dużych wartości (>1000)
   - Metoda `subtract()` - zwraca 0 (do implementacji)
   - Metoda `op()` - operacja z opóźnieniem 500ms
   - Parametr `Current` zawiera kontekst wywołania

2. **IceServer.java (serwer):**
   - Inicjalizacja Communicator
   - Tworzenie ObjectAdapter (z pliku config lub hardcoded)
   - Tworzenie serwantów: `calcServant1`, `calcServant2`
   - Dodawanie do ASM: Identity("calc11", "calc"), Identity("calc22", "calc")
   - Aktywacja adaptera i pętla przetwarzania

3. **IceClient.java (klient):**
   - Inicjalizacja Communicator
   - Uzyskanie proxy przez `propertyToProxy()` lub `stringToProxy()`
   - Rzutowanie do `CalcPrx`
   - Menu interaktywne z różnymi trybami wywołań

---

### Zadanie 6: Uruchomienie serwera i analiza gniazd

**Gniazda używane przez serwer:**
- TCP: 127.0.0.2:10000 (lub 0.0.0.0:10010 z pliku config)
- UDP: 127.0.0.2:10000 (lub 0.0.0.0:10010 z pliku config)

**Polecenia sprawdzające:**
```bash
# Linux/macOS
netstat -ano | grep 10000
lsof -i :10000

# Windows
netstat -ano | findstr 10000
```

**Alternatywnie:**
```bash
ss -tulpn | grep 10000  # Linux
```

---

### Zadanie 7: Implementacja operacji subtract

**Zmiany w kodzie:** Zobacz `CalcI.java` - metoda subtract

**Kod:**
```java
@Override
public long subtract(int a, int b, Current __current) {
    System.out.println("SUBTRACT: a = " + a + ", b = " + b + ", result = " + (a - b));
    return a - b;
}
```

**Test:** Wywołanie `subtract` w kliencie zwraca poprawny wynik (a - b)

---

### Zadanie 8: Pytania o serwanty i obiekty

**Q1: Jak nazywają się zmienne wskazujące na serwantów?**
- `calcServant1` (typu CalcI)
- `calcServant2` (typu CalcI)

**Q2: Ile obiektów udostępnia serwer i jak się nazywają?**
- 2 obiekty ICE:
  - `calc/calc11` (kategoria/nazwa)
  - `calc/calc22` (kategoria/nazwa)

**Q3: Z którym obiektem ICE skomunikował się klient?**
- `calc/calc11` (pierwszy obiekt zdefiniowany w stringToProxy lub w pliku config)

**Q4: Ile wpisów zawiera tablica ASM adaptera? Czy odwzorowanie 1:1?**
- 2 wpisy w ASM (Active Servant Map)
- Odwzorowanie NIE jest 1:1 - możliwe jest mapowanie wielu obiektów na jednego serwanta

**Q5: Z którym serwantem Java komunikował się klient?**
- `calcServant1` (pierwszy dodany do adaptera z Identity "calc11")

**Q6: W jaki sposób klient uzyskał referencję?**
Referencja zawiera:
- Kategorię i nazwę obiektu: `calc/calc11`
- Endpoint(y): `tcp -h 127.0.0.2 -p 10000 -z : udp -h 127.0.0.2 -p 10000 -z`
- Format: `category/name:protocol -h host -p port [options]`

**Q7: Co się stanie przy wywołaniu nieistniejącego obiektu?**
- Klient otrzyma wyjątek `ObjectNotExistException`
- Serwer nie znajdzie obiektu w ASM i zwróci błąd

---

### Zadanie 9: Wiele obiektów, wspólny serwant

**Zmiany w kodzie:** Zobacz `IceServer.java`

**Dodany kod:**
```java
// Strategia: wiele obiektów, wspólny serwant
adapter.add(calcServant1, new Identity("calc33", "calc"));
```

**Wynik:**
- Obiekt `calc/calc33` używa tego samego serwanta co `calc/calc11`
- Serwant może sprawdzić dla jakiego obiektu działa przez: `__current.id.name` i `__current.id.category`

**Test w servancie:**
```java
System.out.println("Serving object: " + __current.id.category + "/" + __current.id.name);
```

---

### Zadanie 10: Wiele obiektów, dedykowane serwanty

**Zmiany w kodzie:** Zobacz `IceServer.java`

**Dodany kod:**
```java
// Strategia: wiele obiektów, każdy z dedykowanym serwantem
CalcI calcServant3 = new CalcI();
adapter.add(calcServant3, new Identity("calc33", "calc"));
```

**Wynik:**
- Każdy obiekt ma własnego serwanta
- Możliwe jest utrzymywanie osobnego stanu dla każdego obiektu
- Większe zużycie pamięci, ale lepsza izolacja

---

### Zadanie 11: Analiza komunikacji sieciowej (Wireshark)

**Filtr Wireshark:**
```
ip.addr==127.0.0.2 or tcp.port==10000 or udp.port==10000
```

**Czy Wireshark rozumie protokół Ice?**
- TAK - Wireshark ma wbudowany dissector dla protokołu Ice
- Pokazuje strukturę wiadomości: nagłówki, typy operacji, parametry

**Informacje w żądaniu:**
- Magic number (Ice protocol)
- Protocol version
- Encoding version
- Message type (Request)
- Request ID
- Object Identity (category + name)
- Facet
- Operation name
- Operation mode
- Context
- Parametry (zakodowane)

**Informacje w odpowiedzi:**
- Request ID (korelacja z żądaniem)
- Reply status (Success, UserException, etc.)
- Wartość zwracana (zakodowana)

**Komunikacja między maszynami:**
Należy zmienić:
1. **W serwerze:** adres IP z `127.0.0.2` na `0.0.0.0` (nasłuchiwanie na wszystkich interfejsach)
2. **W kliencie:** adres IP z `127.0.0.2` na rzeczywisty IP serwera
3. **Firewall:** otworzyć porty 10000 (TCP i UDP)

---

### Zadanie 12: Komunikacja między maszynami

**Konfiguracja:**
- Serwer: `Adapter1.Endpoints=tcp -h 0.0.0.0 -p 10010`
- Klient: `stringToProxy("calc/calc11:tcp -h <IP_SERWERA> -p 10010")`

**Test:** Uruchomienie klienta na jednej maszynie, serwera na drugiej

---

### Zadanie 13: Operacja avg z sekwencjami

**Zmiany w kodzie:** Zobacz pliki poniżej

**Plik: `slice/calculator.ice`** - dodana operacja avg i wyjątek:
```slice
exception DivisionByZero {
    string reason;
};

sequence<long> LongSeq;

interface Calc {
    // ... existing operations ...
    idempotent double avg(LongSeq numbers) throws DivisionByZero;
};
```

**Plik: `CalcI.java`** - implementacja:
```java
@Override
public double avg(long[] numbers, Current __current) throws DivisionByZero {
    if (numbers.length == 0) {
        throw new DivisionByZero("Cannot calculate average of empty sequence");
    }
    long sum = 0;
    for (long num : numbers) {
        sum += num;
    }
    return (double) sum / numbers.length;
}
```

**Plik: `IceClient.java`** - wywołanie:
```java
case "avg":
    long[] nums = {10, 20, 30, 40, 50};
    double avg = obj1.avg(nums);
    System.out.println("AVERAGE = " + avg);
    break;
```

**Po zmianach należy:**
1. Przekompilować plik .ice: `slice2java --output-dir generated slice/calculator.ice`
2. Zaimplementować metodę w CalcI.java
3. Dodać wywołanie w IceClient.java

---

### Zadanie 14: Operacje idempotentne

**Co daje deklaracja idempotent?**
- Informuje Ice, że operacja może być bezpiecznie powtórzona
- Ice może automatycznie ponawiać wywołanie w przypadku błędów sieciowych
- Optymalizacja: możliwość cache'owania wyników

**Które operacje mogą być idempotentne?**
- `add(a, b)` - TAK (zawsze ten sam wynik dla tych samych argumentów)
- `subtract(a, b)` - TAK (zawsze ten sam wynik)
- `avg(numbers)` - TAK (zawsze ten sam wynik)
- `op(a1, b1)` - ZALEŻY (jeśli nie zmienia stanu serwera - TAK)

**Operacje NIE mogą być idempotentne jeśli:**
- Zmieniają stan serwera
- Mają efekty uboczne (np. zapis do bazy)
- Generują unikalne ID

**Deklaracja w .ice:**
```slice
idempotent long add(int a, int b);
idempotent double avg(LongSeq numbers) throws DivisionByZero;
```

---

### Zadanie 15: Wywołanie synchroniczne z opóźnieniem

**Test:** Wywołanie `add2` (z wartościami > 1000)

**Problem:**
- Klient jest zablokowany na 6 sekund
- Interfejs użytkownika nie odpowiada
- Nie można wykonać innych operacji
- Złe doświadczenie użytkownika (UX)

**Rozwiązanie:** Wywołania asynchroniczne (zadanie 16)

---

### Zadanie 16: Wywołania asynchroniczne

**Wzorzec 1: `add-asyn1` (callback):**
```java
obj1.addAsync(7000, 8000).whenComplete((result, ex) -> 
    System.out.println("RESULT (asyn) = " + result)
);
```
- Wywołanie natychmiast zwraca CompletableFuture
- Callback wykonuje się po otrzymaniu wyniku
- Klient może kontynuować pracę

**Wzorzec 2: `add-asyn2-req` i `add-asyn2-res` (future):**
```java
// Wysłanie żądania
CompletableFuture<Long> cfl = obj1.addAsync(7000, 8000);
// ... inne operacje ...
// Odebranie wyniku
long r = cfl.join();
```

**Odpowiedzi na pytania:**

**Q1: Co składa się na opóźnienie wywołania asynchronicznego?**
- Czas serializacji żądania
- Czas wysłania przez sieć (do bufora TCP)
- Wywołanie wraca NATYCHMIAST (nie czeka na odpowiedź)
- Odpowiedź jest odbierana asynchronicznie

**Q2: Kiedy warto używać wywołań nieblokujących?**
- Długotrwałe operacje
- Wiele równoległych wywołań
- Aplikacje GUI (responsywność)
- Operacje I/O-bound
- Gdy klient ma inne zadania do wykonania

**Q3: Czy każde wywołanie powinno być nieblokujące?**
- NIE
- Proste, szybkie operacje lepiej wywołać synchronicznie
- Asynchroniczne wywołania dodają złożoność kodu
- Dla operacji <100ms synchroniczne jest OK

---

### Zadanie 17: Pula wątków adaptera

**Domyślna wielkość:** 1 wątek

**Problem z 1 wątkiem:**
- Tylko jedno wywołanie naraz
- Kolejne wywołania czekają w kolejce
- Przy długotrwałych operacjach - duże opóźnienia

**Konfiguracja w `server.config`:**
```
Adapter1.ThreadPool.Size=10
```

**Uruchomienie z konfiguracją:**
```bash
java -jar server.jar --Ice.Config=server.config
```

**Wynik:**
- Serwer może obsługiwać 10 równoległych wywołań
- Znacznie lepsza wydajność
- Krótszy czas oczekiwania klientów

**Test:** Wywołanie `op-asyn1b 100` - z pulą 10 wątków operacje wykonują się równolegle

---

### Zadanie 18: Wywołania oneway

**Czym jest oneway?**
- Wywołanie bez oczekiwania na odpowiedź
- "Fire and forget"
- Klient nie wie czy operacja się powiodła

**Wymogi:**
- Operacja musi zwracać `void`
- Nie może rzucać wyjątków (poza systemowymi)
- Nie może mieć parametrów `out`

**Które operacje mogą być oneway?**
- `op(A a1, short b1)` - TAK (zwraca void)
- `add(int a, int b)` - NIE (zwraca long)
- `subtract(int a, int b)` - NIE (zwraca long)

**Test w kliencie:**
```java
case "set-proxy oneway":
    obj1 = obj1.ice_oneway();
    break;
case "op":
    obj1.op(a, (short) 44); // Wraca natychmiast
    break;
```

**Różnica w komunikacji:**
- **Twoway:** Request → Response (2 wiadomości)
- **Oneway:** Request (1 wiadomość, brak odpowiedzi)

**Wireshark:** Widoczne tylko żądanie, brak odpowiedzi

---

### Zadanie 19: Wywołania datagramowe

**Czym jest datagram?**
- Wywołanie przez UDP zamiast TCP
- Bez gwarancji dostarczenia
- Bez kolejności
- Szybsze, mniejszy overhead

**Wymogi:**
- Te same co oneway (void, no exceptions)
- Dodatkowo: mały rozmiar wiadomości (MTU ~1500 bajtów)

**Test:**
```java
case "set-proxy datagram":
    obj1 = obj1.ice_datagram();
    break;
```

**Różnica w komunikacji:**
- **Twoway TCP:** 3-way handshake, ACK, retransmisja
- **Datagram UDP:** Pojedynczy pakiet, brak potwierdzenia

**Kiedy używać:**
- Dane telemetryczne
- Monitoring (gdzie utrata pojedynczego pakietu jest akceptowalna)
- Gry online
- Streaming

---

### Zadanie 20: Kompresja wiadomości

**Konfiguracja:**
- Opcja `-z` w endpoints
- Biblioteki: bzip2, commons-compress

**Test:**
```java
case "op":  // Mała wiadomość - NIE skompresowana
case "op2": // Duża wiadomość - skompresowana
```

**Wireshark:**
- Pole "Compression Status" w nagłówku Ice
- `op`: Compression Status = 0 (not compressed)
- `op2`: Compression Status = 1 (compressed)

**Dlaczego tylko op2?**
- Ice kompresuje tylko gdy wiadomość jest wystarczająco duża
- Próg: ~100 bajtów
- Dla małych wiadomości kompresja zwiększyłaby rozmiar

**Odpowiedzi serwera:**
- Również mogą być kompresowane
- Zależy od rozmiaru odpowiedzi

**Kiedy aktywować kompresję?**
- Duże struktury danych
- Wolne łącza sieciowe
- Gdy CPU jest tańsze niż bandwidth
- NIE dla małych, częstych wiadomości

**Wyłączenie:**
```java
case "compress off":
    obj1 = obj1.ice_compress(false);
    break;
```

---

### Zadanie 21: Agregacja wywołań (batching)

**Korzyść z agregacji:**
- Wiele wywołań w jednej wiadomości TCP/UDP
- Mniejszy overhead sieciowy
- Mniej pakietów
- Lepsza wydajność dla wielu małych wywołań

**Wymogi:**
- Operacje oneway lub datagram
- Wywołania muszą być "przepchnięte" (flush)

**Test:**
```java
case "set-proxy batch oneway":
    obj1 = obj1.ice_batchOneway();
    break;
case "op 10":
    for (int i = 0; i < 10; i++) obj1.op(a, (short) 44);
    break;
case "flush":
    obj1.ice_flushBatchRequests();
    break;
```

**Różnica w komunikacji:**
- **Bez batching:** 10 osobnych pakietów TCP
- **Z batching:** 1 pakiet TCP zawierający 10 wywołań

**Wireshark:** Jedna wiadomość Ice z wieloma żądaniami

**Tryby batch:**
- `ice_batchOneway()` - batch przez TCP
- `ice_batchDatagram()` - batch przez UDP

---

### Zadanie 22: Czas podtrzymywania połączenia TCP

**Problem:**
- Zamknąć szybko → overhead przy kolejnym wywołaniu
- Zamknąć późno → marnowanie zasobów

**Konfiguracja ACM (Active Connection Management):**
```
Ice.ACM.Timeout=60  # sekundy
```

**Plik `client.config`:**
```
Ice.Trace.Network=2  # Logowanie zdarzeń sieciowych
Ice.ACM.Timeout=30
```

**Uruchomienie:**
```bash
java -jar client.jar --Ice.Config=client.config
```

**Obserwacja:**
- Logi pokazują otwarcie połączenia
- Po 30 sekundach bezczynności - zamknięcie
- Kolejne wywołanie otwiera nowe połączenie

**Optymalizacja:**
- Krótki timeout dla rzadkich wywołań
- Długi timeout dla częstych wywołań
- Heartbeat dla utrzymania połączenia

---

### Zadanie 23: Uruchomienie w Docker

**Scenariusz 1: Klient i serwer w kontenerach**
```bash
# Kompilacja
mvn package

# Uruchomienie
docker-compose up
```

**Scenariusz 2: Klient w kontenerze, serwer na hoście**
```bash
# W kliencie użyć:
stringToProxy("calc/calc11:tcp -h host.docker.internal -p 10010")
```

**Scenariusz 3: Serwer w kontenerze, klient na hoście**
```yaml
# docker-compose.yaml
ports:
  - "10010:10010"  # Mapowanie portów
```

**Klient na hoście:**
```java
stringToProxy("calc/calc11:tcp -h localhost -p 10010")
```

---

### Zadanie 24: Analiza ruchu sieciowego (ice.pcapng)

**Interesujące aspekty:**

1. **Ustanowienie połączenia (#4-#12):**
   - TCP 3-way handshake
   - Ice protocol negotiation
   - Pierwsze wywołanie

2. **Wiadomość skompresowana (#14):**
   - Compression Status = 1
   - Mniejszy rozmiar payload

3. **Batched TCP (#33) i UDP (#35):**
   - Wiele wywołań w jednej wiadomości
   - Znacznie mniejszy overhead

4. **Oneway TCP (#108) i UDP (#54):**
   - Brak odpowiedzi
   - Tylko żądanie

5. **Analiza opóźnień:**
   - **Oneway (#54-#63, #104-#123):** ~0-1ms (klient nie czeka)
   - **Synchroniczne (#64-#103):** ~500ms (opóźnienie serwanta)

---

## Sekcja 2.3 - Apache Thrift

### Zadanie 1-2: Kompilacja Thrift

**Polecenia:**

1. **Java:**
   ```bash
   thrift --gen java calculator.thrift
   ```

2. **Python:**
   ```bash
   thrift --gen py calculator.thrift
   ```

3. **C++:**
   ```bash
   thrift --gen cpp calculator.thrift
   ```

**Wynik:** Wygenerowane pliki w katalogu `gen-java/`

---

### Zadanie 3-9: Thrift - szczegóły w osobnej sekcji

*(Zadania Thrift wymagają osobnego projektu - nie są obecne w bieżącym katalogu ICE)*

---

## Podsumowanie zmian w kodzie

### Zmiany wymagane dla poszczególnych zadań:

| Zadanie | Plik | Zmiana |
|---------|------|--------|
| 7 | CalcI.java | Implementacja subtract() |
| 9 | IceServer.java | Dodanie calc33 ze wspólnym serwantem |
| 10 | IceServer.java | Dodanie calc33 z dedykowanym serwantem |
| 13 | calculator.ice | Dodanie avg(), DivisionByZero, LongSeq |
| 13 | CalcI.java | Implementacja avg() |
| 13 | IceClient.java | Wywołanie avg w menu |
| 14 | calculator.ice | Oznaczenie operacji jako idempotent |
| 17 | server.config | Ustawienie ThreadPool.Size=10 |
| 22 | client.config | Dodanie Ice.ACM.Timeout |

---

## Wnioski

1. **ICE vs Thrift:** ICE oferuje bardziej zaawansowane funkcje (oneway, batching, kompresja)
2. **Wydajność:** Kluczowe są: pula wątków, asynchroniczność, batching
3. **Sieć:** Wybór TCP vs UDP zależy od wymagań (niezawodność vs szybkość)
4. **Kompresja:** Opłacalna tylko dla dużych wiadomości
5. **Idempotentność:** Ważna dla automatycznego ponawiania wywołań

---

*Dokument wygenerowany automatycznie dla laboratorium Middleware 2026*