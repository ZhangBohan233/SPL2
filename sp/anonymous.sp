import "t2.sp"

abstract class A {
    var ini;

    fn A(ini) {
        this.ini = ini;
    }

    abstract fn write();
}

abstract class B {
    abstract fn read();
}

c := new B <- {
    @Override
    fn read() {
        return 0;
    }
}
println(c.read());

x := 2;
y := 3;
var b = new A(y) <- {
    @Override
    fn write() {
        return ini + x;
    }
}
b.write();

var ta = new t2.A(33) <- {
    fn xxx() {
        return y;
    }
}
ta.xxx();

obj := new Object <- {
    fn test() {
        println(y);
    }
}
obj.test();

for var i; range(5) {
    println(i);
}

for var i; range(10,5,-1) {
    println(i);
}
