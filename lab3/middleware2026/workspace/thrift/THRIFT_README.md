# Apache Thrift - Instrukcje Wykonania Ćwiczeń

## Przygotowanie środowiska

### Wymagania
- Java JDK 8 lub nowszy
- Maven
- Apache Thrift compiler (thrift)
- Wireshark (opcjonalnie, do analizy ruchu)

### Instalacja Thrift compiler

**macOS:**
```bash
brew install thrift
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install thrift-compiler
```

**Windows:**
Pobierz z: https://thrift.apache.org/download

## Kompilacja projektu

### 1. Kompilacja pliku .thrift (Zadanie 2)

**Java:**
```bash
thrift --gen java calculator.thrift
```
Generuje pliki w `gen-java/sr/gen/thrift/`

**Python:**
```bash
thrift --gen py calculator.thrift
```
Generuje pliki w `gen-py/`

**C++:**
```bash
thrift --gen cpp calculator.thrift
```

### 2. Kompilacja projektu Maven

```bash
mvn clean compile
mvn package
```

## Uruchamianie aplikacji

### Serwer

```bash
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.server.ThriftServer
```

**Serwer uruchamia dwa tryby:**
- **Simple mode** - port 9080
- **Multiplex mode** - port 9081

### Klient

```bash
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.client.ThriftClient
```

**Wybór trybu:**
```
Which server do you want to connect to? (simple/multiplex)
==> simple
```
lub
```
==> multiplex
```

## Menu klienta - Dostępne komendy

### Tryb Simple (port 9080)

**Podstawowe operacje:**
- `add1a` - add(44, 55) przez Calculator
- `add1b` - add(4400, 5500) przez Calculator (z opóźnieniem 6s)
- `add3` - add(44, 55) przez AdvancedCalculator
- `subtract1` - subtract(100, 42) (Zadanie 5)

**Operacje zaawansowane:**
- `op1` - op(AVG, {4.0, 5.0, 3.1415926})
- `op2` - op(AVG, {}) - test wyjątku (pusta kolekcja)

**Nowe operacje (Zadanie 5):**
- `fact` - factorial(5) = 120
- `fact10` - factorial(10) = 3628800
- `fact-neg` - factorial(-5) - test wyjątku

**Wyjście:**
- `x` - zakończenie

### Tryb Multiplex (port 9081)

**Wszystkie powyższe komendy plus:**
- `add2` - add przez drugi Calculator (S2)

**Różnica:**
- W simple: wszystkie wywołania trafiają do tego samego handlera
- W multiplex: można wybrać konkretny handler (S1, S2, A1, A2)

## Realizacja poszczególnych zadań

### Zadanie 1: Otwarcie projektu
Otwórz katalog `thrift/` w IDE (IntelliJ IDEA, Eclipse, VS Code)

### Zadanie 2: Kompilacja .thrift
```bash
# Java
thrift --gen java calculator.thrift

# Python
thrift --gen py calculator.thrift

# Sprawdź wygenerowane pliki
ls gen-java/sr/gen/thrift/
```

### Zadanie 3: Analiza kodu
1. Przejrzyj `calculator.thrift` - definicje IDL
2. Sprawdź wygenerowane pliki w `gen-java/`
3. Przeanalizuj:
   - `ThriftServer.java` - konfiguracja serwera
   - `CalculatorHandler.java` - implementacja Calculator
   - `AdvancedCalculatorHandler.java` - implementacja AdvancedCalculator
   - `ThriftClient.java` - klient

### Zadanie 4: Uruchomienie i testowanie

**Terminal 1 - Serwer:**
```bash
mvn package
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.server.ThriftServer
```

**Terminal 2 - Klient:**
```bash
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.client.ThriftClient
```

**Test simple mode:**
```
==> simple
==> add1a
add(44,55) returned 99

==> add3
add(44,55) returned 99
```

**Obserwacja:** Oba wywołania trafiają do tego samego handlera!

**Test multiplex mode:**
```
==> multiplex
==> add1a
CalcHandler#1 add(44,55)

==> add2
CalcHandler#2 add(44,55)

==> add3
AdvCalcHandler#11 add(44,55)
```

**Obserwacja:** Każde wywołanie trafia do innego handlera!

### Zadanie 5: Rozbudowa interfejsu

**Krok 1: Modyfikacja calculator.thrift**
```thrift
exception NegativeNumber {
  1: i32 number,
  2: string message
}

service AdvancedCalculator extends Calculator {
   double op(...),
   i64 factorial(1: i32 n) throws (1: NegativeNumber ex),
}
```

