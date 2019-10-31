class A {
    private var p = 5;
    private var x;

    fn A(x) {
        this.x = x;
        p = 6;
    }

    private fn foo() {
        return x;
    }

    fn bar() {
        return foo();
    }
}

a := new A(3);
println(a.x);
a.bar();
