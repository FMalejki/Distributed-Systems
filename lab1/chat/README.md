# Chat Application

Aplikacja chat z obsługą TCP, UDP i multicast.

## Funkcjonalności

- **TCP**: Podstawowa komunikacja chat z serwerem wielowątkowym
- **UDP**: Przesyłanie wiadomości multimedialnych (ASCII Art)
- **Multicast**: Bezpośrednia komunikacja grupowa między klientami

## Wymagania

- Python 3.6+
- Brak dodatkowych bibliotek

## Uruchomienie

### Serwer

```bash
python server.py
```

Serwer uruchamia się na porcie 12345 (domyślnie) i obsługuje:
- TCP na porcie 12345
- UDP na porcie 12345
- Multicast na grupie 224.0.0.1

### Klient

Mozna określić host i port w razie potrzeby.

```bash
python client.py [host] [port]
```

Przykłady:
```bash
python client.py
python client.py 127.0.0.1 12345
python client.py 192.168.1.100 12345
```

## Użycie

Po uruchomieniu klienta:

1. Podaj nickname
2. Wpisz wiadomość i naciśnij Enter - wysyła przez TCP
3. Wpisz `U` + wiadomość - wysyła przez UDP
4. Wpisz `M` + wiadomość - wysyła przez multicast
5. Wpisz `quit` - wyjście

### Przykłady

```
> Hello everyone!                    # TCP
> U ASCII Art message                # UDP
> M Multicast to all                 # Multicast
> quit                               # Exit
```

## Architektura

### Serwer
- ThreadPoolExecutor dla wydajnej obsługi wielu klientów
- Osobne wątki dla TCP i UDP
- Synchronizacja dostępu do listy klientów (threading.Lock)
- Nie wysyła wiadomości do nadawcy

### Klient
- Osobne wątki dla odbierania TCP, UDP i multicast
- Główny wątek do wysyłania wiadomości
- Obsługa trzech protokołów jednocześnie

## Testowanie

Uruchom serwer i minimum 2 klientów w osobnych terminalach:

Terminal 1:
```bash
python server.py
```

Terminal 2:
```bash
python client.py
# itd parametry
```

Terminal 3:
```bash
python client.py
# itd inne parametry
```

