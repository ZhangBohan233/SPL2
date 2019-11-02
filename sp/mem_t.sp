class A {
    var a;

    fn A() {
        this.a = 6;
    }

    fn __getitem__(i) {
        return 123;
    }

    fn test() {
        return this[0];
    }
}

x := new A();
println(x);
gg := "333";
y := 3;
println(y);

//memory_view();
memory.available();
memory.gc();
memory.available();

//memory_view();

z := new A();
println(id(x));
println(id(z));
println(z);
println(x);

fn func(r) {
    return fn () {
        return r + 2;
    }
}

println(func(5)());
memory.gc();
func(4);
