class Node {
    var freq;
    var value;

    fn Node(freq) {
        this.freq = freq;
    }
}

fn generate_freq(lst) {
    var dict = {};
    for (var x; lst) {
        if (dict.contains(x)) {
            dict[x]++;
        } else {
            dict[x] = 1;
        }
    }
    return dict;
}
