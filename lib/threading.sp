import "functions"


class Thread {

    var process;

    function Thread(target, args) {
        process = natives.thread(target, args);
    }

    function set_daemon(d) {
        process.set_daemon(d);
    }

    function start() {
        process.start();
    }

    function alive() {
        return process.alive();
    }
}


class ThreadPool {


    function ThreadPool(pool_size) {

    }
}

/*
 * Blocks the main thread until the <thread> finishes.
 */
function await(thread) {
    while (thread.alive()) {
        system.sleep(1);
    }
}

function is_alive(th) {
    return th.alive();
}

function await_all(thread_list) {
    while (any(is_alive, thread_list)) {
        system.sleep(1);
    }
}
