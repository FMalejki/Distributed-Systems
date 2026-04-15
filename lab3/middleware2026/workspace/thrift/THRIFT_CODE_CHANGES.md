# Apache Thrift - Podsumowanie Zmian w Kodzie

## Przegląd wszystkich zmian

Ten dokument mapuje wszystkie zmiany w kodzie do konkretnych zadań z instrukcji laboratoryjnej.

---

## 📝 Zmiany w plikach

### 1. `calculator.thrift` - Definicja interfejsu IDL

#### Zadanie 5: Nowy wyjątek NegativeNumber

```thrift
// Task 5: New exception for negative numbers
exception NegativeNumber {
  1: i32 number,
  2: string message
}
```

**Linie:** 37-41

**Cel:** Obsługa błędów dla operacji factorial z liczbami ujemnymi

#### Zadanie 5: Nowa operacja factorial

```thrift
service AdvancedCalculator extends Calculator {
   double op(1:OperationType type, 2: set<double> val) throws (1: InvalidArguments ex),
   
   // Task 5: New operation - calculate factorial
   // Returns factorial of n (n!)
   // Throws NegativeNumber exception if n < 0
   i64 factorial(1: i32 n) throws (1: NegativeNumber ex),
}
```

**Linie:** 49-55

**Cel:** Dodanie operacji obliczającej silnię liczby

**Kompilacja wymagana:**
```bash
thrift --gen java calculator.thrift
```

---

### 2. `src/sr/thrift/server/CalculatorHandler.java` - Implementacja Calculator

#### Zadanie 5: Implementacja metody subtract

**Przed:**
```java
@Override
public int subtract(int num1, int num2) throws TException {
    // TODO Auto-generated method stub
    return 0;
}
```

**Po:**
```java
@Override
public int subtract(int num1, int num2) throws TException {
    System.out.println("CalcHandler#" + id + " subtract(" + num1 + "," + num2 + ")");
    return num1 - num2;
}
```

**Linie:** 24-28

**Cel:** Pełna implementacja operacji odejmowania

---

### 3. `src/sr/thrift/server/AdvancedCalculatorHandler.java` - Implementacja AdvancedCalculator

#### Zadanie 5: Import nowego wyjątku

```java
import sr.gen.thrift.NegativeNumber;
```

**Linia:** 7

**Cel:** Umożliwienie rzucania wyjątku NegativeNumber

#### Zadanie 5: Implementacja metody subtract

```java
@Override
public int subtract(int num1, int num2) throws TException {
    System.out.println("AdvCalcHandler#" + id + " subtract(" + num1 + "," + num2 + ")");
    return num1 - num2;
}
```

**Linie:** 56-60

**Cel:** Implementacja subtract w AdvancedCalculator (dziedziczy z Calculator)

#### Zadanie 5: Implementacja metody factorial

```java
// Task 5: New operation - factorial
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
        // Prevent overflow for large numbers
        if (result < 0) {
            throw new NegativeNumber(n, "Factorial overflow for n=" + n);
        }
    }
    
    System.out.println("  Result: " + result);
    return result;
}
```

**Linie:** 62-85

**Cel:** Obliczanie silni z obsługą:
- Liczb ujemnych (wyjątek)
- Przypadków brzegowych (0!, 1!)
- Przepełnienia (overflow detection)

**Algorytm:**
- Iteracyjne mnożenie od 2 do n
- Sprawdzanie przepełnienia (result < 0)
- Logowanie wyniku

---

### 4. `src/sr/thrift/client/ThriftClient.java` - Klient

#### Zadanie 5: Wywołanie subtract

```java
else if (line.equals("subtract1")) {
    // Task 5: Test subtract operation
    int arg1 = 100;
    int arg2 = 42;
    int res = synCalc1.subtract(arg1, arg2);
    System.out.println("subtract(" + arg1 + "," + arg2 + ") returned " + res);
}
```

**Linie:** 111-117

**Cel:** Test operacji odejmowania

#### Zadanie 5: Wywołanie factorial (normalny przypadek)

```java
else if (line.equals("fact")) {
    // Task 5: Test factorial operation
    int arg = 5;
    long res = synAdvCalc1.factorial(arg);
    System.out.println("factorial(" + arg + ") returned " + res);
}
```

**Linie:** 118-123

