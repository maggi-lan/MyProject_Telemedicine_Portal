# Reflection

1. What is the purpose of static code analysis?
It examines source code without running the application to identify likely bugs, insecure patterns, maintainability issues, and style violations.

2. What did the tools identify in this program?
Bandit flagged eval() and a try/except/pass block. Pylint identified unsafe eval usage, a mutable default argument, missing docstrings, global state, unmanaged file access, unused imports, and naming/style issues. Flake8 reported unused imports, bare except, spacing, and a boolean-comparison issue.

3. Which fixes were most important?
Removing eval() was the most important security fix because a custom formula could otherwise execute arbitrary Python expressions. Replacing the silent broad exception handling was important for reliable error reporting. The mutable default argument and file-handling changes improved correctness and resource management.

4. How were the fixes verified?
The fixed script passed Python bytecode compilation and smoke tests for default/custom formulas, rejection of an unsafe formula, independent log lists, JSON persistence, and missing-file behavior.
