
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

    function Node(node) {
        this.node = node;
    }

    function update() {
        node.call("update");
    }

    function set_width(width) {
        node.configure("width", width);
    }

    function set_height(height) {
        node.configure("height", height);
    }

    function background(color) {
        node.set_bg(color);
    }

    function foreground(color) {
        node.configure("foreground", color);
    }
}

class Window extends Node {

    function Window() {
        node = new Graphic("Tk")
    }

    function set_root(root) {
        root.node.call("grid", sticky=ALIGN_EXPAND);
    }

    function set_menu(menu) {
        node.configure("menu", menu.node.tk);
    }

    function show() {
        node.call("mainloop");
    }
}

abstract class Container extends Node {

    var children = [];
    var alignment = ALIGN_WIDTH;

    function Container(node) {
        Node(node);
    }

    function align(value) {
        alignment = value;
    }
}

class VBox extends Container {

    function VBox(parent) {
        Container(new Graphic("Frame", parent.node));
    }

    function add(n) {
        n.node.call("grid", row=children.size(), column=0, sticky=alignment);
        children.append(n);
    }
}


class HBox extends Container {

    function HBox(parent) {
        Container(new Graphic("Frame", parent.node));
    }

    function add(n) {
        n.node.call("grid", row=0, column=children.size(), sticky=alignment);
        children.append(n);
    }
}


abstract class LabelAble extends Node {
    function set_text(text) {
        node.configure("text", text);
    }

    function get_text() {
        return node.get("text");
    }
}


class Label extends LabelAble {

    function Label(parent, text="") {
        Node(new Graphic("Label", parent.node));
        set_text(text);
    }
}


class TextField extends Node {

    function TextField(parent) {
        Node(new Graphic("Entry", parent.node));
    }

    function get() {

    }
}


class TextArea extends Node {

    function TextArea(parent) {
        Node(new Graphic("Text", parent.node));
    }

    function append_text(text, tag="") {
        node.call("insert", "end", text, tag);
        node.call("see", "end");
        update();
    }

    function tag(tag_name, **kwargs) {
        node.call("tag_configure", tag_name, **kwargs);
    }

    function clear() {
        node.call("delete", "1.0", "end");
    }

    function get_text() {
        return node.call("get", "1.0", "end");
    }
}


class Button extends LabelAble {

    function Button(parent, text="") {
        Node(new Graphic("Button", parent.node));
        set_text(text);
    }

    function callback(command, ftn) {
        node.callback(command, ftn);
    }
}


class MenuBar extends Node {

    function MenuBar(parent) {
        Node(new Graphic("Menu", parent.node));
    }

    function add_menu(menu, name) {
        node.call("add_cascade", label=name, menu=menu.node.tk);
    }
}


class Menu extends Node {

    function Menu(parent) {
        Node(new Graphic("Menu", parent.node));
        node.configure("tearoff", 0);
    }

    function add_item(name, ftn) {
        node.call("add_command", label=name, command=ftn);
    }

    function add_separator() {
        node.call("add_separator");
    }
}


class TreeView extends Node {

    function TreeView(parent) {
        Node(new Graphic("ttk.Treeview", parent.node));
    }

    function columns(num_cols) {
        var cols = [];
        for (var i = 1; i < num_cols; i++) {
            cols.append("#" + string(i));
        }
        node.configure("columns", cols);
    }

    function column_heading(index, name) {
        var index_name = "#" + string(index);
        node.call("heading", index_name, text=name);
    }

    function add_item(text, values, n) {
        return node.call("insert", n, "end", text=text, values=values);
    }

    function column_width(index, width, min_width=0) {
        var index_name = "#" + string(index);
        node.call("column", index_name, width=width, minwidth=min_width);
    }
}


function ask_file_dialog(types={}) {
    return (new Graphic("Button", null)).file_dialog(types);
}
