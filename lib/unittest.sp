const TEST = new Annotation("Test");
const RUN_BEFORE = new Annotation("RunBefore");
const RUN_AFTER = new Annotation("RunAfter");

function testall() {
    const all_functions = get_all_tests();
    const run_before = all_functions[0];
    const run_after = all_functions[1];
    const functions = all_functions[2];
    const flags = all_functions[3];
    const failed = pair();

    // run before
    for (var ftn; run_before) ftn();

    // tests
    for (var name; functions) {
        var test = functions[name];
        var flag = flags[name];
        var exception = null;
        if (flag !== null) {
            if (flag.contains("exception")) {
                exception = flag["exception"];
            }
        }

        try {
            test();
        } catch (e: Exception) {
            if (!(e instanceof exception)) {
                failed[name] = e;
            }
        }
    }

    // run after
    for (var ftn; run_after) ftn();

    var fail_num = failed.size();
    var result = fail_num > 0 ? "Failed" : "Passed";

    var total = functions.size();
    var passed = total - fail_num;
    println("Test %s. Passed: %d out of %d".format(result, passed, total));
    for (var failure; failed) {
        println("%s: %r".format(failure, failed[failure].message), system.stderr);
    }
}

function get_all_tests() {
    var functions = {};
    var flags = {};
    var run_before = [];
    var run_after = [];
    var vars = natives.variables();
    for (var key; vars) {
        var value = vars.get(key);
        if (value instanceof Function) {
            if (value.annotations.contains(TEST)) {
                functions[key] = value;
                flags[key] = value.annotations.get(TEST).params;
            }
            if (value.annotations.contains(RUN_BEFORE)) {
                run_before.append(value);
            }
            if (value.annotations.contains(RUN_AFTER)) {
                run_after.append(value);
            }
        }
    }
    return ~[run_before, run_after, functions, flags];
}

function assert_equals(actual, expected) {
    if (actual != expected) {
        throw new AssertionException("Assertion failed. Expected %r, got %r".format(expected, actual));
    }
}
