import "math"

fn f(x) {
    return math.pow(x, 3) - 2 * math.pow(x, 2) - 7 * x + 3;
}

fn g(x) {
    return 3 * math.pow(x, 2) - 4 * x - 7;
}
println(f(4));
println(g(4));
for i := 0; i < 7; i++ {
    print(f(i) % 7);
    print(",");
}
println();
for i := 0; i < 49; i++ {
    if f(i) % 49 == 0 {
        println(i);
    }
}
