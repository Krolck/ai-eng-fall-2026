import ast
import math
import tkinter as tk
from tkinter import ttk


class SafeEvaluator:
    """Safely evaluate arithmetic expressions."""

    allowed_operators = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: +a,
    }

    def evaluate(self, expression: str):
        if not expression:
            raise ValueError("Nothing to calculate")

        try:
            parsed = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError("Invalid expression") from exc

        return self._eval_node(parsed.body)

    def _eval_node(self, node):
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = type(node.op)
            if op not in self.allowed_operators:
                raise ValueError("Unsupported operation")
            return self.allowed_operators[op](left, right)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = type(node.op)
            if op not in self.allowed_operators:
                raise ValueError("Unsupported operation")
            return self.allowed_operators[op](operand)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.Num) and isinstance(node.n, (int, float)):
            return node.n

        raise ValueError("Unsupported expression")


class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("360x500")
        self.root.resizable(False, False)

        self.expression = ""
        self.evaluator = SafeEvaluator()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Display.TLabel", font=("Segoe UI", 28), background="#f4f4f4", foreground="#1f1f1f")
        self.style.configure("Button.TButton", font=("Segoe UI", 18), padding=10)

        self.display_var = tk.StringVar(value="0")
        self.display = ttk.Label(root, textvariable=self.display_var, anchor="e", style="Display.TLabel", padding=(20, 15))
        self.display.pack(fill="x")

        button_frame = ttk.Frame(root, padding=10)
        button_frame.pack(fill="both", expand=True)

        buttons = [
            ["C", "⌫", "%", "/"],
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "(", ")"],
            ["="]
        ]

        self.button_map = {}
        for row in buttons:
            if row == ["="]:
                btn = ttk.Button(button_frame, text="=", command=self.calculate, style="Button.TButton")
                btn.pack(fill="x", pady=4)
                self.button_map["="] = btn
                continue

            for label in row:
                btn = ttk.Button(button_frame, text=label, command=lambda value=label: self.on_button_click(value), style="Button.TButton")
                btn.pack(side="left", fill="both", expand=True, padx=2, pady=2)
                self.button_map[label] = btn

        self.root.bind("<KeyPress>", self.key_press)

    def display_value(self):
        return self.display_var.get()

    def update_display(self, value):
        self.display_var.set(value)

    def on_button_click(self, value):
        if value == "C":
            self.expression = ""
            self.update_display("0")
            return

        if value == "⌫":
            self.expression = self.expression[:-1]
            self.update_display(self.expression if self.expression else "0")
            return

        if value == "=":
            self.calculate()
            return

        self.expression += str(value)
        self.update_display(self.expression)

    def calculate(self):
        try:
            result = self.evaluator.evaluate(self.expression)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(result)
            self.update_display(self.expression)
        except (ValueError, ZeroDivisionError):
            self.expression = ""
            self.update_display("Error")

    def key_press(self, event):
        key = event.char

        if key.isdigit() or key in ".+-*/()%":
            self.on_button_click(key)
        elif event.keysym == "Return":
            self.calculate()
        elif event.keysym == "BackSpace":
            self.on_button_click("⌫")
        elif event.keysym == "Escape":
            self.on_button_click("C")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
