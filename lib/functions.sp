/*
 * Passes every element from <lst> through the callable <ftn> and returns the collection of
 * results, in the original order.
 */
fn map(lst, ftn) {
    var res = [];
    for var element; lst {
        var cal = ftn(element);
        res.append(cal);
    }
    return res;
}


/*
 * Filters elements in <lst> with function <ftn>.
 * Only elements make <ftn> returns <true> will be in the retuning list.
 */
fn filter(lst, ftn) {
    var res = [];
    for var element; lst {
        if ftn(element) {
            res.append(element);
        }
    }
    return res;
}


/*
 * Returns true iff every element in <lst> satisfies boolean function <ftn>.
 */
fn all(lst=null) {
    for var element; lst {
        var res;
        if ftn === null {
            res = element;
        } else {
            res = ftn(element);
        }
        if !res {
            return false;
        }
    }
    return true;
}


/*
 * Returns true iff any element in <lst> satisfies boolean function <ftn>.
 */
fn any(lst, ftn=null) {
    for var element; lst {
        var res;
        if ftn === null {
            res = element;
        } else {
            res = ftn(element);
        }
        if res {
            return true;
        }
    }
    return false;
}


/*
 * Performs the same operation to every element until it went into one.
 */
fn reduce(lst, ftn) {
    var result = null;
    for var element; lst {
        if result {
            result = ftn(result, element);
        } else {
            result = element;
        }
    }
    return result;
}


/*
 * Returns the sum of a list.
 */
fn sum(lst) {
    return reduce(lst, (x, y) -> x + y);
}


/*
 * Returns the number of items in an iterable that make the `ftn` returns `true`.
 */
fn count(iter, ftn) {
    return filter(iter, ftn).size();
}
