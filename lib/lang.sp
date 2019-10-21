/*
 * Superclass of all spl exceptions.
 */
class Exception {
    var message = "";

    /*
     * Create a new <Exception>, with message <msg>.
     */
    fn Exception(msg="") {
        message = msg;
    }
}


/*
 * Exception of assertion failed.
 */
class AssertionException extends Exception {
    fn AssertionException(msg="") {
        Exception(msg);
    }
}


/*
 * Exception of annotations.
 *
 * Exception from all annotations should be derived from this exception.
 */
class AnnotationException extends Exception {
    fn AnnotationException(msg="") {
        Exception(msg);
    }
}


class IndexException extends Exception {
    fn IndexException(msg="") {
        Exception(msg);
    }
}


class ObjectTypeException extends Exception {
    fn ObjectTypeException(msg="") {
        Exception(msg);
    }
}


/*
 * A superclass of all iterator classes.
 */
abstract class Iterator {
    abstract fn Iterator();

    abstract fn __more__();

    abstract fn __next__();
}


/*
 * Superclass of all iterable classes.
 *
 * Iterable are typically used when calling for (iterable; )
 */
abstract class Iterable {

    /*
     * Returns an object to be iterated, probably an <Iterator>.
     */
    abstract fn __iter__();
}


abstract class OutputStream {
    abstract fn write(obj);

    abstract fn flush();

    abstract fn close();
}

abstract class InputStream {
    abstract fn read();

    abstract fn close();
}

/*
 * Abstract class of lined input stream.
 *
 * All classes extends this must implement <readline>
 */
abstract class LineInputStream extends InputStream {

    /*
     * Returns the next line.
     */
    abstract fn readline();
}

class NativeInputStream extends LineInputStream {

    var ns;

    fn NativeInputStream(stream) {
        ns = stream;
    }

    @Override
    fn readline() {
        return ns.readline();
    }

    @Override
    fn read() {
        return ns.read();
    }

    @Override
    fn close() {
        ns.close();
    }
}

class NativeOutputStream extends OutputStream {

    var ns;

    fn NativeOutputStream(stream) {
        ns = stream;
    }

    @Override
    fn write(obj) {
        ns.write(obj);
    }

    @Override
    fn flush() {
        ns.flush();
    }

    @Override
    fn close() {
        ns.close();
    }
}


class String {
    var lit;  // CharArray

    fn String(lit) {
        if lit instanceof String {
            this.lit = lit.lit;
        } else if lit instanceof CharArray {
            this.lit = lit;
        } else {
            this.lit = chars(lit);
        }
    }

    fn contains(pattern) {
        p_len := pattern.length();
        len := length();
        for i := 0; i < len - p_len; i++ {
            var j;
            for j = 0; j < p_len; j++ {
                if __getitem__(i + j) != pattern[j] {
                    break;
                }
            }
            if j == p_len {
                return true;
            }
        }
        return false;
    }

    fn format(*args) {
        arg_len := args.size();
        len := length();
        lst := [];
        i := 0;
        count := 0;
        while i < len {
            ch := this[i];
            if ch == "%" {
                j := i + 1;
                params := [];
                while !this[j].is_alpha() {
                    params.append(this[j]);
                    j++;
                }
                if count >= arg_len {
                    throw new IndexException("Not enough arguments for string format");
                }
                flag := this[j];
                if flag == "s" {
                    literal := args[count];
                    lst.append(literal)
                } else if flag == "d" {
                    lst.append(string(int(args[count])));
                } else if flag == "f" {
                    if params.size() > 0 {
                        precision := int(params[0]);
                        lst.append(string(round(args[count], precision)));
                    } else {
                        lst.append(string(args[count]));
                    }
                } else if flag == "r" {
                    literal := args[count];
                    lst.append(string(literal));
                } else {
                    lst.append("%");
                    i = j;
                    continue;
                }
                i = j + 1;
                count++;
                continue;
            }
            lst.append(ch);
            i++;
        }
        return "".join(lst);
    }

    fn is_alpha() {
        return lit.is_alpha();
    }

    fn is_number() {
        try {
            __float__();
            return true;
        } catch e : Exception {
            return false;
        }
    }

    fn join(iter) {
        lst := [];
        for var seg; iter {
            lst.append(seg.lit);
        }
        return new String(natives.str_join("".lit, lst.to_array()));
    }

    fn length() {
        return lit.length();
    }

    fn split(pattern) {
        lst := [];
        j := 0;
        len := length();
        for i := 0; i < len; i++ {
            if __getitem__(i) == pattern {
                seg := substring(j, i);
                lst.append(seg);
                j = i + 1;
            }
        }
        lst.append(substring(j, len));
        return lst;
    }

