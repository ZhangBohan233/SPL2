from bin import spl_token_lib as stl

PRECEDENCE = {"+": 50, "-": 50, "*": 100, "/": 100, "%": 100,
              "==": 20, ">": 25, "<": 25, ">=": 25, "<=": 25,
              "!=": 20, "&&": 5, "and": 5, "||": 5, "or": 5, "&": 12, "^": 11, "|": 10,
              "<<": 40, ">>": 40, "unpack": 200, "kw_unpack": 200, "new": 150,
              ".": 500, "!": 200, "neg": 200, "return": 1, "throw": 1, "namespace": 150,
              "=": 2, "+=": 2, "-=": 2, "*=": 2, "/=": 2, "%=": 2,
              "&=": 2, "^=": 2, "|=": 2, "<<=": 2, ">>=": 2, "=>": 500,
              "===": 20, "is": 20, "!==": 20, "instanceof": 25, "subclassof": 25, "assert": 1,
              "?": 3, "++": 300, "--": 300, ":": 2}

MULTIPLIER = 1000

# Nodes
LITERAL_NODE = 3
NAME_NODE = 4
BREAK_STMT = 7
CONTINUE_STMT = 8
ASSIGNMENT_NODE = 9
DOT = 10
BINARY_OPERATOR = 12
UNARY_OPERATOR = 14
TERNARY_OPERATOR = 15
BLOCK_STMT = 16
IF_STMT = 17
WHILE_STMT = 18
FOR_LOOP_STMT = 19
DEF_STMT = 20
FUNCTION_CALL = 21
CLASS_STMT = 22
# CLASS_INIT = 23
ABSTRACT = 25
TRY_STMT = 27
CATCH_STMT = 28
# TYPE_NODE = 29
# JUMP_NODE = 30
UNDEFINED_NODE = 31
IN_DECREMENT_OPERATOR = 32
INDEXING_NODE = 33
IMPORT_NODE = 34
ANNOTATION_NODE = 35

# Variable levels
ASSIGN = 0
CONST = 1
VAR = 2
FUNC_DEFINE = 3


class SpaceCounter:
    def __init__(self):
        self.count = 0

    def add_space(self):
        self.count += 2

    def remove_space(self):
        self.count -= 2

    def get(self):
        return self.count


SPACES = SpaceCounter()


class Node:
    line_num = 0
    file = None
    node_type = 0
    execution = 0

    def __init__(self, line: tuple):
        self.line_num = line[0]
        self.file = line[1]
        self.node_type = 0
        self.execution = 0


class LeafNode(Node):
    def __init__(self, line):
        Node.__init__(self, line)


class Expr(Node):
    def __init__(self, line):
        Node.__init__(self, line)


class BlockStmt(Node):
    lines: list = None
    standalone = False

    def __init__(self, line):
        Node.__init__(self, line)

        self.node_type = BLOCK_STMT
        self.lines = []

    def add_line(self, node):
        self.lines.append(node)

    def __str__(self):
        s = "\n" + " " * SPACES.get() + "{"
        SPACES.add_space()
        for line in self.lines:
            s += "\n" + " " * SPACES.get() + str(line)
        SPACES.remove_space()
        s += "\n" + " " * SPACES.get() + "}"
        return s

    def __repr__(self):
        return "BlockStmt"


class BinaryExpr(Expr):
    """
    :type operation: str
    :type left:
    """
    left = None
    right = None
    operation = None

    def __init__(self, line, operator):
        Expr.__init__(self, line)

        self.operation = operator

    def precedence(self):
        return PRECEDENCE[self.operation]

    def __str__(self):
        return "BE({} {} {})".format(self.left, self.operation, self.right)

    def __repr__(self):
        return "BE'{}'".format(self.operation)


class LiteralNode(LeafNode):
    """
    :type literal: str
    """
    literal = None

    def __init__(self, line, lit):
        LeafNode.__init__(self, line)

        self.node_type = LITERAL_NODE
        self.literal = lit

    def __str__(self):
        return '"' + self.literal + '"'

    def __repr__(self):
        return self.__str__()


class TitleNode(Node):
    titles: list

    def __init__(self, line):
        Node.__init__(self, line)


