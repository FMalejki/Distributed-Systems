package sr.ice.server;

import Demo.A;
import Demo.Calc;
import Demo.DivisionByZero;
import com.zeroc.Ice.Current;

public class CalcI implements Calc {
	private static final long serialVersionUID = -2448962912780867770L;
	long counter = 0;

	@Override
	public long add(int a, int b, Current __current) {
		// Task 9: Show which object is being served
		System.out.println("ADD: a = " + a + ", b = " + b + ", result = " + (a + b));
		System.out.println("  Serving object: " + __current.id.category + "/" + __current.id.name);

		if (a > 1000 || b > 1000) {
			try {
				Thread.sleep(6000);
			} catch (InterruptedException ex) {
				Thread.currentThread().interrupt();
			}
		}

		if (__current.ctx.values().size() > 0) {
			System.out.println("There are some properties in the context");
		}

		return a + b;
	}

	@Override
	public long subtract(int a, int b, Current __current) {
		// Task 7: Implementation of subtract operation
		System.out.println("SUBTRACT: a = " + a + ", b = " + b + ", result = " + (a - b));
		System.out.println("  Serving object: " + __current.id.category + "/" + __current.id.name);
		return a - b;
	}

	@Override
	public /*synchronized*/ void op(A a1, short b1, Current current) {
		System.out.println("OP" + (++counter));
		try {
			Thread.sleep(500);
		} catch (java.lang.InterruptedException ex) {
			Thread.currentThread().interrupt();
		}
	}

	@Override
	public double avg(long[] numbers, Current __current) throws DivisionByZero {
		// Task 13: Implementation of avg operation with exception handling
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
}