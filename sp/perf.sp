import "algorithm"
import "queue"
import "math"

class Test {
    abstract fn get_name();
}

class TestObj extends Test {

    var value;
    const name = "TestObj";

    fn TestObj(value) {
        this.value = value;
    }

    fn print_value() {
        println(value);
    }

    @Override
    fn get_name() {
        return name;
    }

    fn get_value() {
        return value;
    }

    fn fun() {
        value++;
        return this;
    }
}

fn main(args) {
    const t0 = system.time();

    for i := 0; i < 100_000; i++ {}

    const t1 = system.time();
    print("loop: ");
    println(t1 - t0);

    math.fib(20);

    const t2 = system.time();
    print("fib: ");
    println(t2 - t1);

    memory.status();

    const lst = algorithm.randList(500, -32768, 32767);

    const t3 = system.time();
    algorithm.mergeSort(lst);
    const t4 = system.time();

    free(lst);

    print("sort: ");
    println(t4 - t3);

    memory.status();

    var link_lst = new queue.LinkedList();
    for var i = 0; i < 1000; i++ {
        var obj = new TestObj(i);
        link_lst.add_last(obj);
    }
    free(link_lst);

    const t5 = system.time();
    print("object: ");
    println(t5 - t4);

    var s = "";
    for i := 0; i < 1000; i++ {
        s += "a";
    }
    free(s);
    const t6 = system.time();
    print("string: ");
    println(t6 - t5);

    memory.status();
    memory.sp();
    memory.view();
}
