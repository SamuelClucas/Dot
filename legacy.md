i_ 'a = 1; // int a = 1; but there are no variables, only pointers to memory

''a; //dereference a to get the value at memory (there are no double pointers allowed)

// you don't declare arrays like variables, you declare arrays by pointing to contiguous memory
i_ 'q 10; //int q[10];
''q 5; //dereference q[5] to get the value of q[5], which at this point is garbage
//^this way there's no discrepancy between the array and the pointer. there's no [] operator here, the pointer syntax remains consistent
//somehow i need to think about how to declare which memory is allocated for the array

// functions will work like this
f(i_ 'x){ // pass address stored in pointer to int type, @ is almost an ancilliary type
    //expression with local variables, but must use input somehow
}; // function accepts 1 int when called

// call the function
f('a); // error if a is not an int pointer, or more than 1 int passed to f. at the last function call, a goes out of scope. any variables unused in the program will throw an error

// equivalent to classes
set name{
    f(i_ 'x){
        //expression with local variables, but must use input somehow. input is passed by reference using pointer notation
        print(''x + 3); //prints value x + 3. so type mismatch will error
    }
    _ l(i_ 'x, i_ 'y); // just declaration, no definition. might force specifying return type, but not sure as scope works differently. this is an example of void return syntax
}

// out of set definition is allowed if set declared like
set name{ // open curly brace indicates definition is elsewhere, but reserve the symbol
// add a function to the set
name<-f(i_ 'x){
    //expression with local variables, but must use input somehow
}
// then call the function
name.f(a); // pass address stored in pointer a to int in memory. 

// argument order is important, so if you have a function that takes 2 arguments, you need to pass them in the right order
name<-j(i_ 'f, i_ 'g, s_ 'k){
    // definition, using 'f 'g and string 'k somehow
    }

s_ 'ex = 'hello';
i_ 'b = 2;

name.j('a, 'b, 'ex); // within the function, these addresses are assigned to local variables as in the function definition
// might force programmer to explicitly deinitialise variables when they are no longer needed
/a; // deinitialise a

# Dot
