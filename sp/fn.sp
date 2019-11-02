fn test(r) {
    return new Object <- {
        fn test() {
            return r + 1;
        }
    }
}

class A {
    var x = 1;
}

a := test(4);

memory.available();
memory.gc();
memory.available();
b := 999;

a.test();
memory.at(40);
