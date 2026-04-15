# Podsumowanie Zmian w Kodzie - Mapowanie do Zadań

## Przegląd wszystkich zmian

Ten dokument mapuje wszystkie zmiany w kodzie do konkretnych zadań z instrukcji laboratoryjnej.

---

## 📝 Zmiany w plikach

### 1. `slice/calculator.ice` - Definicja interfejsu

#### Zadanie 13: Dodanie operacji avg z sekwencjami
```slice
// Nowy wyjątek dla pustej sekwencji
exception DivisionByZero {
    string reason;
};

// Nowy typ sekwencji
sequence<long> LongSeq;

// Nowa operacja
idempotent double avg(LongSeq numbers) throws DivisionByZero;
```

**Linie:** 11-14, 40-42

**Cel:** Umożliwienie obliczania średniej z sekwencji liczb z obsługą wyjątków

#### Zadanie 14: Operacje idempotentne
```slice
idempotent long add(int a, int b);
idempotent long subtract(int a, int b);
idempotent double avg(LongSeq numbers) throws DivisionByZero;
```

**Linie:** 28-30, 40

**Cel:** Oznaczenie operacji jako idempotentnych (bezpieczne do powtarzania)

**Kompilacja wymagana:**
```bash
slice2java --output-dir generated slice/calculator.ice
```

---

### 2. `src/sr/ice/server/CalcI.java` - Implementacja serwanta

#### Zadanie 7: Implementacja operacji subtract
```java
@Override
public long subtract(int a, int b, Current __current) {
    System.out.println("SUBTRACT: a = " + a + ", b = " + b + ", result = " + (a - b));
    System.out.println("  Serving object: " + __current.id.category + "/" + __current.id.name);
    return a - b;
}
```

**Linie:** 31-36

**Cel:** Pełna implementacja operacji odejmowania

#### Zadanie 9: Identyfikacja obsługiwanego obiektu
```java
System.out.println("  Serving object: " + __current.id.category + "/" + __current.id.name);
```

**Linie:** 16, 35, 52

**Cel:** Serwant może sprawdzić, dla którego obiektu ICE realizuje wywołanie

#### Zadanie 13: Implementacja operacji avg
```java
@Override
public double avg(long[] numbers, Current __current) throws DivisionByZero {
    System.out.println("AVG: calculating average of " + numbers.length + " numbers");
    System.out.println("  Serving object: " + __current.id.category + "/" + __current.id.name);
    
    if (numbers.length == 0) {
        throw new DivisionByZero("Cannot calculate average of empty sequence");
    }
    
    long sum = 0;
    for (long num : numbers) {
        sum += num;
    }
    
    double result = (double) sum / numbers.length;
    System.out.println("  Result: " + result);
    return result;
}
```

**Linie:** 48-64

**Cel:** Obliczanie średniej z sekwencji z obsługą wyjątku dla pustej sekwencji

---

### 3. `src/sr/ice/server/IceServer.java` - Konfiguracja serwera

#### Zadanie 9: Wiele obiektów, wspólny serwant
```java
// Task 9: Multiple objects, shared servant
// calc33 shares the same servant as calc11 (calcServant1)
// Uncomment to test:
// adapter.add(calcServant1, new Identity("calc33", "calc"));
```

**Linie:** 40-43

**Cel:** Demonstracja mapowania wielu obiektów ICE na jednego serwanta

**Jak przetestować:**
1. Odkomentuj linię 43
2. Uruchom serwer
3. Klient może łączyć się z calc11 lub calc33 (ten sam serwant)

#### Zadanie 10: Wiele obiektów, dedykowane serwanty
```java
// Task 10: Multiple objects, dedicated servants
// calc33 has its own dedicated servant (calcServant3)
// Uncomment to test (comment out Task 9 first):
// CalcI calcServant3 = new CalcI();
// adapter.add(calcServant3, new Identity("calc33", "calc"));
```

**Linie:** 45-49

**Cel:** Demonstracja mapowania każdego obiektu ICE na osobnego serwanta

