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
    //memory.gc();
    if n < two {
        return n;
    } else {
        return fib(n - one) + fib(n - two);
    }
}

fn f1(n) {
    return f3(n) + f3(n);
}

fn f3(n) {
    memory.gc();

    return n + new Int(1);
}

f1(new Int(5));

fn nest(n) {
    return fn() {
        memory.gc();
        return n;
    }
}

fn out(n) {
    return nest(n)() + nest(n)();
}

out(new Int(4));

println(one);
free(one);
println(one);

import "util"
util.memoryView(get_env());