**Krok 2: Rekompilacja**
```bash
thrift --gen java calculator.thrift
mvn clean compile package
```

**Krok 3: Implementacja w AdvancedCalculatorHandler.java**
(Zobacz kod w pliku)

**Krok 4: Dodanie wywołań w kliencie**
(Zobacz kod w ThriftClient.java)

**Krok 5: Test**
```
==> fact
factorial(5) returned 120

==> fact10
factorial(10) returned 3628800

==> fact-neg
ERROR (expected): Factorial is not defined for negative numbers (number: -5)
```

### Zadanie 6: Analiza w Wireshark

**Krok 1: Uruchom Wireshark**
```bash
# Wybierz interfejs Loopback (lo0)
# Zastosuj filtr:
tcp.port == 9080 or tcp.port == 9081
```

**Krok 2: Uruchom serwer i klienta**

**Krok 3: Wywołaj operację**
```
==> add1a
```

**Krok 4: Analiza w Wireshark**
- Znajdź pakiety TCP z portem 9080
- Sprawdź rozmiar payload (Data)
- Protokół L4: **TCP**

**Przykładowe rozmiary:**
- Request: ~60-80 bajtów (TBinaryProtocol)
- Response: ~20-30 bajtów

### Zadanie 7: Porównanie protokołów serializacji

**Zmiana protokołu w serwerze (ThriftServer.java):**
```java
// Linia 74 w metodzie simple():
TProtocolFactory protocolFactory1 = new TBinaryProtocol.Factory();
// Zmień na:
TProtocolFactory protocolFactory1 = new TCompactProtocol.Factory();
// lub:
TProtocolFactory protocolFactory1 = new TJSONProtocol.Factory();
```

**Zmiana protokołu w kliencie (ThriftClient.java):**
```java
// Linie 49-51 w trybie simple:
protocol = new TBinaryProtocol(transport);
// Zmień na:
protocol = new TCompactProtocol(transport);
// lub:
protocol = new TJSONProtocol(transport);
```

**WAŻNE:** Protokół w kliencie i serwerze musi być ten sam!

**Test każdego protokołu:**
1. Zmień protokół w serwerze i kliencie
2. Rekompiluj: `mvn clean compile package`
3. Uruchom serwer i klienta
4. Wywołaj `add1a`
5. Sprawdź rozmiar w Wireshark

**Oczekiwane wyniki:**

| Protokół | Request | Response | Suma | Uwagi |
|----------|---------|----------|------|-------|
| TBinaryProtocol | ~65B | ~25B | ~90B | Standard |
| TCompactProtocol | ~45B | ~20B | ~65B | Najefektywniejszy |
| TJSONProtocol | ~140B | ~50B | ~190B | Czytelny, największy |

**Analiza pliku thrift1-binary-compact-json.pcapng:**
```bash
# Otwórz w Wireshark
# Filtr: tcp.port == 9080
# Znajdź 3 serie wywołań (binary, compact, json)
# JSON jest łatwo rozpoznawalny (czytelny tekst)
```

### Zadanie 8: TBinaryProtocol - wiele obiektów

**Pytanie:** Jak udostępnić wiele obiektów w trybie simple?

**Eksperyment:**

**Kod serwera (ThriftServer.java, linie 78-88):**
```java
TServer server1 = new TSimpleServer(...processor1);
TServer server2 = new TSimpleServer(...processor2);
TServer server3 = new TSimpleServer(...processor3);

server1.serve();  // Blokuje tutaj!
server2.serve();  // Nigdy się nie wykona
server3.serve();  // Nigdy się nie wykona
```

**Obserwacja:**
- Tylko server1 działa
- `serve()` jest blokujące
- Wszystkie próbują użyć tego samego portu (9080)

**Próba rozwiązania - różne porty:**
```java
TServerTransport serverTransport1 = new TServerSocket(9080);
TServerTransport serverTransport2 = new TServerSocket(9081);
TServerTransport serverTransport3 = new TServerSocket(9082);
```

**Problem:**
- To nie są "wiele obiektów", ale "wiele serwerów"
- Klient musi znać wszystkie porty
- Nie jest to eleganckie rozwiązanie

**Wniosek:**
- TBinaryProtocol sam w sobie nie wspiera wielu obiektów
- Thrift jest **service-oriented**, nie object-oriented
- Rozwiązanie: **TMultiplexedProcessor** (Zadanie 9)

### Zadanie 9: TMultiplexedProcessor - wiele serwisów