**Jak przetestować:**
1. Zakomentuj Zadanie 9
2. Odkomentuj linie 48-49
3. Uruchom serwer
4. calc33 ma teraz własnego serwanta z osobnym stanem

---

### 4. `src/sr/ice/client/IceClient.java` - Klient

#### Zadanie 13: Wywołania operacji avg
```java
case "avg":
    // Task 13: Test avg operation with valid sequence
    long[] nums = {10, 20, 30, 40, 50};
    try {
        double avg = obj1.avg(nums);
        System.out.println("AVERAGE = " + avg);
    } catch (Demo.DivisionByZero ex) {
        System.out.println("ERROR: " + ex.reason);
    }
    break;

case "avg-empty":
    // Task 13: Test avg operation with empty sequence (should throw exception)
    long[] emptyNums = {};
    try {
        double avg = obj1.avg(emptyNums);
        System.out.println("AVERAGE = " + avg);
    } catch (Demo.DivisionByZero ex) {
        System.out.println("ERROR (expected): " + ex.reason);
    }
    break;

case "avg-large":
    // Task 13: Test avg operation with large sequence
    long[] largeNums = new long[100];
    for (int i = 0; i < 100; i++) {
        largeNums[i] = i + 1;
    }
    try {
        double avg = obj1.avg(largeNums);
        System.out.println("AVERAGE = " + avg);
    } catch (Demo.DivisionByZero ex) {
        System.out.println("ERROR: " + ex.reason);
    }
    break;
```

**Linie:** 59-91

**Cel:** Testowanie operacji avg w różnych scenariuszach

**Komendy w menu:**
- `avg` - normalna sekwencja
- `avg-empty` - pusta sekwencja (test wyjątku)
- `avg-large` - duża sekwencja (100 elementów)

---

### 5. `client.config` - Konfiguracja klienta

#### Zadanie 22: Active Connection Management (ACM)
```
# Task 22: Active Connection Management - TCP connection timeout (in seconds)
# Default is 60 seconds. Set to 30 for faster observation of connection closure.
Ice.ACM.Timeout=30
```

**Linie:** 12-14

**Cel:** Konfiguracja czasu utrzymywania połączenia TCP

**Jak przetestować:**
1. Uruchom klienta z: `--Ice.Config=client.config`
2. Odkomentuj `Ice.Trace.Network=2` w pliku config
3. Obserwuj logi zamykania połączeń po 30 sekundach bezczynności

---

### 6. `server.config` - Konfiguracja serwera

#### Zadanie 17: Pula wątków adaptera
```
Adapter1.ThreadPool.Size=10
```

**Linia:** 8

**Cel:** Zwiększenie liczby wątków obsługujących żądania z 1 (domyślnie) do 10

**Jak przetestować:**
1. Uruchom serwer z: `--Ice.Config=server.config`
2. W kliencie wywołaj: `op-asyn1b 100`
3. Obserwuj równoległe wykonywanie operacji (10 naraz zamiast 1)

---

## 📊 Mapowanie zadań do zmian

| Zadanie | Plik | Typ zmiany | Opis |
|---------|------|------------|------|
| 7 | CalcI.java | Implementacja | Metoda subtract() |
| 9 | IceServer.java | Konfiguracja | Wspólny serwant dla wielu obiektów |
| 9 | CalcI.java | Logowanie | Wyświetlanie Identity obiektu |
| 10 | IceServer.java | Konfiguracja | Dedykowane serwanty |
| 13 | calculator.ice | IDL | Nowa operacja avg, wyjątek, sekwencja |
| 13 | CalcI.java | Implementacja | Metoda avg() z obsługą wyjątków |
| 13 | IceClient.java | Wywołania | Testy avg, avg-empty, avg-large |
| 14 | calculator.ice | IDL | Oznaczenie operacji jako idempotent |
| 17 | server.config | Konfiguracja | ThreadPool.Size=10 |
| 22 | client.config | Konfiguracja | Ice.ACM.Timeout=30 |

---

## 🔧 Zadania bez zmian w kodzie

Następujące zadania nie wymagają zmian w kodzie, tylko testowania istniejącej funkcjonalności:

