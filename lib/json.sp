import "io"
import "util"

class NotAJSONObjectException extends Exception {
    function NotAJSONObjectException(msg="") {
        Exception(msg);
    }
}

function to_json(obj) {
    if (obj instanceof Pair) {
        var sb = new util.StringBuilder();
        sb.append('{');
        var i = 0;
        var len = obj.size();
        for (var k; obj) {
            sb.append('"')
                    .append(k)
                    .append('":')
                    .append(to_json(obj[k]));
            if (i < len - 1) {
                sb.append(',');
            }
            i++;
        }
        sb.append('}');
        return sb.to_string();
    } else if (obj instanceof List) {
        var sb = new util.StringBuilder();
        sb.append('[');
        var len = obj.size();
        for (var i = 0; i < len; i++) {
            sb.append(to_json(obj[i]));
            if (i < len - 1) {
                sb.append(',');
            }
        }
        sb.append(']');
        return sb.to_string();
    } else {
        return '"' + string(obj) + '"';
    }
}

function read_file(name) {
    var stream = new io.TextInputStream(name);
    var text = stream.read();
    stream.close();
    return from_string(text);
}

function write_file(json_obj, file_name) {
    var stream = new io.TextOutputStream(file_name);
    var text;
    if (json_obj instanceof Pair) {
        text = to_json(json_obj);
    } else {
        throw new NotAJSONObjectException("Type '%r' is not a JSON object".format(type(json_obj)));
    }
    stream.write(text);
    stream.close();
}

function from_string(content) {
    var p = eval(content);
    return p;
}