class TernaryOperator(Expr):
    first_op: str
    second_op: str = None
    left: Node = None
    mid: Node = None
    right: Node = None

    def __init__(self, line, first_op):
        Expr.__init__(self, line)

        self.node_type = TERNARY_OPERATOR
        self.first_op = first_op

    def precedence(self):
        return PRECEDENCE[self.first_op]

    def __str__(self):
        return "TE({} {} {} {} {})".format(self.left, self.first_op, self.mid, self.second_op, self.right)

    def __repr__(self):
        return "TE'{} {}'".format(self.first_op, self.second_op)


class BinaryOperator(BinaryExpr):
    assignment = False

    def __init__(self, line, op):
        BinaryExpr.__init__(self, line, op)

        self.node_type = BINARY_OPERATOR


class UnaryOperator(Expr):
    value = None
    operation = None

    def __init__(self, line, op):
        Expr.__init__(self, line)

        self.node_type = UNARY_OPERATOR
        self.operation = op

    def precedence(self):
        return PRECEDENCE[self.operation]

    def __str__(self):
        return "UE({} {})".format(self.operation, self.value)

    def __repr__(self):
        return "UE'{}'".format(self.operation)


class NameNode(LeafNode):
    name: str = None

    def __init__(self, line, n):
        LeafNode.__init__(self, line)

        self.node_type = NAME_NODE
        self.name = n

    def __str__(self):
        return "N(" + self.name + ")"

    def __repr__(self):
        return self.name


class AssignmentNode(BinaryExpr):
    level = ASSIGN

    def __init__(self, line, level):
        BinaryExpr.__init__(self, line, "=")

        self.node_type = ASSIGNMENT_NODE
        self.level = level


class InDecrementOperator(Expr):
    operation: str
    is_post: bool = True  # if is_post: i++
    value = None

    def __init__(self, lf, operation):
        Expr.__init__(self, lf)

        self.operation = operation
        self.node_type = IN_DECREMENT_OPERATOR

    def precedence(self):
        return PRECEDENCE[self.operation]

    def __str__(self):
        if self.is_post:
            return str(self.value) + self.operation
        else:
            return self.operation + str(self.value)

    def __repr__(self):
        if self.is_post:
            return "post" + self.operation
        else:
            return self.operation + "pre"


class AnnotationNode(Node):
    name: str
    args: BlockStmt = None
    body: BlockStmt = None

    def __init__(self, line, name):
        Node.__init__(self, line)
        self.name = name

        self.node_type = ANNOTATION_NODE

    def __str__(self):
        return "@" + self.name + ("" if self.body is None else str(self.body))

    def __repr__(self):
        return "@" + self.name


class BreakStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = BREAK_STMT

    def __str__(self):
        return "break"

    def __repr__(self):
        return self.__str__()


class ContinueStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = CONTINUE_STMT

    def __str__(self):
        return "continue"

    def __repr__(self):
        return self.__str__()


class CondStmt(Node):
    condition = None

    def __init__(self, line):
        Node.__init__(self, line)


class IfStmt(CondStmt):
    then_block = None
    else_block = None
    has_else = False

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = IF_STMT

    def __str__(self):
        return "if({} then {} else[{}] {})".format(self.condition, self.then_block, self.has_else, self.else_block)

    def __repr__(self):
        return "If-else Stmt"


class WhileStmt(CondStmt):
    body = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = WHILE_STMT

    def __str__(self):
        return "while({} do {})".format(self.condition, self.body)

    def __repr__(self):
        return "WhileStmt"


class ForLoopStmt(CondStmt):
    body = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = FOR_LOOP_STMT

    def __str__(self):
        return "for ({}) do {}".format(self.condition, self.body)

    def __repr__(self):
        return "ForLoopStmt"


class DefStmt(TitleNode):
    params: BlockStmt = None
    body = None
    abstract: bool = False
    annotations: list
    doc: str

    def __init__(self, line, abstract: bool, func_doc: str):
        TitleNode.__init__(self, line)

        self.node_type = DEF_STMT
        self.params = None
        self.abstract = abstract
        self.doc = func_doc
        self.annotations = []

    def __str__(self):
        return "func(({}) -> {})".format(self.params, self.body)

    def __repr__(self):
        return ("abstract " if self.abstract else "") + "function"


