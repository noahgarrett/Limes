
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

// Variable Re-assignment
name = "this name";

// Data Structures
[1, "two", true]        // Arrays
{"test": 12, 2: 14}     // Objects / Dictionaries

// Indexing
let a = [1, 2];
let b = {"one": 1};
a[0];
b["one"];

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
len() -> 1 Argument (array or string)
print() -> 1 Argument (integer)

// Import Statements
import "folder/file.lime";

// While Loops
while true {
    print(69);
}

// For Loops
for (let i = 0; i < 10; i = i + 1) {
    print(i);
}
```