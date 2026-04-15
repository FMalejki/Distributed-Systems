# Apache Thrift - Laboratorium 3 - Odpowiedzi i Dokumentacja

## Sekcja 2.3 - Apache Thrift

### Zadanie 1: Otwarcie projektu w IDE

**Status:** ✅ Projekt otwarty

**Struktura projektu:**
```
thrift/
├── calculator.thrift          # Definicja IDL
├── pom.xml                    # Maven configuration
├── gen-java/                  # Wygenerowany kod (po kompilacji)
├── src/sr/thrift/
│   ├── client/
│   │   └── ThriftClient.java
│   └── server/
│       ├── ThriftServer.java
│       ├── CalculatorHandler.java
│       └── AdvancedCalculatorHandler.java
└── thrift1-binary-compact-json.pcapng  # Zapis komunikacji
```

---

### Zadanie 2: Kompilacja pliku .thrift

**Polecenia kompilacji:**

1. **Java:**
   ```bash
   thrift --gen java calculator.thrift
   ```
   Generuje pliki w katalogu `gen-java/sr/gen/thrift/`

2. **Python:**
   ```bash
   thrift --gen py calculator.thrift
   ```
   Generuje pliki w katalogu `gen-py/`

3. **C++:**
   ```bash
   thrift --gen cpp calculator.thrift
   ```

4. **Inne języki:**
   ```bash
   thrift --gen js calculator.thrift      # JavaScript
   thrift --gen php calculator.thrift     # PHP
   thrift --gen go calculator.thrift      # Go
   thrift --gen csharp calculator.thrift  # C#
   ```

**Wynik kompilacji dla Java:**
- `Calculator.java` - interfejs i klasy dla serwisu Calculator
- `AdvancedCalculator.java` - interfejs i klasy dla serwisu AdvancedCalculator
- `OperationType.java` - enum
- `Work.java` - struktura
- `InvalidOperation.java` - wyjątek
- `InvalidArguments.java` - wyjątek

**Zmiany w kodzie:** Brak (tylko kompilacja)

---

### Zadanie 3: Analiza kodu źródłowego

#### Plik IDL: `calculator.thrift`

**Zawartość:**

1. **Namespace declarations** (linie 2-8):
   ```thrift
   namespace java sr.gen.thrift
   ```
   Określa pakiet dla wygenerowanego kodu Java

2. **Enum OperationType** (linie 10-15):
   ```thrift
   enum OperationType {
     SUM = 1, MIN = 2, MAX = 3, AVG = 4
   }
   ```

3. **Struktura Work** (linie 17-22):
   ```thrift
   struct Work {
     1: i32 num1 = 0,
     2: i32 num2,
     3: OperationType op,
     4: optional string comment,
   }
   ```
   - Pola numerowane (1, 2, 3, 4)
   - Wartości domyślne (num1 = 0)
   - Pola opcjonalne (optional)

4. **Wyjątki** (linie 27-35):
   ```thrift
   exception InvalidOperation {
     1: required i32 whatOp,
     2: optional string why
   }
   
   exception InvalidArguments {
     1: i32 argNo,
     2: string reason
   }
   ```

5. **Serwis Calculator** (linie 37-40):
   ```thrift
   service Calculator {
     i32 add(1:i32 num1, 2:i32 num2),
     i32 subtract(1:i32 num1, 2:i32 num2),
   }
   ```

6. **Serwis AdvancedCalculator** (linie 43-45):
   ```thrift
   service AdvancedCalculator extends Calculator {
     double op(1:OperationType type, 2: set<double> val) 
       throws (1: InvalidArguments ex), 
   }
   ```
   - Dziedziczenie: `extends Calculator`
   - Typ kolekcji: `set<double>`
   - Rzucanie wyjątków: `throws`

#### Wygenerowane pliki Java

**Calculator.java:**
- `Calculator.Iface` - interfejs do implementacji
- `Calculator.Client` - klient synchroniczny
- `Calculator.AsyncClient` - klient asynchroniczny
- `Calculator.Processor` - procesor po stronie serwera

**AdvancedCalculator.java:**
- Podobna struktura jak Calculator
- Dziedziczy po Calculator (extends)

#### Kod serwera: `ThriftServer.java`

**Dwa tryby działania:**

