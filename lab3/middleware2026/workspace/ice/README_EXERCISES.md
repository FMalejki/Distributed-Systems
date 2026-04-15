# ICE Middleware - Instrukcje Wykonania Ćwiczeń

## Przygotowanie środowiska

### Wymagania
- Java JDK 8 lub nowszy
- Maven
- ZeroC Ice (slice2java)
- Wireshark (opcjonalnie, do analizy ruchu)
- Docker (opcjonalnie, do zadania 23)

## Kompilacja projektu

### 1. Kompilacja pliku .ice (Zadanie 3)

**Java:**
```bash
slice2java --output-dir generated slice/calculator.ice
```

**Python:**
```bash
slice2py --output-dir generated slice/calculator.ice
```

**C++:**
```bash
slice2cpp --output-dir generated slice/calculator.ice
```

### 2. Kompilacja projektu Maven

```bash
mvn clean compile
mvn package
```

## Uruchamianie aplikacji

### Serwer

**Bez pliku konfiguracyjnego (hardcoded config):**
```bash
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.server.IceServer
```

**Z plikiem konfiguracyjnym (Zadanie 17 - pula wątków):**
```bash
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.server.IceServer --Ice.Config=server.config
```

### Klient

**Bez pliku konfiguracyjnego:**
```bash
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.client.IceClient
```

**Z plikiem konfiguracyjnym (Zadanie 22 - ACM timeout):**
```bash
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.client.IceClient --Ice.Config=client.config
```

## Menu klienta - Dostępne komendy

### Podstawowe operacje
- `add` - Dodawanie 7 + 8
- `add2` - Dodawanie 7000 + 8000 (z opóźnieniem 6s)
- `subtract` - Odejmowanie 7 - 8 (Zadanie 7)
- `avg` - Średnia z sekwencji [10, 20, 30, 40, 50] (Zadanie 13)
- `avg-empty` - Test wyjątku dla pustej sekwencji (Zadanie 13)
- `avg-large` - Średnia ze 100 liczb (Zadanie 13)
- `op` - Operacja z małą strukturą
- `op2` - Operacja z dużą strukturą (kompresja)
- `op 10` - 10x wywołanie operacji op

### Wywołania asynchroniczne (Zadanie 16)
- `add-asyn1` - Asynchroniczne z callback
- `add-asyn2-req` - Wysłanie żądania asynchronicznego
- `add-asyn2-res` - Odebranie wyniku asynchronicznego
- `op-asyn1a 100` - 100x asynchroniczne wywołanie op
- `op-asyn1b 100` - 100x asynchroniczne z callback

### Tryby proxy (Zadania 18-21)
- `set-proxy twoway` - Tryb normalny (request-response)
- `set-proxy oneway` - Tryb oneway (bez odpowiedzi) - Zadanie 18
- `set-proxy datagram` - Tryb datagram (UDP) - Zadanie 19
- `set-proxy batch oneway` - Agregacja przez TCP - Zadanie 21
- `set-proxy batch datagram` - Agregacja przez UDP - Zadanie 21
- `flush` - Przepchnięcie zakolejkowanych wywołań batch

### Kompresja (Zadanie 20)
- `compress on` - Włączenie kompresji
- `compress off` - Wyłączenie kompresji

### Inne
- `add-with-ctx` - Wywołanie z kontekstem
- `x` - Wyjście

## Realizacja poszczególnych zadań

### Zadanie 6: Sprawdzenie gniazd serwera
```bash
# Linux/macOS
netstat -ano | grep 10000
lsof -i :10000
ss -tulpn | grep 10000

# Windows
netstat -ano | findstr 10000
```

### Zadanie 9: Wiele obiektów, wspólny serwant
W pliku `IceServer.java` odkomentuj linię:
```java
adapter.add(calcServant1, new Identity("calc33", "calc"));
```

Uruchom drugiego klienta z referencją do calc33:
```java
stringToProxy("calc/calc33:tcp -h 127.0.0.2 -p 10000")
```

### Zadanie 10: Wiele obiektów, dedykowane serwanty
W pliku `IceServer.java` odkomentuj linie:
```java
CalcI calcServant3 = new CalcI();
adapter.add(calcServant3, new Identity("calc33", "calc"));
```

### Zadanie 11: Analiza w Wireshark
1. Uruchom Wireshark
2. Zastosuj filtr: `ip.addr==127.0.0.2 or tcp.port==10000`
3. Uruchom serwer i klienta
4. Wywołaj różne operacje
5. Analizuj pakiety ICE

