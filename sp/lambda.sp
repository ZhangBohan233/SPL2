import "functions"

lst := [1,2,3,4,5,6];
res := functions.map(lst, e -> e + 1);
lst2 := [[1,2], [1,2,3,4], [5,6,2,1]];
res2 := functions.map(lst2, e ->
        functions.filter(e, e1 ->
                e1 % 2 == 0
        )
);
println(res);
println(res2);
res3 := functions.reduce(lst, (a, b) -> a + b);
println(res3);

fn lambda(x) {
    return e -> e * x;
}
res4 := functions.map(lst, lambda(5));
println(res4);

fn no_arg(f) {
    for i := 0; i < 5; i++ {
        f();
    }
}

var i = 0;
res5 := no_arg(() -> i++);
println(res5);