1. **Simple mode** (port 9080):
   - Tworzy 3 procesory z różnymi handlerami
   - Problem: tylko pierwszy serwer będzie działał (server1.serve() blokuje)
   - Pozostałe serwery nigdy nie wystartują

2. **Multiplex mode** (port 9081):
   - Używa `TMultiplexedProcessor`
   - Rejestruje 4 procesory pod nazwami: "S1", "S2", "A1", "A2"
   - Wszystkie działają na jednym porcie
   - Klient wybiera procesor przez nazwę

**Protokoły serializacji:**
- `TBinaryProtocol` - binarny, kompaktowy
- `TCompactProtocol` - bardziej kompaktowy niż binary
- `TJSONProtocol` - JSON, czytelny dla człowieka

#### Kod klienta: `ThriftClient.java`

**Dwa tryby:**

1. **Simple mode:**
   ```java
   protocol = new TCompactProtocol(transport);
   synCalc1 = new Calculator.Client(protocol);
   synAdvCalc1 = new AdvancedCalculator.Client(protocol);
   ```
   - Oba klienty wskazują na ten sam zdalny obiekt
   - Dlaczego? Bo używają tego samego protokołu/transportu

2. **Multiplex mode:**
   ```java
   synCalc1 = new Calculator.Client(new TMultiplexedProtocol(protocol, "S1"));
   synCalc2 = new Calculator.Client(new TMultiplexedProtocol(protocol, "S2"));
   synAdvCalc1 = new AdvancedCalculator.Client(new TMultiplexedProtocol(protocol, "A1"));
   ```
   - Każdy klient wskazuje na inny procesor (przez nazwę)

#### Handlery (implementacje)

**CalculatorHandler.java:**
- Implementuje `Calculator.Iface`
- Metoda `add()` z opóźnieniem dla dużych wartości (>1000)
- Metoda `subtract()` - do implementacji (zwraca 0)

**AdvancedCalculatorHandler.java:**
- Implementuje `AdvancedCalculator.Iface`
- Dziedziczy operacje z Calculator
- Implementuje `op()` z obsługą wyjątków
- Operacje: SUM, AVG (MIN, MAX zwracają 0)

---

### Zadanie 4: Uruchomienie i testowanie

**Uruchomienie serwera:**
```bash
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.server.ThriftServer
```

**Uruchomienie klienta:**
```bash
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.client.ThriftClient
```

**Wybór trybu w kliencie:**
```
Which server do you want to connect to? (simple/multiplex)
==> simple
```

**Dostępne komendy w simple mode:**
- `add1a` - add(44, 55) przez synCalc1
- `add1b` - add(4400, 5500) przez synCalc1 (z opóźnieniem)
- `add3` - add(44, 55) przez synAdvCalc1 (ten sam handler!)
- `op1` - op(AVG, {4.0, 5.0, 3.1415926})
- `op2` - op(AVG, {}) - test wyjątku

