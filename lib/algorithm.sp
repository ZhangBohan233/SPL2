import "math"


fn bubbleSort(lst) {
    const length = lst.size();
    for var i = 0; i < length; i++ {
        var swaps = 0;
        for var j = 0; j < length - 1; j++ {
            if lst[j] > lst[j+1] {
                lst.swap(j, j+1);
                swaps++;
            }
        }
        if (swaps == 0) {
            return;
        }
    }
}


fn gnomeSort(lst) {
    const length = lst.size();

}


/*
 * Sorts the <lst> with merge sort algorithm.
 */
fn mergeSort(lst) {
    const length = lst.size();
    var step = 1;
    while step < length {
        for var i = 0; i < length; i += step * 2 {
            var mid = i + step;
            var end = mid + step;
            if end > length {
                end = length;
            }
            if mid > length {
                mid = length;
            }

            var c_len = end - i;
            var i1 = i;
            var i2 = mid;
            var ci = 0;
            var cache = list();

            while i1 < mid && i2 < end {
                if lst[i1] < lst[i2] {
                    cache.append(lst[i1]);
                    ci += 1;
                    i1 += 1;
                } else {
                    cache.append(lst[i2]);
                    ci += 1;
                    i2 += 1;
                }
            }
            var remain = mid - i1;
            if remain > 0 {
                for var x = 0; x < remain; x++ {
                    cache.append(lst[i1 + x]);
                }
                for var x = 0; x < c_len; x++ {
                    lst[i + x] = cache[x];
                }
            } else {
                for var x = 0; x < ci; x++ {
                    lst[i + x] = cache[x];
                }
            }
        }
        step *= 2;
    }
}


/*
 * Returns a list with length <length> containing random integers in range [min, max].
 */
fn randList(length, min, max) {
    var lst = [];
    var r = max - min;
    for var i = 0; i < length; i += 1 {
        var x = math.random() * r + min;
        var xi = int(x);
        lst.append(xi);
    }
    return lst;
}
