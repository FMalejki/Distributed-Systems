
#ifndef CALC_ICE
#define CALC_ICE

module Demo
{
  enum operation { MIN, MAX, AVG };
  
  exception NoInput {};
  
  // Task 13: Exception for division by zero (empty sequence)
  exception DivisionByZero {
    string reason;
  };
  
  // Task 13: Sequence type for avg operation
  sequence<long> LongSeq;

  struct A
  {
    short a;
    long b;
    float c;
    string d;
  }

  interface Calc
  {
    // Task 14: Idempotent operations - add and subtract always return same result for same inputs
    idempotent long add(int a, int b);
    idempotent long subtract(int a, int b);
    void op(A a1, short b1); //załóżmy, że to też jest operacja arytmetyczna ;)
    
    // Task 13: New operation to calculate average of a sequence
    // Task 14: avg is idempotent - same inputs always produce same output
    idempotent double avg(LongSeq numbers) throws DivisionByZero;
  };

};

#endif
