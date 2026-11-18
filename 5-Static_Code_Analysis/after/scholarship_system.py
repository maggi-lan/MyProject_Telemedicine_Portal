"""Evaluate scholarship applicants and manage application results."""

import ast
import json
import operator
from pathlib import Path

MERIT_FORMULA = "gpa * 10 + credits * 2"
INCOME_LIMIT = 800000
CUTOFF = 85

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate_expression(node, values):
    """Evaluate a restricted arithmetic expression without executing code."""
    if isinstance(node, ast.Expression):
        return _evaluate_expression(node.body, values)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _evaluate_expression(node.left, values)
        right = _evaluate_expression(node.right, values)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        operand = _evaluate_expression(node.operand, values)
        return _ALLOWED_OPERATORS[type(node.op)](operand)
    raise ValueError("Formula contains an unsupported expression.")


def calculate_merit_score(gpa, credit_count, formula=MERIT_FORMULA):
    """Calculate merit score from GPA, credits, and a safe arithmetic formula."""
    try:
        expression = ast.parse(formula, mode="eval")
        score = _evaluate_expression(expression, {"gpa": gpa, "credits": credit_count})
    except (SyntaxError, TypeError, ZeroDivisionError, OverflowError) as error:
        raise ValueError("Invalid merit formula.") from error
    if not isinstance(score, (int, float)):
        raise ValueError("Merit formula must produce a number.")
    return score


def evaluate_applicant(student_id, test_scores, results, logs=None, formula=MERIT_FORMULA):
    """Evaluate an applicant and record the result and optional log message."""
    if logs is None:
        logs = []
    gpa = test_scores["gpa"]
    credit_count = test_scores.get("credits", 0)
    income = test_scores.get("income", 0)
    score = calculate_merit_score(gpa, credit_count, formula)
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    results[student_id] = {"score": score, "eligible": eligible}
    logs.append(f"{student_id} scored {score}")
    return eligible


def persist_results(results, file="scholarships.json"):
    """Write applicant results to a JSON file using UTF-8 encoding."""
    with Path(file).open("w", encoding="utf-8") as output_file:
        json.dump(results, output_file, indent=2)


def load_results(file="scholarships.json"):
    """Load results from JSON; return an empty dictionary if the file is absent."""
    try:
        with Path(file).open("r", encoding="utf-8") as input_file:
            loaded_results = json.load(input_file)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"Could not load results from {file!r}.") from error
    if not isinstance(loaded_results, dict):
        raise ValueError("Results file must contain a JSON object.")
    return loaded_results


def print_shortlist(results):
    """Print applicants who meet the scholarship eligibility criteria."""
    print("Shortlisted applicants:")
    for student_id, applicant in results.items():
        if applicant.get("eligible") is True:
            print(" ", student_id, "score =", applicant["score"])


def main():
    """Run the sample scholarship evaluation workflow."""
    results = {}
    logs = []
    formula = MERIT_FORMULA
    evaluate_applicant(
        "U001", {"gpa": 9.1, "credits": 4, "income": 450000}, results, logs, formula
    )
    evaluate_applicant(
        "U002", {"gpa": 7.2, "credits": 1, "income": 300000}, results, logs, formula
    )
    evaluate_applicant(
        "U003", {"gpa": 12.5, "credits": -3, "income": -1}, results, logs, formula
    )
    evaluate_applicant("U004", {"gpa": 6.5}, results, logs, formula)
    new_formula = input("Merit formula (Enter to keep default): ").strip()
    if new_formula:
        # Validate the formula before using it for subsequent applicants.
        calculate_merit_score(1, 1, new_formula)
        formula = new_formula
    evaluate_applicant(
        "U005", {"gpa": 8.4, "credits": 3, "income": 600000}, results, logs, formula
    )
    persist_results(results)
    results = load_results()
    print_shortlist(results)


if __name__ == "__main__":
    main()
