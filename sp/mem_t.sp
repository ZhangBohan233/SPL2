class A {
    var a;
    var b = 6;

    fn A(x) {
        b = x;
        a = malloc(array(length=x));
        for i := 0; i < x; i++ {
            set_(i, i);
        }
    }

    fn __free__() {
        if a instanceof Object {
            free(a);
        }
    }

    fn set_(i, v) {
        a[i] = v;
    }

    fn __str__() {
        var ca = chars(a);
        var cb = chars(b);
        var rtn = "A:" + cb + ca;
        free(ca);
        free(cb);
        //println(rtn);
        return malloc(rtn);
    }

    fn __repr__() {
        return __str__();
    }
}

class B {
    fn B() {
    }
}

fn t1() {
    var a = 2;
    var b = new A(a);
    malloc(b);
}

fn t2(x) {
    x.a++;
    return x.a;
    x;
}

fn t3() {
    return chars(112312);
}

fn t4(x) {
    return malloc(new A(x));
}

fn main(argv) {
    memory.status();
    var b = malloc(new B());
    var a = malloc(new List());
    for i := 0; i < 2; i++ {
        a.append(t4(i));
    }
    //natives.print(a);
    free(b);
    for var x; a {
        natives.print(x);
        free(x);
    }
    free(a);
    memory.view();
    memory.status();
    memory.available();
}