**Cel:** Test factorial dla małej liczby (5! = 120)

#### Zadanie 5: Wywołanie factorial (większa liczba)

```java
else if (line.equals("fact10")) {
    // Task 5: Test factorial with larger number
    int arg = 10;
    long res = synAdvCalc1.factorial(arg);
    System.out.println("factorial(" + arg + ") returned " + res);
}
```

**Linie:** 124-129

**Cel:** Test factorial dla większej liczby (10! = 3628800)

#### Zadanie 5: Wywołanie factorial (test wyjątku)

```java
else if (line.equals("fact-neg")) {
    // Task 5: Test factorial with negative number (should throw exception)
    try {
        int arg = -5;
        long res = synAdvCalc1.factorial(arg);
        System.out.println("factorial(" + arg + ") returned " + res);
    } catch (sr.gen.thrift.NegativeNumber ex) {
        System.out.println("ERROR (expected): " + ex.message + " (number: " + ex.number + ")");
    }
}
```

**Linie:** 130-139

**Cel:** Test obsługi wyjątku dla liczby ujemnej

---

## 📊 Mapowanie zadań do zmian

| Zadanie | Plik | Typ zmiany | Opis |
|---------|------|------------|------|
| 5 | calculator.thrift | IDL | Nowy wyjątek NegativeNumber |
| 5 | calculator.thrift | IDL | Nowa operacja factorial |
| 5 | CalculatorHandler.java | Implementacja | Metoda subtract() |
| 5 | AdvancedCalculatorHandler.java | Import | Import NegativeNumber |
| 5 | AdvancedCalculatorHandler.java | Implementacja | Metoda subtract() |
| 5 | AdvancedCalculatorHandler.java | Implementacja | Metoda factorial() |
| 5 | ThriftClient.java | Wywołania | Test subtract1 |
| 5 | ThriftClient.java | Wywołania | Test fact |
| 5 | ThriftClient.java | Wywołania | Test fact10 |
| 5 | ThriftClient.java | Wywołania | Test fact-neg |

---

## 🔧 Zadania bez zmian w kodzie

Następujące zadania nie wymagają zmian w kodzie, tylko analizę i testowanie:

### Zadanie 1: Otwarcie projektu
- Otwórz katalog w IDE
- Nie wymaga zmian w kodzie

### Zadanie 2: Kompilacja .thrift
- Użyj: `thrift --gen java calculator.thrift`
- Nie wymaga zmian w kodzie źródłowym

### Zadanie 3: Analiza kodu
- Przejrzyj istniejące pliki
- Odpowiedzi w THRIFT_ANSWERS.md

### Zadanie 4: Uruchomienie i testowanie
- Uruchom serwer i klienta
- Testuj istniejącą funkcjonalność
- Odpowiedzi w THRIFT_ANSWERS.md

### Zadanie 6: Analiza Wireshark
- Uruchom Wireshark
- Filtr: `tcp.port == 9080 or tcp.port == 9081`
- Odpowiedzi w THRIFT_ANSWERS.md

### Zadanie 7: Porównanie protokołów
- Zmień protokół w kodzie (tymczasowo)
- Zmierz rozmiary w Wireshark
- Przywróć oryginalny protokół
- Wyniki w THRIFT_ANSWERS.md

### Zadanie 8: TBinaryProtocol - wiele obiektów
- Analiza istniejącego kodu serwera
- Testowanie trybu simple
- Odpowiedzi w THRIFT_ANSWERS.md

### Zadanie 9: TMultiplexedProcessor
- Analiza istniejącego kodu
- Testowanie trybu multiplex
- Odpowiedzi w THRIFT_ANSWERS.md

---

## 🚀 Kolejność wykonywania zmian

### Krok 1: Modyfikacja IDL
```bash
# Edytuj calculator.thrift
# Dodaj: NegativeNumber exception, factorial operation
```

### Krok 2: Kompilacja Thrift
```bash
thrift --gen java calculator.thrift
```

### Krok 3: Implementacja w handlerach
```bash
# Edytuj CalculatorHandler.java
# Dodaj: subtract()

# Edytuj AdvancedCalculatorHandler.java
# Dodaj: import NegativeNumber, subtract(), factorial()
```