**Implementacja w serwerze (ThriftServer.java, linie 96-123):**

```java
// 1. Utworzenie procesorów
Calculator.Processor processor1 = new Calculator.Processor(new CalculatorHandler(1));
Calculator.Processor processor2 = new Calculator.Processor(new CalculatorHandler(2));
AdvancedCalculator.Processor processor3 = new AdvancedCalculator.Processor(new AdvancedCalculatorHandler(11));
AdvancedCalculator.Processor processor4 = new AdvancedCalculator.Processor(new AdvancedCalculatorHandler(12));

// 2. Jeden transport i protokół
TServerTransport serverTransport = new TServerSocket(9081);
TProtocolFactory protocolFactory = new TBinaryProtocol.Factory();

// 3. TMultiplexedProcessor - rejestracja
TMultiplexedProcessor multiplex = new TMultiplexedProcessor();
multiplex.registerProcessor("S1", processor1);
multiplex.registerProcessor("S2", processor2);
multiplex.registerProcessor("A1", processor3);
multiplex.registerProcessor("A2", processor4);

// 4. Jeden serwer
TServer server = new TSimpleServer(
    new Args(serverTransport)
        .protocolFactory(protocolFactory)
        .processor(multiplex)
);
server.serve();
```

**Użycie w kliencie (ThriftClient.java, linie 58-69):**

```java
transport = new TSocket(host, 9081);
protocol = new TBinaryProtocol(transport);

// Klienci dla różnych procesorów
synCalc1 = new Calculator.Client(
    new TMultiplexedProtocol(protocol, "S1")
);
synCalc2 = new Calculator.Client(
    new TMultiplexedProtocol(protocol, "S2")
);
synAdvCalc1 = new AdvancedCalculator.Client(
    new TMultiplexedProtocol(protocol, "A1")
);

transport.open();
```

**Test:**
```
==> multiplex
==> add1a
CalcHandler#1 add(44,55)

==> add2
CalcHandler#2 add(44,55)

==> add3
AdvCalcHandler#11 add(44,55)
```

**Każde wywołanie trafia do innego handlera!**

**Jak to działa:**
1. `TMultiplexedProtocol` dodaje nazwę serwisu do wiadomości
2. Format: `serviceName:methodName`
3. `TMultiplexedProcessor` czyta nazwę i routuje do odpowiedniego procesora
4. Jeden port, wiele serwisów!

## Porównanie z ICE

| Aspekt | Thrift | ICE |
|--------|--------|-----|
| **Filozofia** | Service-oriented | Object-oriented |
| **Identyfikacja** | Nazwa serwisu | Identity (category/name) |
| **Multiplexing** | TMultiplexedProcessor | Wbudowane (ASM) |
| **Protokoły** | Binary, Compact, JSON | Binary, Compact |
| **Kompresja** | Brak natywnej | Wbudowana (-z) |
| **Oneway** | Brak | Tak |
| **Batching** | Brak | Tak |

## Rozwiązywanie problemów

### Błąd kompilacji .thrift
```bash
# Sprawdź wersję
thrift --version

# Rekompiluj
thrift --gen java calculator.thrift
```

### Serwer nie startuje
```bash
# Sprawdź czy port jest wolny
netstat -ano | grep 9080
lsof -i :9080

# Zabij proces
kill -9 <PID>
```

### Klient nie może się połączyć
- Sprawdź czy serwer działa
- Sprawdź czy protokoły są zgodne (klient i serwer)
- Sprawdź port (9080 dla simple, 9081 dla multiplex)

### Błąd "No such method"
- Rekompiluj .thrift: `thrift --gen java calculator.thrift`
- Rekompiluj projekt: `mvn clean compile package`
- Upewnij się, że używasz najnowszych klas

## Dokumentacja

Szczegółowe odpowiedzi na wszystkie pytania znajdują się w pliku **THRIFT_ANSWERS.md**.

## Dodatkowe zasoby

- [Apache Thrift Documentation](https://thrift.apache.org/docs/)
- [Thrift Tutorial](https://thrift.apache.org/tutorial/)
- [Thrift IDL](https://thrift.apache.org/docs/idl)
- [Thrift Types](https://thrift.apache.org/docs/types)

## Podsumowanie komend

```bash
# Kompilacja
thrift --gen java calculator.thrift
mvn clean compile package

# Uruchomienie
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.server.ThriftServer
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.client.ThriftClient

# Wireshark
# Filtr: tcp.port == 9080 or tcp.port == 9081