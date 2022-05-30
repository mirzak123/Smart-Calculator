from custom_exceptions import *
from collections import deque
import re


class Calculator:
    """
    Calculator that deals with integer values, has ability of storing variables and supports the following operations: '+', '-', '*', '/', '^'

    Works by transforming an expression received in infix form to postfix notation and then evaluating that postfix
     expression.
    Functionalities:
        * Commands:
            1. /help - outputs instructions
            2. /exit - quits the program
        * Variables:
            Assign variable values in the following form: " variableName = value "
            Variable name MUST consist of only latin letters
            Usage of space separation does not matter
        * Expressions:
            input: infix notation expression
            You can use numbers of previously assigned variables
            Parentheses must be properly closed!
            Usage of space separation does not matter
    """

    priority = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3, '(': 0}  # special case '(': 0 to avoid KeyErrors

    def __init__(self):
        self.total = 0
        self.variables = {}  # store all variables declared during one program execution
        self.postfix = deque()  # expression postfix notation; reinitialized after every expression evaluation

    def start_calculator(self):
        while True:
            expression = input().strip()
            if expression == '':
                continue
            if expression[0] == '/':
                try:
                    command_value = self.handle_command(expression)
                except UnknownCommandError as err:
                    print(err)
                    continue
                if command_value == -1:
                    break
            elif '=' in expression or expression.isalpha():
                try:
                    self.handle_variable(expression)
                except InvalidIdentifierError as err:
                    print(err)
                except UnknownVariableError as err:
                    print(err)
                except InvalidAssignmentError as err:
                    print(err)
            else:
                try:
                    self.handle_expression(expression)
                except InvalidExpressionError as err:
                    print(err)
                except UnknownVariableError as err:
                    print(err)
                else:
                    print(self.total)
                    self.total = 0

    def infix_to_postfix(self, infix):
        """
        Return an expression in postfix notation with the help of a stack

        :param infix: expression in infix notation in the form of a list
        :return: postfix: expression in postfix notation in the form of a collections.deque

        Operand -- numbers or variables
        Operator -- {+, -, *, /, ^}

        How:
            1. Infix expression is evaluated from left to right
            2. When an operand is encountered, it is added to the postfix expression
            3. When an operator is encountered, it is pushed onto the stack while following the rules stated below
            4. When all elements from the infix expression have been evaluated, operators are popped and added to the
                postfix expression accordingly


        Rules for infix to postfix:
            1. Priorities of operators from highest to lowest: '^' -> '*', '/' -> '+', '-'
            2. No two operators of same priority can stay together in the stack. In such cases you pop the previous
                operator and add it to the postfix expression
            3. Lower priority operator cannot be placed on top of a higher priority operator in the stack. Pop the
                higher priority operator and then push the incoming operator onto the stack
            4. If you encounter closing parentheses, pop everything enclosed by the parentheses and add to postfix exp.
        """

        stack = deque()
        postfix = deque()

        for ch in infix:
            # print(list(self.postfix), list(stack))
            if ch.isalnum():
                postfix.append(ch)
            elif ch == '(':
                stack.append(ch)
            elif ch == ')':
                while len(stack) != 0 and stack[-1] != '(':
                    postfix.append(stack.pop())
                if len(stack) == 0:
                    raise InvalidExpressionError
                stack.pop()
            elif len(stack) == 0 or self.priority[ch] > self.priority[stack[-1]]:
                stack.append(ch)
            else:
                while len(stack) != 0 and self.priority[ch] <= self.priority[stack[-1]]:
                    postfix.append(stack.pop())
                stack.append(ch)

        while stack:
            postfix.append(stack.pop())
        if '(' in postfix:
            raise InvalidExpressionError
        # print(*list(self.postfix), sep='')

        return postfix

    def evaluate_postfix(self):
        """
        Return the result of postfix expression

        :input: nothing since the current postfix expression is visible to the calculator object
        :return: Result of the expression evaluation

        Operand -- numbers or variables
        Operator -- {+, -, *, /, ^}

        How:
            1. Loop through elements in postfix expression
            2. When an operand is encountered it is pushed onto the stack
            3. When an operator is encountered, two stack operands are popped and the appropriate operation is performed
                on them (In case there is only one element in the stack, it is popped and the other value will be 0).
                The result is then pushed back onto the stack.
            4. When all elements in postfix expression have been evaluated, reinitialize the instance variable
                self.postfix, and return the element left in the stack as the result of the evaluation
        """

        stack = deque()
        for ch in self.postfix:
            if ch in '+-*/^':
                b = stack.pop()
                try:
                    a = stack.pop()
                except IndexError:
                    a = 0
                if ch == '+':
                    stack.append(a + b)
                elif ch == '-':
                    stack.append(a - b)
                elif ch == '*':
                    stack.append(a * b)
                elif ch == '/':
                    stack.append(a // b)
                elif ch == '^':
                    stack.append(a ** b)
            elif ch.isdigit():
                stack.append(int(ch))
            else:  # ch is a variable
                if ch in self.variables:
                    stack.append(int(self.variables[ch]))
                else:
                    raise UnknownVariableError
        self.postfix = deque()
        return stack.pop()

    def handle_command(self, command):
        if command == '/exit':
            print("Bye!")
            return -1
        if command == '/help':
            print(self.__doc__)
            return 0
        raise UnknownCommandError

    def handle_variable(self, expression):
        """
        Check if variable is tried to be initialized and check the validity of that attempt. If variable is being
        accessed (only variable name has been inputted), check if it has been initialized and output it to the console
        or raise appropriate Exceptions.
        """

        expression = expression.split('=')
        if len(expression) > 2:
            raise InvalidAssignmentError
        elif len(expression) == 1:
            variable = expression[0].strip(' ')
            if not variable.isalpha():
                raise InvalidIdentifierError
            try:
                print(self.variables[variable])
            except KeyError:
                raise UnknownVariableError
        else:
            variable = expression[0].strip(' ')
            value = expression[1].strip(' ')
            if not variable.isalpha():
                raise InvalidIdentifierError
            if value in self.variables:
                value = self.variables[value]
            try:
                value = int(value)
            except ValueError:
                raise InvalidAssignmentError
            else:
                self.variables[variable] = str(value)

    def handle_expression(self, expression):
        infix = self.get_infix(expression)
        self.postfix = self.infix_to_postfix(infix)
        self.total = self.evaluate_postfix()

    def get_infix(self, expression):
        """
        Return infix notation of user inputted expression in the form of a list

        :param expression: raw input of the user
        :return:

        How:
            Split user input using re.split(...) and eliminate all None and empty string '' values.
        """

        pattern = r'(\w+)?([+-]+)?([*/^]+)?([\(\)])?'
        infix = [ch for ch in re.split(pattern, expression.replace(' ', '')) if ch]  # eliminate all spaces beforehand
        for i, ch in enumerate(infix):
            if ('*' in ch or '/' in ch or '^' in ch) and len(ch) > 1:
                raise InvalidExpressionError
            if ('+' in ch or '-' in ch) and len(ch) > 1:
                infix[i] = '-' if ch.count('-') % 2 == 1 else '+'

        return infix


def main():
    calculator = Calculator()
    calculator.start_calculator()


if __name__ == "__main__":
    main()
