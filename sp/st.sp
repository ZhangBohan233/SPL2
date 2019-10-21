a := "abcd";
println(a[1]);
b := [3, 3, 4, 2];
println(b);
if a == "abcd" {
    println(999);
} else {
    println(777);
}
c := a + "ee";
println(c.substring(1, 3));
println("123.5".is_number());
println(",1,22,333,4,".split(","));
println("asdfg".contains("g"));
println("Test content: str %s, int %d, float %f, round float %4f".format("ggg", 123, 213.33, 3333.4543623523));
