
const ALIGN_LEFT = "w";
const ALIGN_RIGHT = "e";
const ALIGN_TOP = "n";
const ALIGN_BOTTOM = "s";
const ALIGN_WIDTH = "ew";
const ALIGN_CENTER = "";
const ALIGN_EXPAND = "news";

/*
 *
 */
abstract class Node {

    var node;  // Graphic

    fn Node(node) {
        this.node = node;
    }

    fn update() {
        node.call("update");
    }

    fn set_width(width) {
        node.configure("width", width);
    }

    fn set_height(height) {
        node.configure("height", height);
    }

    fn background(color) {
        node.set_bg(color);
    }

    fn foreground(color) {
        node.configure("foreground", color);
    }
}

class Window extends Node {

    fn Window() {
        node = new Graphic("Tk")
    }

    fn set_root(root) {
        root.node.call("grid", sticky=ALIGN_EXPAND);
    }

    fn set_menu(menu) {
        node.configure("menu", menu.node.tk);
    }

    fn show() {
        node.call("mainloop");
    }
}

abstract class Container extends Node {

    var children = [];
    var alignment = ALIGN_WIDTH;

    fn Container(node) {
        Node(node);
    }

    fn align(value) {
        alignment = value;
    }
}

class VBox extends Container {

    fn VBox(parent) {
        Container(new Graphic("Frame", parent.node));
    }

    fn add(n) {
        n.node.call("grid", row=children.size(), column=0, sticky=alignment);
        children.append(n);
    }
}


class HBox extends Container {

    fn HBox(parent) {
        Container(new Graphic("Frame", parent.node));
    }

    fn add(n) {
        n.node.call("grid", row=0, column=children.size(), sticky=alignment);
        children.append(n);
    }
}


abstract class LabelAble extends Node {
    fn set_text(text) {
        node.configure("text", text);
    }

    fn get_text() {
        return node.get("text");
    }
}


class Label extends LabelAble {

    fn Label(parent, text="") {
        Node(new Graphic("Label", parent.node));
        set_text(text);
    }
}


class TextField extends Node {

    fn TextField(parent) {
        Node(new Graphic("Entry", parent.node));
    }

    fn get() {

    }
}


class TextArea extends Node {

    fn TextArea(parent) {
        Node(new Graphic("Text", parent.node));
    }

    fn append_text(text, tag="") {
        node.call("insert", "end", text, tag);
        node.call("see", "end");
        update();
    }

    fn tag(tag_name, **kwargs) {
        node.call("tag_configure", tag_name, **kwargs);
    }

    fn clear() {
        node.call("delete", "1.0", "end");
    }

    fn get_text() {
        return node.call("get", "1.0", "end");
    }
}


class Button extends LabelAble {

    fn Button(parent, text="") {
        Node(new Graphic("Button", parent.node));
        set_text(text);
    }

    fn callback(command, ftn) {
        node.callback(command, ftn);
    }
}


class MenuBar extends Node {

    fn MenuBar(parent) {
        Node(new Graphic("Menu", parent.node));
    }

    fn add_menu(menu, name) {
        node.call("add_cascade", label=name, menu=menu.node.tk);
    }
}


class Menu extends Node {

    fn Menu(parent) {
        Node(new Graphic("Menu", parent.node));
        node.configure("tearoff", 0);
    }

    fn add_item(name, ftn) {
        node.call("add_command", label=name, command=ftn);
    }

    fn add_separator() {
        node.call("add_separator");
    }
}


class TreeView extends Node {

    fn TreeView(parent) {
        Node(new Graphic("ttk.Treeview", parent.node));
    }

    fn columns(num_cols) {
        var cols = [];
        for var i = 1; i < num_cols; i++ {
            cols.append("#" + string(i));
        }
        node.configure("columns", cols);
    }

    fn column_heading(index, name) {
        var index_name = "#" + string(index);
        node.call("heading", index_name, text=name);
    }

    fn add_item(text, values, n) {
        return node.call("insert", n, "end", text=text, values=values);
    }

    fn column_width(index, width, min_width=0) {
        var index_name = "#" + string(index);
        node.call("column", index_name, width=width, minwidth=min_width);
    }
}


fn ask_file_dialog(types={}) {
    return (new Graphic("Button", null)).file_dialog(types);
}
