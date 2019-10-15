/*
 * A stack data structure, follows the rule "last in first out".
 */
abstract class Stack {

    @Suppress
    abstract fn size();

    abstract fn top();

    abstract fn push(element);

    abstract fn pop();
}