    fn substring(from, to=null) {
        if to == null {
            to = length();
        }
        return new String(lit.substring(from, to));
    }

    fn __add__(other) {
        if other instanceof String {
            return new String(lit + other.lit);
        } else {
            throw new ObjectTypeException("String adder must be String");
        }
    }

    fn __eq__(other) {
        return other instanceof String && lit == other.lit;
    }

    fn __float__() {
        return float(lit);
    }

    fn __getitem__(index) {
        return new String(lit[index]);
    }

    fn __hash__() {
        return lit.__hash__();
    }

    fn __neq__(other) {
        return !(this == other);
    }

    fn __str__() {
        return this;
    }

    fn __repr__() {
        return this;
    }
}


class List extends Iterable {

    var arr;
    var length = 0;

    fn List(*args) {
        arr = array(length=8);
        for var x; args {
            append(x);
        }
    }

    fn __getitem__(index) {
        return arr[index];
    }

    fn __setitem__(index, value) {
        arr[index] = value;
    }

    fn __iter__() {
        return to_array();
    }

    fn __str__() {
        return string(to_array());
    }

    fn __repr__() {
        return __str__();
    }

    fn __unpack__() {
        return to_array();
    }

    fn append(v) {
        if length >= arr.size() {
            double_size();
        }
        arr[length] = v;
        length++;
        return this;
    }

    fn insert(index, value) {
        if length >= arr.size() {
            double_size();
        }
        for var i = length + 1; i >= index; i-- {
            arr[i] = arr[i - 1];
        }
        arr[index] = value;
        length++;
    }

    fn pop(index=null) {
        if index === null {
            index = length - 1;
        }
        var val = arr[index];
        for var i = index; i < length; i++ {
            arr[i] = arr[i + 1];
        }
        length--;
        if length < arr.size() / 4 {
            half_size();
        }
        return val;
    }

    fn extend(iter) {
        for var x; iter {
            append(x);
        }
    }

    fn clear() {
        arr = array(length = 8);
    }

    fn copy() {
        return new List(*this);
    }

    fn size() {
        return length;
    }

    /*
     * Swaps the content at index <src> to the content at index <dest>.
     */
    fn swap(src, dest) {
        var temp = this[src];
        this[src] = this[dest];
        this[dest] = temp;
    }

    fn sublist(from, to=null) {
        if to === null {
            to = size();
        }
        lst := [];
        for i := from; i < to; i++ {
            lst.append(arr[i]);
        }
        return lst;
    }

    fn to_array() {
        var s_arr = array(length=length);
        for var i = 0; i < length; i++ {
            s_arr[i] = arr[i];
        }
        return s_arr;
    }

    fn double_size() {
        var big_arr = array(length = arr.size() * 2);
        for var i = 0; i < arr.size(); i++ {
            big_arr[i] = arr[i];
        }
        arr = big_arr;
    }

    fn half_size() {
        var sml_array = array(length = arr.size() / 2);
        for var i = 0; i < sml_arr.size(); i++ {
            sml_arr[i] = arr[i];
        }
        arr = sml_arr;
    }
}


/*
 * Returns a new <List> instance, with initial elements *args
 */
fn list(*args) {
    return new List(*args);
}

/*
 * Returns a new <String> instance, with literal `lit`
 */
fn string(lit) {
    return new String(lit);
}

/*
 * Returns the rounded number, with floor mode.
 */
fn round(num, precision=0) {
    if precision == 0 {
        return int(num);
    } else {
        n := 1;
        for i := 0; i < precision; i++ {
            n *= 10;
        }
        return float(int(num * n)) / n;
    }
}

/*
 * Returns the ftn(object) if the object <obj> is not null. Otherwise, return null.
 */
fn non_null_else(obj, alter, ftn=null) {
    if obj === null {
        return null;
    } else if ftn === null {
        return obj;
    } else {
        return ftn(obj);
    }
}

/*
 * Returns a <Iterator>, counts from
 */
fn range(n1, n2=null, step=1) {
    var iter;
    var stop;
    if n2 === null {
        iter = 0;
        stop = n1;
    } else {
        iter = n1;
        stop = n2;
    }
    var step_fn = x -> x + step;

    return new Iterator <- {
        @Override
        fn __more__() {
            return iter != stop;
        }

        @Override
        fn __next__() {
            var temp = iter;
            iter = step_fn(iter);
            return temp;
        }
    }
}

system.set_in(new NativeInputStream(system.native_in));
system.set_out(new NativeOutputStream(system.native_out));
system.set_err(new NativeOutputStream(system.native_err));
