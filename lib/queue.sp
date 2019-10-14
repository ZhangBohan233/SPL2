import namespace "stack"


/*
 * A queue data structure, follows the rule "first in first out".
 */
abstract class Queue {

    abstract function Queue();

    /*
     * Returns the number of element in this queue.
     */
    abstract function size();

    /*
     * Adds an element to the last.
     */
    abstract function add_last(element);

    abstract function remove_last();

    /*
     * Returns first-added element.
     */
    abstract function get_first();

    abstract function remove_first();
}


class Deque extends Queue, Stack {

    abstract function Deque();

    abstract function add_first(element);

    @Override
    abstract function remove_first();

    abstract function get_last();

    @Override
    abstract function remove_last();
}


class LLNode {
    var before = null;
    var after = null;
    var value = null;
}


class LinkedListIterator extends Iterator {
    var iter;

    function LinkedListIterator(head) {
        iter = head;
    }

    @Override
    function __more__() {
        return iter !== null;
    }

    @Override
    function __next__() {
        var temp = iter;
        iter = iter.after;
        return temp.value;
    }
}


class LinkedList extends Deque, Iterable {

    var size_ = 0;
    var head = null;
    var tail = null;

    function LinkedList() {
    }

    @Override
    function __iter__() {
        return new LinkedListIterator(head);
    }

    function __str__() {
        var s = "Link[";
        for (var cur = head; cur; cur = cur.after) {
            s += string(cur.value) + "->";
        }
        s += "]";
        return s;
    }

    @Override
    function size() {
        return size_;
    }

    @Override
    function add_last(element) {
        if (size_ == 0) {
            create(element);
        } else {
            var n = new LLNode;
            n.value = element;
            n.before = tail;
            tail.after = n;
            tail = n;
            size_ += 1;
        }
        return element;
    }

    @Override
    function add_first(element) {
        if (size_ == 0) {
            create(element);
        } else {
            var n = new LLNode;
            n.value = element;
            n.after = head;
            head.before = n;
            head = n;
            size_ += 1;
        }
        return element;
    }

    @Override
    function last() {
        return tail.value;
    }

    @Override
    function first() {
        return head.value;
    }

    @Override
    function remove_first() {
        var n = head;
        head = head.after;
        if (head !== null) {
            head.before = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    function remove_last() {
        var n = tail;
        tail = head.before;
        if (tail) {
            tail.after = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    function top() {
        return last();
    }

    @Override
    function pop() {
        return remove_last();
    }

    @Override
    function push(element) {
        return add_last(element)
    }

    function create(ele) {
        var n = new LLNode;
        n.value = ele;
        head = n;
        tail = n;
        size_ = 1;
    }

    function removable() {
        return size_ > 0;
    }
}