### Zadanie 13: Kompilacja po zmianach w .ice
```bash
slice2java --output-dir generated slice/calculator.ice
mvn clean compile package
```

### Zadanie 17: Pula wątków
1. Uruchom serwer z `--Ice.Config=server.config`
2. W kliencie wywołaj `op-asyn1b 100`
3. Obserwuj równoległe wykonywanie (10 wątków)

### Zadanie 18-19: Oneway i Datagram
```
==> set-proxy oneway
==> op
==> set-proxy datagram
==> op
```
Obserwuj w Wireshark brak odpowiedzi.

### Zadanie 20: Kompresja
```
==> compress on
==> op      # Nie skompresowane (za małe)
==> op2     # Skompresowane (duże)
```
W Wireshark sprawdź pole "Compression Status".

### Zadanie 21: Batching
```
==> set-proxy batch oneway
==> op 10
==> flush
```
W Wireshark zobaczysz jedną wiadomość z 10 wywołaniami.

### Zadanie 22: ACM Timeout
```bash
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.client.IceClient --Ice.Config=client.config
```
Odkomentuj w `client.config`:
```
Ice.Trace.Network=2
```
Obserwuj logi zamykania połączeń po 30 sekundach bezczynności.

### Zadanie 23: Docker

**Kompilacja:**
```bash
mvn package
```

**Uruchomienie w kontenerze:**
```bash
# Sprawdź plik cmdline.txt dla poleceń Docker
docker-compose up
```

**Klient w kontenerze, serwer na hoście:**
```bash
# W kliencie użyj:
stringToProxy("calc/calc11:tcp -h host.docker.internal -p 10010")
```

**Serwer w kontenerze, klient na hoście:**
```bash
# Upewnij się, że porty są zmapowane w docker-compose.yaml
ports:
  - "10010:10010"
```

## Zmiany w kodzie - Podsumowanie

### Zmodyfikowane pliki:

1. **slice/calculator.ice**
   - Dodano wyjątek `DivisionByZero`
   - Dodano typ `LongSeq` (sequence<long>)
   - Dodano operację `avg()`
   - Oznaczono operacje jako `idempotent`

2. **src/sr/ice/server/CalcI.java**
   - Zaimplementowano `subtract()` (Zadanie 7)
   - Zaimplementowano `avg()` z obsługą wyjątków (Zadanie 13)
   - Dodano logowanie Identity obiektu (Zadanie 9)

3. **src/sr/ice/server/IceServer.java**
   - Dodano komentarze dla Zadania 9 (wspólny serwant)
   - Dodano komentarze dla Zadania 10 (dedykowane serwanty)

4. **src/sr/ice/client/IceClient.java**
   - Dodano wywołania `avg`, `avg-empty`, `avg-large` (Zadanie 13)

5. **client.config**
   - Zaktualizowano `Ice.ACM.Timeout=30` (Zadanie 22)

6. **server.config**
   - Już zawiera `Adapter1.ThreadPool.Size=10` (Zadanie 17)

## Testowanie

### Test podstawowych operacji:
```
==> add
RESULT = 15

==> subtract
RESULT = -1

==> avg
AVERAGE = 30.0
```

### Test wyjątków:
```
==> avg-empty
ERROR (expected): Cannot calculate average of empty sequence
```

### Test asynchroniczności:
```
==> add-asyn1
RESULT (asyn) = 15000
```

### Test oneway:
```
==> set-proxy oneway
==> op
DONE
```

## Rozwiązywanie problemów

### Błąd kompilacji po zmianie .ice
```bash
slice2java --output-dir generated slice/calculator.ice
mvn clean compile
```

### Serwer nie startuje
- Sprawdź czy port 10000/10010 nie jest zajęty
- Sprawdź czy plik config jest poprawny

### Klient nie może się połączyć
- Sprawdź czy serwer działa
- Sprawdź adres IP i port w konfiguracji
- Sprawdź firewall

### Wireshark nie pokazuje pakietów
- Sprawdź czy filtr jest poprawny
- Sprawdź czy nasłuchujesz na właściwym interfejsie (lo0/Loopback)

## Dokumentacja

Szczegółowe odpowiedzi na wszystkie pytania znajdują się w pliku **ANSWERS.md**.

## Dodatkowe zasoby

- [ZeroC Ice Documentation](https://doc.zeroc.com/ice/3.7/)
- [Ice Property Reference](https://doc.zeroc.com/ice/3.7/property-reference/)
- [Slice Language](https://doc.zeroc.com/ice/3.7/the-slice-language)