import namespace "stack"


/*
 * A queue data structure, follows the rule "first in first out".
 */
abstract class Queue {

    abstract fn Queue();

    /*
     * Returns the number of element in this queue.
     */
    abstract fn size();

    /*
     * Adds an element to the last.
     */
    abstract fn add_last(element);

    abstract fn remove_last();

    /*
     * Returns first-added element.
     */
    abstract fn get_first();

    abstract fn remove_first();
}


class Deque extends Queue, Stack {

    abstract fn Deque();

    abstract fn add_first(element);

    @Override
    abstract fn remove_first();

    abstract fn get_last();

    @Override
    abstract fn remove_last();
}


class LLNode {
    var before = null;
    var after = null;
    var value = null;
}


class LinkedListIterator extends Iterator {
    var iter;

    fn LinkedListIterator(head) {
        iter = head;
    }

    @Override
    fn __more__() {
        return iter !== null;
    }

    @Override
    fn __next__() {
        var temp = iter;
        iter = iter.after;
        return temp.value;
    }
}


class LinkedList extends Deque, Iterable {

    var size_ = 0;
    var head = null;
    var tail = null;

    fn LinkedList() {
    }

    fn __free__() {
        node := head;
        while node !== null {
            next := node.after;
            free(node.value);
            free(node);
            node = next;
        }
    }

    @Override
    fn __iter__() {
        return malloc(new LinkedListIterator(head));
    }

    fn __str__() {
        var s = malloc("Link[");
        for var cur = head; cur; cur = cur.after {
            ch := chars(cur.value);
            s += ch + "->";
            free(ch);
        }
        s += "]";
        return s;
    }

    @Override
    fn size() {
        return size_;
    }

    @Override
    fn add_last(element) {
        if size_ == 0 {
            create(element);
        } else {
            var n = malloc(new LLNode);
            n.value = element;
            n.before = tail;
            tail.after = n;
            tail = n;
            size_ += 1;
        }
        return element;
    }

    @Override
    fn add_first(element) {
        if size_ == 0 {
            create(element);
        } else {
            var n = malloc(new LLNode);
            n.value = element;
            n.after = head;
            head.before = n;
            head = n;
            size_ += 1;
        }
        return element;
    }

    @Override
    fn last() {
        return tail.value;
    }

    @Override
    fn first() {
        return head.value;
    }

    @Override
    fn remove_first() {
        var n = head;
        head = head.after;
        if head !== null {
            head.before = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    fn remove_last() {
        var n = tail;
        tail = head.before;
        if tail {
            tail.after = null;
        }
        size_ -= 1;
        return n.value;
    }

    @Override
    fn top() {
        return last();
    }

    @Override
    fn pop() {
        return remove_last();
    }

    @Override
    fn push(element) {
        return add_last(element)
    }

    fn create(ele) {
        var n = malloc(new LLNode);
        n.value = ele;
        head = n;
        tail = n;
        size_ = 1;
    }

    fn removable() {
        return size_ > 0;
    }
}