### Zadanie 6: Sprawdzenie gniazd
- Użyj: `netstat -ano | grep 10000`
- Nie wymaga zmian w kodzie

### Zadanie 8: Pytania o serwanty
- Analiza istniejącego kodu
- Odpowiedzi w ANSWERS.md

### Zadanie 11: Analiza Wireshark
- Uruchom Wireshark z filtrem
- Nie wymaga zmian w kodzie

### Zadanie 12: Komunikacja między maszynami
- Zmień IP w stringToProxy() lub config
- Tymczasowa zmiana, nie commitowana

### Zadanie 15: Wywołanie z opóźnieniem
- Użyj komendy `add2` w kliencie
- Istniejąca funkcjonalność

### Zadanie 16: Wywołania asynchroniczne
- Użyj komend `add-asyn1`, `add-asyn2-req`, `add-asyn2-res`
- Istniejąca funkcjonalność

### Zadanie 18: Oneway
- Użyj `set-proxy oneway` + `op`
- Istniejąca funkcjonalność

### Zadanie 19: Datagram
- Użyj `set-proxy datagram` + `op`
- Istniejąca funkcjonalność

### Zadanie 20: Kompresja
- Użyj `compress on/off` + `op`/`op2`
- Istniejąca funkcjonalność

### Zadanie 21: Batching
- Użyj `set-proxy batch oneway` + `op 10` + `flush`
- Istniejąca funkcjonalność

### Zadanie 23: Docker
- Użyj docker-compose
- Instrukcje w cmdline.txt

### Zadanie 24: Analiza pcapng
- Otwórz ice.pcapng w Wireshark
- Nie wymaga zmian w kodzie

---

## 🚀 Kolejność wykonywania zmian

### Krok 1: Modyfikacja IDL
```bash
# Edytuj slice/calculator.ice
# Dodaj: DivisionByZero, LongSeq, avg(), idempotent
```

### Krok 2: Kompilacja
```bash
slice2java --output-dir generated slice/calculator.ice
```

### Krok 3: Implementacja serwanta
```bash
# Edytuj src/sr/ice/server/CalcI.java
# Dodaj: subtract(), avg(), logowanie Identity
```

### Krok 4: Rozszerzenie klienta
```bash
# Edytuj src/sr/ice/client/IceClient.java
# Dodaj: avg, avg-empty, avg-large
```

### Krok 5: Konfiguracja
```bash
# Edytuj server.config (ThreadPool.Size)
# Edytuj client.config (ACM.Timeout)
```

### Krok 6: Kompilacja Maven
```bash
mvn clean compile package
```

### Krok 7: Testowanie
```bash
# Terminal 1
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.server.IceServer --Ice.Config=server.config

# Terminal 2
java -cp target/ice-client-server-1.0-SNAPSHOT.jar sr.ice.client.IceClient --Ice.Config=client.config
```

---

## 📚 Dokumentacja

- **ANSWERS.md** - Szczegółowe odpowiedzi na wszystkie pytania
- **README_EXERCISES.md** - Instrukcje uruchamiania i testowania
- **CODE_CHANGES_SUMMARY.md** - Ten dokument

---

## ✅ Checklist implementacji

- [x] Zadanie 7: Implementacja subtract()
- [x] Zadanie 9: Wspólny serwant (kod z komentarzem)
- [x] Zadanie 10: Dedykowane serwanty (kod z komentarzem)
- [x] Zadanie 13: Operacja avg z sekwencjami i wyjątkami
- [x] Zadanie 14: Oznaczenie operacji jako idempotent
- [x] Zadanie 17: Konfiguracja puli wątków
- [x] Zadanie 22: Konfiguracja ACM timeout
- [x] Dokumentacja: ANSWERS.md
- [x] Dokumentacja: README_EXERCISES.md
- [x] Dokumentacja: CODE_CHANGES_SUMMARY.md

---

**Uwaga:** Po każdej zmianie w pliku .ice należy ponownie skompilować:
```bash
slice2java --output-dir generated slice/calculator.ice
mvn clean compile package