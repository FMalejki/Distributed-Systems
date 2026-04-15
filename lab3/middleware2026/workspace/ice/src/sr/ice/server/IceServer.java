package sr.ice.server;

import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.Identity;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;
import com.zeroc.Ice.InitializationException;

public class IceServer {
	public void t1(String[] args) {
		int status = 0;
		Communicator communicator = null;

		try {
			// 1. Inicjalizacja ICE - utworzenie communicatora
			communicator = Util.initialize(args);
            ObjectAdapter adapter = null;

            // 2. Konfiguracja adaptera
			try {
                // METODA 1 (polecana produkcyjnie): Konfiguracja adaptera Adapter1 jest w pliku konfiguracyjnym podanym jako parametr uruchomienia serwera (--Ice.Config=server.config)
                adapter = communicator.createObjectAdapter("Adapter1");
            }
            catch(InitializationException e) { //gdy plik konfiguracyjny nie został użyty lub nie zawiera definicji adaptera
                System.out.println("(using a hard-coded configuration)");
                // METODA 2 (niepolecana, dopuszczalna testowo): Konfiguracja adaptera Adapter1 jest w kodzie źródłowym
                //ObjectAdapter adapter = communicator.createObjectAdapterWithEndpoints("Adapter1", "tcp -h 127.0.0.2 -p 10000");
                //ObjectAdapter adapter = communicator.createObjectAdapterWithEndpoints("Adapter1", "tcp -h 127.0.0.2 -p 10000 : udp -h 127.0.0.2 -p 10000");
                adapter = communicator.createObjectAdapterWithEndpoints("Adapter2", "tcp -h 127.0.0.2 -p 10000 -z : udp -h 127.0.0.2 -p 10000 -z");
            }

			// 3. Utworzenie serwanta/serwantów
			CalcI calcServant1 = new CalcI();
			CalcI calcServant2 = new CalcI();

			// 4. Dodanie wpisów do tablicy ASM, skojarzenie nazwy obiektu (Identity) z serwantem
			adapter.add(calcServant1, new Identity("calc11", "calc"));
			adapter.add(calcServant2, new Identity("calc22", "calc"));
			
			// Task 9: Multiple objects, shared servant
			// calc33 shares the same servant as calc11 (calcServant1)
			// Uncomment to test:
			// adapter.add(calcServant1, new Identity("calc33", "calc"));
			
			// Task 10: Multiple objects, dedicated servants
			// calc33 has its own dedicated servant (calcServant3)
			// Uncomment to test (comment out Task 9 first):
			// CalcI calcServant3 = new CalcI();
			// adapter.add(calcServant3, new Identity("calc33", "calc"));

			// 5. Aktywacja adaptera i wejście w pętlę przetwarzania żądań
			adapter.activate();

			System.out.println("Entering event processing loop...");

			communicator.waitForShutdown();

		} catch (Exception e) {
			e.printStackTrace(System.err);
			status = 1;
		}
		if (communicator != null) {
			try {
				communicator.destroy();
			} catch (Exception e) {
				e.printStackTrace(System.err);
				status = 1;
			}
		}
		System.exit(status);
	}


	public static void main(String[] args) {
		IceServer app = new IceServer();
		app.t1(args);
	}
}