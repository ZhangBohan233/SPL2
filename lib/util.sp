import "sgl"

class MemoryViewer {

    var base_env;
    var window;
    var tree;
    var id_set = set();

    function MemoryViewer(env) {
        base_env = env;
        window = new sgl.Window();
        tree = new sgl.TreeView(window);
        tree.set_height(30);
        tree.columns(4);
        tree.column_width(2, 400);
        tree.column_heading(0, "Name");
        tree.column_heading(1, "Type");
        tree.column_heading(2, "Content");
        tree.column_heading(3, "Note");
        window.set_root(tree);
    }

    function browse(name, obj, parent) {
        if (obj instanceof Object) {
            var obj_id = id(obj);
            if (id_set.contains(obj_id)) {
                append(name, obj, parent, "duplicate");
                return;
            } else {
                id_set.add(obj_id);
            }
        }
        var child = append(name, obj, parent);
        if (obj instanceof EnvWrapper) {
            for (var attr; obj.attributes()) {
                browse(attr, obj.get(attr), child);
            }
        } else if (obj instanceof Object || obj instanceof Module) {
            var sub_env = get_env(obj);
            for (var attr; sub_env.attributes()) {
                if (attr != "this") {
                    browse(attr, sub_env.get(attr), child);
                }
            }
        }
    }

    function append(name, obj, parent, note="") {
        return tree.add_item(name, ~[type(obj), string(obj), note], parent)
    }

    function show() {
        browse("root", base_env, "");
        window.show();
    }
}

/*
 * A type of dynamic building strings.
 */
class StringBuilder {

    var lst;
    var len = 0;

    function StringBuilder() {
        lst = [];
    }

    function append(s) {
        var v = string(s);
        len += v.length();
        lst.append(v);
        return this;
    }

    function to_string() {
        return natives.str_join("", lst.to_array());
    }

    function length() {
        return len;
    }

    function substring(from, to=null) {
        return to_string().substring(from, to);
    }

    function __str__() {
        return to_string();
    }
}

function memory_view(env) {
    var mv = new MemoryViewer(env);
    mv.show();
}
