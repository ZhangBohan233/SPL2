class A {
    var si;

    fn A(i) {
        si = string(i);
    }
}

lst0 := [];
for i := 0; i < 10; i++ {
    lst0.append(i);
}

memory.status();
memory.gc();
memory.status();

lst := [];
st := system.time();
for i := 0; i < 10; i++ {
    lst.append(new A(i));
}
end := system.time();
println(end - st);
memory.status();
memory.gc();
memory.status();

println(lst0);

fn loop() {
    lst := [];
    for i:=0; i < 20; i++ {
        memory.gc();
        println(i);
        lst.append(i);
    }
    println(lst);
}
loop();
