class Int {
    var n;

    fn Int(n) {
        this.n = n;
    }

    fn __lt__(x) {
        return n < x.n;
    }

    fn __add__(x) {
        return new Int(n + x.n);
    }

    fn __sub__(x) {
        return new Int(n - x.n);
    }
}

one := new Int(1);
two := new Int(2);

fn fib(n) {
    memory.gc();
    if n < two {
        return n;
    } else {
        return fib(n - one) + fib(n - two);
    }
}

println(fib(new Int(6)));

fn f1(n) {
    return f3(n) + f3(n) + f3(n);
}

fn f3(n) {
    memory.gc();

    return n + new Int(1) + new Int(1);
}

println(f1(new Int(5)));

//import "util"
//util.memoryView(get_env());