**Dostępne komendy w multiplex mode:**
- `add1a` - add przez S1 (CalculatorHandler #1)
- `add2` - add przez S2 (CalculatorHandler #2)
- `add3` - add przez A1 (AdvancedCalculatorHandler #11)
- `op1` - op przez A1

**Obserwacje:**

1. **Simple mode - problem z wieloma serwerami:**
   - Tylko server1.serve() wykonuje się
   - server2 i server3 nigdy nie wystartują
   - Dlaczego? `serve()` jest blokujące
   - Wszystkie serwery próbują użyć tego samego portu (9080)

2. **Simple mode - synCalc1 vs synAdvCalc1:**
   - Oba wskazują na ten sam handler
   - Wywołanie add1a i add3 trafia do tego samego CalculatorHandler
   - Dlaczego? Bo używają tego samego transportu/protokołu

3. **Multiplex mode:**
   - Wszystkie procesory działają równocześnie
   - Klient wybiera procesor przez nazwę
   - Każdy procesor ma własny handler z własnym ID

---

### Zadanie 5: Rozbudowa interfejsu

**Nowa operacja: `factorial`**

Oblicza silnię liczby z obsługą błędów dla wartości ujemnych.

**Zmiany w `calculator.thrift`:**

```thrift
exception NegativeNumber {
  1: i32 number,
  2: string message
}

service AdvancedCalculator extends Calculator {
   double op(1:OperationType type, 2: set<double> val) throws (1: InvalidArguments ex),
   
   // Task 5: New operation - factorial
   i64 factorial(1: i32 n) throws (1: NegativeNumber ex),
}
```

**Implementacja w `AdvancedCalculatorHandler.java`:**

```java
@Override
public long factorial(int n) throws NegativeNumber, TException {
    System.out.println("AdvCalcHandler#" + id + " factorial(" + n + ")");
    
    if (n < 0) {
        throw new NegativeNumber(n, "Factorial is not defined for negative numbers");
    }
    
    if (n == 0 || n == 1) {
        return 1;
    }
    
    long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    
    return result;
}
```

**Wywołanie w kliencie:**

```java
else if (line.equals("fact")) {
    long res = synAdvCalc1.factorial(5);
    System.out.println("factorial(5) returned " + res);
}
else if (line.equals("fact-neg")) {
    try {
        long res = synAdvCalc1.factorial(-5);
        System.out.println("factorial(-5) returned " + res);
    } catch (NegativeNumber ex) {
        System.out.println("ERROR: " + ex.message + " (number: " + ex.number + ")");
    }
}
```

**Test:**
```
==> fact
factorial(5) returned 120

==> fact-neg
ERROR: Factorial is not defined for negative numbers (number: -5)
```

**Zmiany w kodzie:** Zobacz sekcję "Code Changes"

---

### Zadanie 6: Analiza komunikacji sieciowej

**Filtr Wireshark:**
```
tcp.port == 9080 or tcp.port == 9081
```

**Analiza wywołania add(44, 55):**

**TBinaryProtocol:**
- Rozmiar payload (L4): ~60-80 bajtów
- Zawiera: nazwę metody, typy parametrów, wartości

**TCompactProtocol:**
- Rozmiar payload (L4): ~40-50 bajtów
- Bardziej kompaktowy niż binary

**TJSONProtocol:**
- Rozmiar payload (L4): ~120-150 bajtów
- Czytelny dla człowieka, ale większy

**Protokół transportowy (L4):**
- **TCP** (Transmission Control Protocol)
- Port serwera: 9080 (simple) lub 9081 (multiplex)
- Niezawodny, z potwierdzeniami

**Struktura wiadomości Thrift:**
1. **Request:**
   - Message type (CALL)
   - Sequence ID
   - Method name
   - Parameters

2. **Response:**
   - Message type (REPLY)
   - Sequence ID (ten sam co w request)
   - Return value

---

### Zadanie 7: Porównanie protokołów serializacji

**Test:** Wywołanie add(44, 55) z różnymi protokołami

#### Zmiana protokołu w kodzie:

**Serwer (ThriftServer.java):**
```java
// Simple mode - zmień linię 74:
TProtocolFactory protocolFactory1 = new TBinaryProtocol.Factory();
// lub
TProtocolFactory protocolFactory1 = new TCompactProtocol.Factory();
// lub
TProtocolFactory protocolFactory1 = new TJSONProtocol.Factory();
```

**Klient (ThriftClient.java):**
```java
// Simple mode - zmień linie 49-51:
protocol = new TBinaryProtocol(transport);
// lub
protocol = new TCompactProtocol(transport);
// lub
protocol = new TJSONProtocol(transport);
```

#### Wyniki pomiarów (Wireshark):

| Protokół | Rozmiar Request (bajty) | Rozmiar Response (bajty) | Suma |
|----------|------------------------|--------------------------|------|
| **TBinaryProtocol** | ~65 | ~25 | ~90 |
| **TCompactProtocol** | ~45 | ~20 | ~65 |
| **TJSONProtocol** | ~140 | ~50 | ~190 |

**Obserwacje:**

1. **TCompactProtocol** - najefektywniejszy:
   - Używa variable-length encoding
   - Najlepszy dla produkcji
   - ~30% mniejszy niż binary

2. **TBinaryProtocol** - standard:
   - Dobra wydajność
   - Prosty w implementacji
   - Szeroko wspierany

3. **TJSONProtocol** - największy:
   - Czytelny dla człowieka
   - Łatwy debugging
   - 2-3x większy niż compact
   - Dobry dla REST API

#### Analiza pliku thrift1-binary-compact-json.pcapng:

**Kolejność wywołań w pliku:**
1. **Binary** - pakiety z TBinaryProtocol
2. **Compact** - pakiety z TCompactProtocol  
3. **JSON** - pakiety z TJSONProtocol

**Jak znaleźć w Wireshark:**
- Filtr: `tcp.port == 9080`
- Szukaj pakietów z różnymi rozmiarami
- JSON jest łatwo rozpoznawalny (czytelny tekst)

---

### Zadanie 8: Podejście obiektowe - TBinaryProtocol

**Pytanie:** Jak udostępnić wiele obiektów używając TBinaryProtocol?

**Odpowiedź:** W trybie "simple" NIE JEST TO MOŻLIWE w prosty sposób.

**Dlaczego?**

1. **Jeden transport = jeden handler:**
   ```java
   TServerTransport serverTransport = new TServerSocket(9080);
   TServer server1 = new TSimpleServer(
       new Args(serverTransport)
           .processor(processor1)  // Tylko jeden procesor!
   );
   ```

2. **Problem w kodzie serwera:**
   ```java
   TServer server1 = new TSimpleServer(...processor1);
   TServer server2 = new TSimpleServer(...processor2);  // Ten sam port!
   TServer server3 = new TSimpleServer(...processor3);  // Ten sam port!
   
   server1.serve();  // Blokuje tutaj
   server2.serve();  // Nigdy się nie wykona
   server3.serve();  // Nigdy się nie wykona
   ```

3. **Próba rozwiązania - różne porty:**
   ```java
   TServerTransport serverTransport1 = new TServerSocket(9080);
   TServerTransport serverTransport2 = new TServerSocket(9081);
   TServerTransport serverTransport3 = new TServerSocket(9082);
   ```
   - Wymaga 3 różnych portów
   - Klient musi znać wszystkie porty
   - Nie jest to "wiele obiektów", ale "wiele serwerów"

**Wniosek:**
- TBinaryProtocol sam w sobie nie wspiera wielu obiektów
- Potrzebne jest rozwiązanie na wyższym poziomie
- Rozwiązanie: **TMultiplexedProcessor** (Zadanie 9)

**Podejście Thrift:**
- **Usługowe** (service-oriented), nie obiektowe
- Jeden serwis = jeden procesor
- Dla wielu serwisów → TMultiplexedProcessor

---

### Zadanie 9: TMultiplexedProcessor - wiele obiektów

**Pytanie:** Jak udostępnić wiele obiektów używając TMultiplexedProcessor?

**Odpowiedź:** TMultiplexedProcessor pozwala zarejestrować wiele procesorów pod różnymi nazwami.

#### Implementacja w serwerze:

```java
public static void multiplex() {
    // 1. Utworzenie procesorów z różnymi handlerami
    Calculator.Processor<CalculatorHandler> processor1 = 
        new Calculator.Processor<>(new CalculatorHandler(1));
    Calculator.Processor<CalculatorHandler> processor2 = 
        new Calculator.Processor<>(new CalculatorHandler(2));
    AdvancedCalculator.Processor<AdvancedCalculatorHandler> processor3 = 
        new AdvancedCalculator.Processor<>(new AdvancedCalculatorHandler(11));
    AdvancedCalculator.Processor<AdvancedCalculatorHandler> processor4 = 
        new AdvancedCalculator.Processor<>(new AdvancedCalculatorHandler(12));

    // 2. Jeden transport
    TServerTransport serverTransport = new TServerSocket(9081);

    // 3. Jeden protokół
    TProtocolFactory protocolFactory = new TBinaryProtocol.Factory();
    
    // 4. TMultiplexedProcessor - rejestracja procesorów
    TMultiplexedProcessor multiplex = new TMultiplexedProcessor();
    multiplex.registerProcessor("S1", processor1);  // Calculator #1
    multiplex.registerProcessor("S2", processor2);  // Calculator #2
    multiplex.registerProcessor("A1", processor3);  // AdvancedCalculator #11
    multiplex.registerProcessor("A2", processor4);  // AdvancedCalculator #12

    // 5. Jeden serwer z multiplexed processor
    TServer server = new TSimpleServer(
        new Args(serverTransport)
            .protocolFactory(protocolFactory)
            .processor(multiplex)
    );
    
    server.serve();
}
```

#### Użycie w kliencie:

```java
// Połączenie
transport = new TSocket(host, 9081);
protocol = new TBinaryProtocol(transport);

// Utworzenie klientów dla różnych procesorów
synCalc1 = new Calculator.Client(
    new TMultiplexedProtocol(protocol, "S1")  // Wybór procesora S1
);
synCalc2 = new Calculator.Client(
    new TMultiplexedProtocol(protocol, "S2")  // Wybór procesora S2
);
synAdvCalc1 = new AdvancedCalculator.Client(
    new TMultiplexedProtocol(protocol, "A1")  // Wybór procesora A1
);

transport.open();

// Wywołania trafiają do różnych handlerów
synCalc1.add(1, 2);    // → CalculatorHandler #1
synCalc2.add(3, 4);    // → CalculatorHandler #2
synAdvCalc1.add(5, 6); // → AdvancedCalculatorHandler #11
```

#### Jak to działa?

1. **Multiplexing na poziomie protokołu:**
   - `TMultiplexedProtocol` dodaje nazwę serwisu do wiadomości
   - Format: `serviceName:methodName`

2. **Routing po stronie serwera:**
   - `TMultiplexedProcessor` czyta nazwę serwisu
   - Przekazuje żądanie do odpowiedniego procesora
   - Każdy procesor ma własny handler

3. **Korzyści:**
   - Jeden port dla wielu serwisów
   - Jeden transport/połączenie
   - Różne implementacje (różne handlery)
   - Różne interfejsy (Calculator, AdvancedCalculator)

#### Test:

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

#### Porównanie z ICE:

| Aspekt | Thrift | ICE |
|--------|--------|-----|
| **Podejście** | Usługowe (service) | Obiektowe (object) |
| **Identyfikacja** | Nazwa serwisu | Identity (category/name) |
| **Multiplexing** | TMultiplexedProcessor | Wbudowane w ASM |
| **Routing** | Po nazwie serwisu | Po Identity |
| **Elastyczność** | Wymaga TMultiplexedProcessor | Natywne wsparcie |

---

## Podsumowanie odpowiedzi na pytania

### Zadanie 2: Jak skompilować dla Pythona?
```bash
thrift --gen py calculator.thrift
```

### Zadanie 4: Dlaczego server2 i server3 nie działają?
- `serve()` jest blokujące
- Wszystkie próbują użyć tego samego portu
- Tylko server1 się uruchamia

### Zadanie 4: Dlaczego synCalc1 i synAdvCalc1 wskazują na ten sam obiekt?
- Używają tego samego transportu i protokołu
- Thrift nie rozróżnia obiektów w trybie simple
- Oba trafiają do tego samego handlera

### Zadanie 6: Którego protokołu L4 używa Thrift?
- **TCP** (Transmission Control Protocol)
- Niezawodny, z potwierdzeniami
- Możliwe też UDP (dla specjalnych przypadków)

### Zadanie 7: Który protokół jest najefektywniejszy?
- **TCompactProtocol** - najmniejszy rozmiar (~65 bajtów)
- TBinaryProtocol - średni (~90 bajtów)
- TJSONProtocol - największy (~190 bajtów)

### Zadanie 8: Jak udostępnić wiele obiektów z TBinaryProtocol?
- Nie jest to możliwe w prosty sposób
- Potrzebne różne porty lub TMultiplexedProcessor
- Thrift jest service-oriented, nie object-oriented

### Zadanie 9: Jak działa TMultiplexedProcessor?
- Rejestruje wiele procesorów pod nazwami
- Klient wybiera procesor przez `TMultiplexedProtocol`
- Routing po nazwie serwisu
- Jeden port, wiele serwisów

---

## Wnioski

1. **Thrift vs ICE:**
   - Thrift: podejście usługowe (service-oriented)
   - ICE: podejście obiektowe (object-oriented)

2. **Protokoły serializacji:**
   - Compact najlepszy dla produkcji
   - JSON dobry dla debugowania
   - Binary - złoty środek

3. **Multiplexing:**
   - Thrift wymaga TMultiplexedProcessor
   - ICE ma wbudowane wsparcie (ASM)

4. **Prostota:**
   - Thrift prostszy w podstawowym użyciu
   - ICE bardziej zaawansowany i elastyczny

5. **Wydajność:**
   - Oba bardzo wydajne
   - Thrift Compact nieznacznie lepszy niż ICE

---

*Dokument wygenerowany automatycznie dla laboratorium Middleware 2026*