import "functions"


class Thread {

    var process;

    fn Thread(target, args) {
        process = natives.thread(target, args);
    }

    fn set_daemon(d) {
        process.set_daemon(d);
    }

    fn start() {
        process.start();
    }

    fn alive() {
        return process.alive();
    }
}


class ThreadPool {


    fn ThreadPool(pool_size) {

    }
}

/*
 * Blocks the main thread until the <thread> finishes.
 */
fn await(thread) {
    while thread.alive() {
        system.sleep(1);
    }
}

fn is_alive(th) {
    return th.alive();
}

fn await_all(thread_list) {
    while any(is_alive, thread_list) {
        system.sleep(1);
    }
}