class FuncCall(Node):
    call_obj = None
    args: BlockStmt = None

    def __init__(self, line, call_obj):
        Node.__init__(self, line)

        self.node_type = FUNCTION_CALL
        self.call_obj = call_obj

    def __str__(self):
        return "call:[{}({})]".format(self.call_obj, self.args)

    def __repr__(self):
        return "Call"

    def fulfilled(self):
        return self.args is not None


class IndexingNode(Node):
    call_obj = None
    arg: BlockStmt = None

    def __init__(self, line, call_obj):
        Node.__init__(self, line)

        self.node_type = INDEXING_NODE
        self.call_obj = call_obj

    def __str__(self):
        return "{}[{}]".format(self.call_obj, self.arg)

    def __repr__(self):
        return "indexing"

    def fulfilled(self):
        return self.arg is not None


class ImportNode(Node):
    import_name: str
    path: str
    block: BlockStmt = None

    def __init__(self, line, name, path):
        Node.__init__(self, line)

        self.import_name = name
        self.path = path
        self.node_type = IMPORT_NODE

    def __str__(self):
        return "import {}: {}".format(self.import_name, self.block)

    def __repr__(self):
        return "import {}".format(self.import_name)


class ClassStmt(Node):
    class_name: str = None
    superclass_nodes: list
    block: BlockStmt = None
    abstract: bool = False
    doc: str

    def __init__(self, line: tuple, name: str, abstract: bool, class_doc: str):
        Node.__init__(self, line)

        self.node_type = CLASS_STMT
        self.class_name = name
        self.abstract = abstract
        self.doc = class_doc
        self.superclass_nodes = [NameNode(line, "Object")]

    def __str__(self):
        return "Class {}: {}".format(self.class_name, self.block)

    def __repr__(self):
        return ("abstract " if self.abstract else "") + "class " + self.class_name


class Dot(BinaryOperator):
    def __init__(self, line):
        BinaryOperator.__init__(self, line, ".")

        self.node_type = DOT

    def __str__(self):
        return "({} dot {})".format(self.left, self.right)

    def __repr__(self):
        return "."


class CatchStmt(CondStmt):
    then: BlockStmt = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = CATCH_STMT

    def __str__(self):
        return "catch ({}) {}".format(self.condition, self.then)

    def __repr__(self):
        return "CatchStmt"


class TryStmt(Node):
    try_block: BlockStmt = None
    catch_blocks = None
    finally_block: BlockStmt = None

    def __init__(self, line):
        Node.__init__(self, line)

        self.node_type = TRY_STMT
        self.catch_blocks: [CatchStmt] = []

    def __str__(self):
        return "try {} {} finally {}" \
            .format(self.try_block, self.catch_blocks, self.finally_block)

    def __repr__(self):
        return "TryStmt"


class JumpNode(Node):
    to = None
    args = None

    def __init__(self, line, to):
        Node.__init__(self, line)

        self.node_type = JUMP_NODE
        self.to = to
        self.args = []

    def __str__(self):
        return "Jump({}: {})".format(self.to, self.args)

    def __repr__(self):
        return self.__str__()


