import sympy
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    Use this for any arithmetic, algebra, or mathematical calculations.
    Examples: '10 + 10', 'sqrt(16)', '2**8', 'sin(90)', '100 * 0.18'
    """
    try:
        result = sympy.sympify(expression)
        evaluated = float(result.evalf()) ## evalf() converts to decimal number e.g. sqrt(2) → 1.41421...

        return (
            f"Expression: {expression}, "
            f"Result: {evaluated}"
        )

    except sympy.SympifyError: # Only catches when sympy can't understand your expression.
        return f"Could not parse expression: '{expression}'. Please use valid math syntax."

    except Exception as e:
        return f"Error: {str(e)}"