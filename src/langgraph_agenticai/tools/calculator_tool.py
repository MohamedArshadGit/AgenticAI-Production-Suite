import sympy

def calculator(expression:str)->dict:
    """
    Evaluate a mathematical expression safely.
    Use this for any arithmetic, algebra, or mathematical calculations.
    Examples: '10 + 10', 'sqrt(16)', '2**8', 'sin(90)', '100 * 0.18'

    Args:
        expression: A mathematical expression as a string

    Returns:
        dict with the result or error message

    """

    try:
        result =sympy.sympify(expression)
        evaluated =float(result.evalf()) ## evalf() converts to decimal number e.g. sqrt(2) → 1.41421...

        return {"status":"Success",
                "expression":expression,
                "result":evaluated}

    except sympy.SympifyError: #Only catches when sympy can't understand your expression.
        return {
            "status": "error",
            "message": f"Could not parse expression: '{expression}'. Please use valid math syntax."
        }
    
    except Exception as e:
        return {"status":"Error",
                "message":str(e)}