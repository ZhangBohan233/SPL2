/*
 * An input stream that reads text file.
 */
class TextInputStream extends InputStream {

    var fp = null;

    fn TextInputStream(file_name) {
        fp = f_open(file_name, "r");
        if fp == -1 {
            throw new FileNotFoundException(file_name + " not found");
        }
    }

    @Override
    fn read() {
        return non_null_else(fp.read(), null, string);
    }

    fn readline() {
        return non_null_else(fp.readline(), null, string);
    }

    @Override
    fn close() {
        return fp.close();
    }
}


/*
 * An input stream that reads binary file.
 */
class FileInputStream extends InputStream {

    var fp = null;

    fn FileInputStream(file_name) {
        fp = f_open(file_name, "rb");
        if fp == -1 {
            throw new FileNotFoundException(file_name + " not found");
        }
    }

    @Override
    fn read() {
        return fp.read();
    }

    fn read_one() {
        return fp.read_one();
    }

    @Override
    fn close() {
        return fp.close();
    }
}


/*
 * An output stream that writes text file.
 */
class TextOutputStream extends OutputStream {

    var fp = null;

    fn TextOutputStream(file_name) {
        fp = f_open(file_name, "w");
        if fp == -1 {
            throw new FileNotFoundException(file_name + " not found");
        }
    }

    @Override
    fn write(s) {
        return fp.write(s);
    }

    @Override
    fn flush() {
        return fp.flush();
    }

    @Override
    fn close() {
        return fp.close();
    }
}


/*
 * An output stream that writes binary file.
 */
class FileOutputStream extends OutputStream {

    var fp = null;

    fn FileOutputStream(file_name) {
        fp = f_open(file_name, "wb");
        if fp == -1 {
            throw new FileNotFoundException(file_name + " not found");
        }
    }

    @Override
    fn write(s) {
        return fp.write(s);
    }

    @Override
    fn flush() {
        return fp.flush();
    }

    @Override
    fn close() {
        return fp.close();
    }
}


class IOException extends Exception {
    fn IOException(msg="") {
        Exception(msg);
    }
}


class FileNotFoundException extends IOException {
    fn FileNotFoundException(msg="") {
        IOException(msg);
    }
}
