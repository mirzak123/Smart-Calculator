"""
Custom exceptions needed for the calculator.py program
"""


class InvalidExpressionError(Exception):
    """
    Raise in case of: improper usage of parentheses
                      multiple '*' or '/' signs used after each other
    """

    def __str__(self):
        return "Invalid expression"


class UnknownCommandError(Exception):
    """
    Raise in case of: user tries to access a command that has not been defined
    """

    def __str__(self):
        return "Unknown command"


class InvalidIdentifierError(Exception):
    """
    Raise in case of: user enters a variable that consists of characters other than latin letters
    """

    def __str__(self):
        return "Invalid identifier"


class UnknownVariableError(Exception):
    """
    Raise in case of: user tries to access a variable that has not been declared
    """

    def __str__(self):
        return "Unknown variable"


class InvalidAssignmentError(Exception):
    """
    Raise in case of: user tries to set an invalid value to a variable
                      more than one '=' sign used in variable assignment
    """

    def __str__(self):
        return "Invalid assignment"
