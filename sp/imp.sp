import "pack/imp1.sp"
import "pack/../t2.sp"
import namespace "math"
import "util"

println(imp1);
imp1.doSomething();
println(t2.c instanceof Object);

if (main()) {
    println(eulerPhiFp(100));
}
util.memoryView(get_env());