class UndefinedNode(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = UNDEFINED_NODE

    def __str__(self):
        return "undefined"

    def __repr__(self):
        return self.__str__()


class AbstractSyntaxTree:
    """
    :type inner: AbstractSyntaxTree
    """

    def __init__(self):
        self.elements: BlockStmt = BlockStmt((0, "parser"))
        self.stack = []
        self.inner = None
        self.in_expr = False
        self.in_ternary = False

    def __str__(self):
        return str(self.elements)

    def invalidate_inner(self):
        self.inner = None

    def last_is_name(self):
        if self.inner:
            return self.inner.last_is_name()
        else:
            if len(self.stack) > 0:
                if isinstance(self.stack[-1], NameNode):
                    return True
            return False

    def get_active(self):
        if self.inner:
            return self.inner.get_active()
        else:
            return self

    def get_block_and_remove(self) -> BlockStmt:
        if self.inner:
            return self.inner.get_block_and_remove()
        else:
            block = self.stack.pop()
            return block

    def is_in_ternary(self):
        if self.inner:
            return self.inner.is_in_ternary()
        else:
            return self.in_ternary

    def add_name(self, line, n):
        if self.inner:
            self.inner.add_name(line, n)
        else:
            node = NameNode(line, n)
            self.stack.append(node)

    def add_number(self, line, v):
        if self.inner:
            self.inner.add_number(line, v)
        else:
            num = get_number(line, v)
            self.stack.append(num)

    def add_literal(self, line, lit):
        if self.inner:
            self.inner.add_literal(line, lit)
        else:
            node = LiteralNode(line, lit)
            self.stack.append(node)

    def add_operator(self, line, op, assignment=False):
        if self.inner:
            self.inner.add_operator(line, op, assignment)
        else:
            self.in_expr = True
            op_node = BinaryOperator(line, op)
            op_node.assignment = assignment
            self.stack.append(op_node)

    def add_unary(self, line, op):
        if self.inner:
            self.inner.add_unary(line, op)
        else:
            self.in_expr = True
            node = UnaryOperator(line, op)
            self.stack.append(node)

    def add_assignment(self, line, var_level: int):
        if self.inner:
            self.inner.add_assignment(line, var_level)
        else:
            self.in_expr = True
            ass_node = AssignmentNode(line, var_level)
            self.stack.append(ass_node)

    def add_ternary(self, line, op1):
        if self.inner:
            self.inner.add_ternary(line, op1)
        else:
            self.in_expr = True
            self.in_ternary = True
            node = TernaryOperator(line, op1)
            self.stack.append(node)

    def finish_ternary(self, line, op2):
        if self.inner:
            self.inner.finish_ternary(line, op2)
        else:
            self.in_ternary = False
            node: TernaryOperator = self.stack[-2]
            node.second_op = op2

    def add_increment_decrement(self, line, op):
        if self.inner:
            self.inner.add_increment_decrement(line, op)
        else:
            self.in_expr = True
            node = InDecrementOperator(line, op)
            self.stack.append(node)

    def add_undefined(self, line):
        if self.inner:
            self.inner.add_undefined(line)
        else:
            node = UndefinedNode(line)
            self.stack.append(node)

    def add_import(self, line, import_name, path):
        if self.inner:
            self.inner.add_import(line, import_name, path)
        else:
            node = ImportNode(line, import_name, path)
            self.stack.append(node)

    def add_if(self, line):
        if self.inner:
            self.inner.add_if(line)
        else:
            ifs = IfStmt(line)
            self.stack.append(ifs)
            self.inner = AbstractSyntaxTree()

    def add_else(self):
        if self.inner:
            self.inner.add_else()
        else:
            if_stmt = self.elements.lines[-1]
            find_else(if_stmt)

    def add_while(self, line):
        if self.inner:
            self.inner.add_while(line)
        else:
            whs = WhileStmt(line)
            self.stack.append(whs)
            self.inner = AbstractSyntaxTree()

    def add_for_loop(self, line):
        if self.inner:
            self.inner.add_for_loop(line)
        else:
            fls = ForLoopStmt(line)
            self.stack.append(fls)
            self.inner = AbstractSyntaxTree()

    def add_try(self, line):
        if self.inner:
            self.inner.add_try(line)
        else:
            tb = TryStmt(line)
            self.stack.append(tb)

    def add_catch(self, line):
        if self.inner:
            self.inner.add_catch(line)
        else:
            cat = CatchStmt(line)
            self.stack.append(cat)
            self.inner = AbstractSyntaxTree()

    def add_finally(self, line):
        if self.inner:
            self.inner.add_finally(line)
        else:
            pass

    def add_function(self, line, abstract: bool, func_doc: str):
        if self.inner:
            self.inner.add_function(line, abstract, func_doc)
        else:
            func = DefStmt(line, abstract, func_doc)
            self.stack.append(func)
            self.inner = AbstractSyntaxTree()

    def build_func_params(self):
        if self.inner.inner:
            self.inner.build_func_params()
        else:
            self.inner.build_line()
            block = self.inner.get_as_block()
            self.invalidate_inner()
            function = self.stack.pop()
            function.params = block
            self.stack.append(function)

    def add_call(self, line):
        # print(f_name)
        if self.inner:
            self.inner.add_call(line)
        else:
            obj = self.stack.pop()
            if isinstance(obj, AnnotationNode):
                self.stack.append(obj)
                self.inner = AbstractSyntaxTree()
            else:
                fc = FuncCall(line, obj)
                self.stack.append(fc)
                self.inner = AbstractSyntaxTree()

    def add_getitem(self, line):
        if self.inner:
            self.inner.add_getitem(line)
        else:
            node = IndexingNode(line, self.stack.pop())
            self.stack.append(node)
            self.inner = AbstractSyntaxTree()

    def build_getitem(self):
        if self.inner.inner:
            self.inner.build_getitem()
        else:
            self.inner.build_line()
            block: BlockStmt = self.inner.get_as_block()
            self.invalidate_inner()
            node: IndexingNode = self.stack.pop()
            node.arg = block
            self.stack.append(node)

    def add_break(self, line):
        if self.inner:
            self.inner.add_break(line)
        else:
            node = BreakStmt(line)
            self.stack.append(node)

    def add_continue(self, line):
        if self.inner:
            self.inner.add_continue(line)
        else:
            node = ContinueStmt(line)
            self.stack.append(node)

    def add_bool(self, line, v: str):
        if self.inner:
            self.inner.add_bool(line, v)
        else:
            if v == "true":
                node = True
            elif v == "false":
                node = False
            else:
                raise stl.ParseException("Unknown boolean value.")
            self.stack.append(node)

    def add_null(self, line):
        if self.inner:
            self.inner.add_null(line)
        else:
            self.stack.append(None)

    def add_annotation(self, line, name):
        if self.inner:
            self.inner.add_annotation(line, name)
        else:
            node = AnnotationNode(line, name)
            self.stack.append(node)

    def build_call(self):
        if self.inner.inner:
            self.inner.build_call()
        else:
            self.inner.build_line()
            block: BlockStmt = self.inner.get_as_block()
            self.invalidate_inner()
            call = self.stack.pop()
            if isinstance(call, AnnotationNode):
                call.args = block
            else:
                call: FuncCall
                call.args = block
            self.stack.append(call)

    def build_condition(self):
        if self.inner.inner:
            self.inner.build_condition()
        else:
            self.inner.build_line()
            expr = self.inner.get_as_block()
            # print(expr)
            self.invalidate_inner()
            cond_stmt: CondStmt = self.stack.pop()
            cond_stmt.condition = expr
            # print(cond_stmt)
            self.stack.append(cond_stmt)

    def build_import(self):
        if self.inner:
            self.inner.build_import()
        else:
            block: BlockStmt = self.stack.pop()
            node: ImportNode = self.stack[-1]
            node.block = block

    def new_block(self):
        if self.inner:
            self.inner.new_block()
        else:
            self.inner = AbstractSyntaxTree()

    def add_dict(self):
        if self.inner:
            self.inner.add_dict()
        else:
            inner = AbstractSyntaxTree()
            inner.elements.standalone = True
            self.inner = inner

    def add_class(self, line, class_name, abstract: bool, class_doc: str):
        if self.inner:
            self.inner.add_class(line, class_name, abstract, class_doc)
        else:
            cs = ClassStmt(line, class_name, abstract, class_doc)
            self.stack.append(cs)

    def get_current_class(self):
        if self.inner:
            return self.inner.get_current_class()
        else:
            return self.stack[-1]

    def add_extends(self):
        if self.inner:
            self.inner.add_extends()
        else:
            self.inner = AbstractSyntaxTree()

    def build_class(self):
        if self.inner:
            self.inner.build_class()
        else:
            node = self.stack.pop()
            class_node = self.stack.pop()
            class_node.block = node
            self.stack.append(class_node)

    def add_dot(self, line):
        if self.inner:
            self.inner.add_dot(line)
        else:
            self.in_expr = True
            node = Dot(line)
            self.stack.append(node)

    def add_parenthesis(self):
        if self.inner:
            self.inner.add_parenthesis()
        else:
            block = AbstractSyntaxTree()
            self.inner = block

    def build_parenthesis(self):
        if self.inner.inner:
            self.inner.build_parenthesis()
        else:
            self.inner.build_line()
            block = self.inner.get_as_block()
            self.invalidate_inner()
            if len(block.lines) != 1:
                raise stl.ParseException("Empty parenthesis")
            self.stack.append(block.lines[0])

    def build_extends(self):
        if self.inner.inner:
            self.inner.build_extends()
        else:
            self.inner.build_line()
            block = self.inner.get_as_block()
            self.invalidate_inner()
            clazz: ClassStmt = self.stack[-1]
            clazz.superclass_nodes = block.lines

    def try_build_func(self):
        if self.inner:
            self.inner.try_build_func()
        else:
            if len(self.stack) >= 2:
                prob_func_node = self.stack[-2]
                block_node = self.stack[-1]
                if isinstance(prob_func_node, DefStmt):
                    if isinstance(block_node, BlockStmt):
                        if prob_func_node.abstract:
                            raise stl.ParseException("Abstract function cannot have body")
                        prob_func_node.body = block_node
                        self.stack.pop()

    def build_block(self):
        if self.inner.inner:
            self.inner.build_block()
        else:
            self.inner.build_line()
            root = self.inner.get_as_block()
            self.invalidate_inner()
            self.stack.append(root)

    def build_expr(self):
        if self.inner:
            self.inner.build_expr()
        else:
            if not self.in_expr:
                return
            self.in_expr = False
            lst = []
            # print(self.stack)
            while len(self.stack) > 0:
                node = self.stack[-1]
                if node is None or \
                        isinstance(node, bool) or \
                        isinstance(node, int) or \
                        isinstance(node, float) or \
                        isinstance(node, LeafNode) or \
                        isinstance(node, Expr) or \
                        (isinstance(node, FuncCall) and node.fulfilled()) or \
                        (isinstance(node, IndexingNode) and node.fulfilled()) or \
                        isinstance(node, DefStmt) or \
                        isinstance(node, UndefinedNode) or \
                        (isinstance(node, BlockStmt) and node.standalone):
                    lst.append(node)
                    self.stack.pop()
                else:
                    break
            lst.reverse()

            if len(lst) > 0:
                node = parse_expr(lst)
                self.stack.append(node)
            # print(self.stack)

    def build_line(self):
        if self.inner:
            self.inner.build_line()
        else:
            self.build_expr()
            if len(self.stack) > 0:
                lst = [self.stack.pop()]
                while len(self.stack) > 0:
                    node = self.stack.pop()
                    if isinstance(node, LeafNode):
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    # elif isinstance(node, AssignmentNode) and len(lst) > 0:
                    #     node.right = lst[0]
                    #     lst[0] = node
                    elif isinstance(node, UnaryOperator) and len(lst) > 0 and node.value is None:
                        # The build-expr method was interrupted by something
                        node.value = lst[0]
                        lst[0] = node
                    elif isinstance(node, BinaryExpr) and len(lst) > 0 and node.right is None:
                        node.right = lst[0]
                        lst[0] = node
                    elif isinstance(node, AnnotationNode) and len(lst) > 0 and node.body is None:
                        node.body = lst[0]
                        lst[0] = node
                        # last: AssignmentNode = lst[0]
                        # func: DefStmt = last.right
                        # func.tags = node
                    # elif isinstance(node, TernaryOperator) and len(lst) > 0:
                    #     node.right = lst[0]
                    #     lst[0] = node
                    elif isinstance(node, BlockStmt):
                        if len(lst) > 0:
                            lst.insert(0, node)
                        else:
                            lst.append(node)
                            # res = node
                    elif isinstance(node, IfStmt):
                        if len(lst) == 1:
                            node.then_block = lst[0]
                        # elif len(lst) == 2:
                        #     node.then_block = lst[0]
                        #     node.else_block = lst[1]
                        elif len(lst) != 0:
                            raise stl.ParseException("Unexpected token, in file '{}', at line {}"
                                                     .format(node.file, node.line_num))
                        lst.clear()
                        lst.append(node)
                    elif isinstance(node, WhileStmt) or isinstance(node, ForLoopStmt):
                        if len(lst) == 1:
                            node.body = lst.pop()
                            lst.append(node)
                        elif len(lst) != 0:
                            raise stl.ParseException("Unexpected token")
                        # node.body = lst[0] if len(lst) > 0 else None
                        # lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    elif isinstance(node, CatchStmt):
                        node.then = lst[0] if len(lst) > 0 else None
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    elif isinstance(node, TryStmt):
                        node.try_block = lst[0]
                        if isinstance(lst[-1], CatchStmt):
                            node.catch_blocks = lst[1:]
                        else:
                            node.catch_blocks = lst[1:-1]
                            node.finally_block = lst[-1]
                        lst.clear()
                        lst.append(node)
                    else:
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                        # res = node
                if len(self.elements.lines) > 0:
                    last = self.elements.lines[-1]
                    if place_else(last, lst[0]):
                        return
                self.elements.add_line(lst[0])

    def get_as_block(self) -> BlockStmt:
        if len(self.stack) > 0 or self.in_expr:
            raise stl.ParseException("Line is not terminated")
        return self.elements

    def print_stack(self):
        print([str(x) for x in self.stack])


def get_number(line, v: str):
    try:
        if "." in v:
            return float(v)
        else:
            return int(v)
    except TypeError:
        raise stl.ParseException("Unexpected syntax: '{}', at line {}".format(v, line))


def parse_expr(lst):
    while len(lst) > 1:
        max_pre = 0
        index = 0
        for i in range(len(lst)):
            node = lst[i]
            if isinstance(node, UnaryOperator):
                pre = node.precedence()
                if pre > max_pre and node.value is None:
                    max_pre = pre
                    index = i
            elif isinstance(node, BinaryExpr):
                pre = node.precedence()
                if pre > max_pre and node.left is None and node.right is None:
                    max_pre = pre
                    index = i
            elif isinstance(node, TernaryOperator):
                pre = node.precedence()
                if pre > max_pre and node.left is None and node.mid is None and node.right is None:
                    max_pre = pre
                    index = i
            elif isinstance(node, InDecrementOperator):
                pre = node.precedence()
                if pre > max_pre and node.value is None:
                    max_pre = pre
                    index = i
        operator = lst[index]
        if isinstance(operator, UnaryOperator):
            operator.value = lst[index + 1]
            lst.pop(index + 1)
        elif isinstance(operator, BinaryExpr):
            operator.left = lst[index - 1]
            operator.right = lst[index + 1]
            lst.pop(index + 1)
            lst.pop(index - 1)
        elif isinstance(operator, TernaryOperator):
            operator.left = lst[index - 1]
            operator.mid = lst[index + 1]
            operator.right = lst[index + 2]
            lst.pop(index + 1)
            lst.pop(index + 1)
            lst.pop(index - 1)
        elif isinstance(operator, InDecrementOperator):
            is_post = True
            if index < len(lst) - 1:
                node = lst[index + 1]
                if isinstance(node, NameNode) or isinstance(node, Dot):
                    is_post = False
            operator.is_post = is_post
            if is_post:
                operator.value = lst[index - 1]
                lst.pop(index - 1)
            else:
                operator.value = lst[index + 1]
                lst.pop(index + 1)
        else:
            raise stl.ParseException("Unknown error while parsing operators")
    return lst[0]


def find_else(stmt: Node) -> bool:
    if isinstance(stmt, IfStmt):
        if find_else(stmt.then_block):
            return True

        if stmt.else_block is None:
            stmt.has_else = True
            return True
        else:
            find_else(stmt.else_block)
    return False


def place_else(stmt: Node, element) -> bool:
    if isinstance(stmt, IfStmt):
        if place_else(stmt.then_block, element):
            return True
        if stmt.has_else:
            if stmt.else_block is None:
                stmt.else_block = element
                return True
            else:
                return place_else(stmt.else_block, element)
    return False
