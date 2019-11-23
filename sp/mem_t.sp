class A {
    var a;
    var b = 6;

    fn A(x) {
        a = malloc(array(length=x));
        for i := 0; i < x; i++ {
            set(i, i);
        }
    }

    fn set(i, v) {
        a[i] = v;
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

fn main(argv) {
    var a = new List();
    //a.set(1, 3);
    //a.a;
}
