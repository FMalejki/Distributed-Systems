package sr.thrift.server;

import org.apache.thrift.TException;

import sr.gen.thrift.OperationType;
import sr.gen.thrift.InvalidArguments;
import sr.gen.thrift.NegativeNumber;
import sr.gen.thrift.AdvancedCalculator;

// Generated code

import java.util.Set;

public class AdvancedCalculatorHandler implements AdvancedCalculator.Iface {

	int id;

	public AdvancedCalculatorHandler(int id) {
		this.id = id;
	}

	public int add(int n1, int n2) {
		System.out.println("AdvCalcHandler#" + id + " add(" + n1 + "," + n2 + ")");
		//try { Thread.sleep(9000); } catch(java.lang.InterruptedException ex) { }
		System.out.println("DONE");
		return n1 + n2;
	}


	@Override
	public double op(OperationType type, Set<Double> val) throws TException 
	{
		System.out.println("AdvCalcHandler#" + id + " op() with " + val.size() + " arguments");
		
		if(val.size() == 0) {
			throw new InvalidArguments(0, "no data");
		}
		
		double res = 0;
		switch (type) {
		case SUM:
			for (Double d : val) res += d;
			return res;
		case AVG:
			for (Double d : val) res += d;
			return res/val.size();
		case MIN:
			return 0;
		case MAX:
			return 0;
		}
		
		return 0;
	}

	
	@Override
	public int subtract(int num1, int num2) throws TException {
		System.out.println("AdvCalcHandler#" + id + " subtract(" + num1 + "," + num2 + ")");
		return num1 - num2;
	}

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

}

