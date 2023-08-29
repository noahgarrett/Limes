
```
// Comments

// Data Types
true, false     // Booleans
1, 2            // Integers
1.5, 2.5        // Floats
"apple", "yes"  // Strings
null            // Null Values

// Variable Declaration
let name = "value";

// Data Structures
[1, "two", true]        // Arrays
{"test": 12, 2: 14}     // Objects / Dictionaries

// Basic Arithmetic
+ - * /

// Basic Comparison
== != < > <= >=

// Conditionals
if true {
    10;
} else {
    11;
}

// Functions
// Like in Rust and Python, all functions return a value
let test = fn(a, b) { };
    // Explicit Returns
    let ex = fn() { return 69; };
    // Implicit Returns
    let im = fn() { 69; };

// Function Calling
test(1, 2);
let var = ex();

// First-Class Functions
let returnsOne = fn() { 1; };
let returnsOneReturner = fn() { returnsOne; };
returnsOneReturner()();

// Local Scopes with functions
let globalSeed = 50;

let minusOne = fn() {
    let num = 1;
    globalSeed - num;
};

let minusTwo = fn() {
    let num = 2;
    globalSeed - num;
};

minusOne() + minusTwo();

// Functions with arguments
let sum = fn(a, b) {
    a + b;
};

sum(1, 2);

// Builtin Functions
let get_length = fn(array_or_string) {
    return len(array_or_string);
};

let a = [1, 2, 3];
get_length(a);
```