### Krok 4: Rozszerzenie klienta
```bash
# Edytuj ThriftClient.java
# Dodaj: subtract1, fact, fact10, fact-neg
```

### Krok 5: Kompilacja Maven
```bash
mvn clean compile package
```

### Krok 6: Testowanie
```bash
# Terminal 1
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.server.ThriftServer

# Terminal 2
java -cp target/thrift-client-server-1.0-SNAPSHOT.jar sr.thrift.client.ThriftClient
```

**Testy:**
```
==> simple
==> subtract1
subtract(100,42) returned 58

==> fact
factorial(5) returned 120

==> fact10
factorial(10) returned 3628800

==> fact-neg
ERROR (expected): Factorial is not defined for negative numbers (number: -5)
```

---

## 📚 Dokumentacja

- **THRIFT_ANSWERS.md** - Szczegółowe odpowiedzi na wszystkie pytania
- **THRIFT_README.md** - Instrukcje uruchamiania i testowania
- **THRIFT_CODE_CHANGES.md** - Ten dokument

---

## ✅ Checklist implementacji

- [x] Zadanie 5: Wyjątek NegativeNumber w .thrift
- [x] Zadanie 5: Operacja factorial w .thrift
- [x] Zadanie 5: Implementacja subtract w CalculatorHandler
- [x] Zadanie 5: Implementacja subtract w AdvancedCalculatorHandler
- [x] Zadanie 5: Implementacja factorial w AdvancedCalculatorHandler
- [x] Zadanie 5: Wywołania w kliencie (subtract1, fact, fact10, fact-neg)
- [x] Dokumentacja: THRIFT_ANSWERS.md
- [x] Dokumentacja: THRIFT_README.md
- [x] Dokumentacja: THRIFT_CODE_CHANGES.md

---

## 🔍 Szczegóły implementacji

### Factorial - algorytm

**Przypadki specjalne:**
```java
if (n < 0) throw new NegativeNumber(...);  // Liczby ujemne
if (n == 0 || n == 1) return 1;            // 0! = 1, 1! = 1
```

**Obliczanie:**
```java
long result = 1;
for (int i = 2; i <= n; i++) {
    result *= i;
    if (result < 0) {  // Overflow detection
        throw new NegativeNumber(n, "Factorial overflow for n=" + n);
    }
}
```

**Limity:**
- Typ `i64` (long) w Thrift
- Maksymalna wartość: 2^63 - 1
- Factorial(20) = 2432902008176640000 (mieści się)
- Factorial(21) = overflow (nie mieści się)

### Subtract - implementacja

**Prosta operacja:**
```java
return num1 - num2;
```

**Logowanie:**
```java
System.out.println("CalcHandler#" + id + " subtract(" + num1 + "," + num2 + ")");
```

**Identyfikacja handlera:**
- `id` pozwala rozróżnić różne instancje handlera
- Przydatne w trybie multiplex

---

## 🎯 Porównanie z ICE

| Aspekt | Thrift | ICE |
|--------|--------|-----|
| **Definicja interfejsu** | .thrift (IDL) | .ice (Slice) |
| **Kompilator** | thrift --gen | slice2java |
| **Wyjątki** | exception | exception |
| **Sekwencje** | list<T>, set<T> | sequence<T> |
| **Typy całkowite** | i32, i64 | int, long |
| **Dziedziczenie** | extends | extends |
| **Multiplexing** | TMultiplexedProcessor | Wbudowane (ASM) |

---

## 💡 Wskazówki

1. **Po każdej zmianie w .thrift:**
   ```bash
   thrift --gen java calculator.thrift
   mvn clean compile package
   ```

2. **Sprawdzanie wygenerowanych klas:**
   ```bash
   ls gen-java/sr/gen/thrift/
   ```

3. **Debugowanie:**
   - Dodaj więcej `System.out.println()`
   - Sprawdź logi serwera
   - Użyj Wireshark do analizy komunikacji

4. **Testowanie wyjątków:**
   - Zawsze testuj przypadki brzegowe
   - Sprawdź czy wyjątek jest poprawnie rzucany
   - Sprawdź czy klient poprawnie obsługuje wyjątek

---

**Uwaga:** Wszystkie zmiany są kompatybilne wstecz. Istniejąca funkcjonalność nie została naruszona.

*Dokument wygenerowany automatycznie dla laboratorium Middleware 2026*