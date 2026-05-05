import sys

class Tokenizer:
    TERMINALS = {
        "+": ("PLUS", "+"),
        "-": ("MINUS", "-"),
        "=": ("ASSIGN", "="),
        "/": ("DIVIDE", "/"),
        "*": ("MULTI", "*"),
        "(": ("LPAREN", "("),
        ")": ("RPAREN", ")"),
        ";": ("SEMICOLON", ";"),
    }

    KEYWORDS = {"let": "LET"}

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.state = 0

    def _next_char(self):
        c = self.source[self.pos]
        self.pos += 1
        return c

    def _flush_identifier(self, temp, tokens):
        if temp in self.KEYWORDS:
            tokens.append((self.KEYWORDS[temp], temp))
        else:
            tokens.append(("IDENTIFIER", temp))

    def tokenize(self):
        self.pos = 0
        self.state = 0
        temp = ""
        tokens = []

        while self.pos < len(self.source):
            c = self._next_char()
            match self.state:
                case 0:
                    if c in self.TERMINALS:
                        tokens.append(self.TERMINALS[c])
                    elif c.isspace():
                        continue
                    elif c.isalpha() or c == "_":
                        temp += c
                        self.state = 1
                    elif "1" <= c <= "9":
                        temp += c
                        self.state = 2
                    elif c == "0":
                        temp += c
                        self.state = 3
                    else:
                        raise Exception(f"Invalid character: {c!r}")
                case 1:
                    if c.isalnum() or c == "_":
                        temp += c
                    else:
                        self._flush_identifier(temp, tokens)
                        temp = ""
                        self.state = 0
                        self.pos -= 1
                case 2:
                    if c.isdigit():
                        temp += c
                    else:
                        tokens.append(("LITERAL", temp))
                        temp = ""
                        self.state = 0
                        self.pos -= 1
                case 3:
                    if c.isdigit():
                        raise Exception("Invalid literal with leading zero")
                    else:
                        tokens.append(("LITERAL", temp))
                        temp = ""
                        self.state = 0
                        self.pos -= 1

        match self.state:
            case 1:
                self._flush_identifier(temp, tokens)
            case 2 | 3:
                tokens.append(("LITERAL", temp))

        return tokens


class Node:
    def __init__(self, tag, value=None):
        self.tag = tag
        self.value = value
        self.children = []

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _match(self, expected_type):
        token = self._peek()
        if token is None or token[0] != expected_type:
            raise Exception(
                f"Expected {expected_type}, got {token} at position {self.pos}"
            )
        self.pos += 1
        return token

    def parse(self):
        node = Node("Program")
        while self._peek() is not None:
            node.children.append(self.assignment())
        return node

    def assignment(self):
        token = self._peek()
        if token is None:
            raise Exception("Expected assignment but reached end of input")

        is_let = token[0] == "LET"
        if is_let:
            self._match("LET")

        ident = self._match("IDENTIFIER")
        self._match("ASSIGN")
        exp_node = self.exp()
        self._match("SEMICOLON")

        node = Node("LetAssignment" if is_let else "Assignment", value=ident[1])
        node.children.append(exp_node)
        return node

    def exp(self):
        return self.exp_prime(self.term())

    def exp_prime(self, left):
        token = self._peek()
        if token and token[0] == "PLUS":
            self._match("PLUS")
            right = self.term()
            node = Node("Add")
            node.children = [left, right]
            return self.exp_prime(node)
        elif token and token[0] == "MINUS":
            self._match("MINUS")
            right = self.term()
            node = Node("Subtract")
            node.children = [left, right]
            return self.exp_prime(node)
        else:
            return left

    def term(self):
        return self.term_prime(self.fact())

    def term_prime(self, left):
        token = self._peek()
        if token and token[0] == "MULTI":
            self._match("MULTI")
            right = self.fact()
            node = Node("Multiply")
            node.children = [left, right]
            return self.term_prime(node)
        else:
            return left

    def fact(self):
        token = self._peek()
        if token is None:
            raise Exception("Expected a factor but reached end of input")

        ttype = token[0]

        if ttype == "LPAREN":
            self._match("LPAREN")
            node = self.exp()
            self._match("RPAREN")
            return node

        if ttype == "MINUS":
            self._match("MINUS")
            operand = self.fact()
            node = Node("Negate")
            node.children.append(operand)
            return node

        if ttype == "PLUS":
            self._match("PLUS")
            return self.fact()

        if ttype == "LITERAL":
            tok = self._match("LITERAL")
            return Node("Literal", value=int(tok[1]))

        if ttype == "IDENTIFIER":
            tok = self._match("IDENTIFIER")
            return Node("Identifier", value=tok[1])

        raise Exception(
            f"Unexpected token {token[0]} ('{token[1]}') at position {self.pos}"
        )


class Evaluator:
    def __init__(self):
        self.vars = {}   
        self.order = [] 

    def run(self, program_node):
        for assignment in program_node.children:
            self._exec_assignment(assignment)
        return [(name, self.vars[name][0]) for name in self.order]

    def _exec_assignment(self, node):
        name = node.value
        exp_node = node.children[0]

        if node.tag == "LetAssignment":
            if name in self.vars:
                raise Exception(f"Cannot redefine '{name}' with let")
            value = self._eval(exp_node, let_context=True)
            self.vars[name] = (value, True)
            self.order.append(name)
        else:
            if name in self.vars and self.vars[name][1]:
                raise Exception(f"Cannot reassign let variable '{name}'")
            value = self._eval(exp_node, let_context=False)
            if name not in self.vars:
                self.order.append(name)
            self.vars[name] = (value, False)

    def _eval(self, node, let_context):
        tag = node.tag
        if tag == "Literal":
            return node.value
        if tag == "Identifier":
            return self._lookup(node.value, let_context)
        if tag == "Add":
            return self._eval(node.children[0], let_context) + \
                   self._eval(node.children[1], let_context)
        if tag == "Subtract":
            return self._eval(node.children[0], let_context) - \
                   self._eval(node.children[1], let_context)
        if tag == "Multiply":
            return self._eval(node.children[0], let_context) * \
                   self._eval(node.children[1], let_context)
        if tag == "Negate":
            return -self._eval(node.children[0], let_context)
        raise Exception(f"Unknown node tag: {tag}")

    def _lookup(self, name, let_context):
        if name not in self.vars:
            raise Exception(f"Uninitialized variable '{name}'")
        value, is_let = self.vars[name]
        if let_context and not is_let:
            raise Exception(f"normal variable '{name}' used in let expression")
        return value


def interpret(source):
    try:
        tokens = Tokenizer(source).tokenize()
        ast = Parser(tokens).parse()
        results = Evaluator().run(ast)
    except Exception:
        print("error")
        return
    for name, val in results:
        print(f"{name} = {val}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try: 
            with open(sys.argv[1]) as f:
                src = f.read()
            interpret(src)
        except Exception as e:
            print(f"Unexpected error has occurred: {e}")
            exit()
    else:
        print("Usage: python interpreter.py <file>\n")
        exit()
