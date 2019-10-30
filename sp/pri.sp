class A {
    var _p = 5;
    var _x;

    fn A(x) {
        this._x = x;
        _p = 6;
    }

    fn _foo() {
        return _x;
    }

    fn foo() {
        return _foo();
    }
}

a := new A(3);
println(a._x);
a._foo();
