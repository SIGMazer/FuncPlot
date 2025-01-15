import sys
import re
import numpy as np
from scipy.optimize import root_scalar
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide2.QtGui import QFont
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure

class MathPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Math Plotter")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f0f0;")

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20) 
        self.layout.setSpacing(20) 

        # Input Fields Layout
        self.input_layout = QHBoxLayout()

        self.function1_label = QLabel("Function 1 (f(x)): ")
        self.function1_label.setFont(self.font_style())  # Apply custom font
        self.function1_label.setStyleSheet("color: #333;")  # Set text color

        self.function1_input = QLineEdit()
        self.function1_input.setStyleSheet("background-color: #fff; border: 1px solid #ccc; padding: 5px; border-radius: 5px;")
        self.function1_input.setFont(self.font_style()) 

        self.function2_label = QLabel("Function 2 (g(x)): ")
        self.function2_label.setFont(self.font_style())
        self.function2_label.setStyleSheet("color: #333;")

        self.function2_input = QLineEdit()
        self.function2_input.setStyleSheet("background-color: #fff; border: 1px solid #ccc; padding: 5px; border-radius: 5px;")
        self.function2_input.setFont(self.font_style())

        self.solve_button = QPushButton("Solve and Plot")
        self.solve_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px 20px; font-size: 14px;")
        self.solve_button.setFont(self.font_style())
        self.solve_button.clicked.connect(self.solve_and_plot)

        # Add widgets to input layout
        self.input_layout.addWidget(self.function1_label)
        self.input_layout.addWidget(self.function1_input)
        self.input_layout.addWidget(self.function2_label)
        self.input_layout.addWidget(self.function2_input)
        self.input_layout.addWidget(self.solve_button)

        self.layout.addLayout(self.input_layout)

        # Matplotlib Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def font_style(self):
        """Return a standard font for the app."""
        return QFont("Arial", 12)

    def validate_function(self, func):
        # Allowable characters and functions
        pattern = r"^[0-9x+\-*/^().\sloglog10log2sqrt]+$"
        
        if not re.match(pattern, func):
            return False
        
        # Check for consecutive operators (e.g., **, //, ++)
        if re.search(r"[\^*/+\-]{2,}", func):
            return False
        
        # Check parentheses pairing
        stack = []
        for char in func:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack:
                    return False
                stack.pop()
        if stack: 
            return False
    
        if func.strip()[0] in "+-*/^" or func.strip()[-1] in "+-*/^":
            return False

        # check for negative numbers in sqrt and log functions
        if re.search(r"sqrt\(\s*-", func):
            return False

        if re.search(r"log.*\(\s*-", func):
            return False


        return True


    def parse_function(self, func):
        try:
            func = func.replace('^', '**').replace('sqrt', 'np.sqrt').replace('log', 'np.log')
            def parsed_func(x):
                return eval(func)
            return parsed_func
        except Exception:
            return None

    def solve_and_plot(self):
        func1_str = self.function1_input.text().strip()
        func2_str = self.function2_input.text().strip()

        if not self.validate_function(func1_str) or not self.validate_function(func2_str):
            QMessageBox.warning(self, "Invalid Input", "Please enter valid mathematical functions.")
            return

        func1 = self.parse_function(func1_str)
        func2 = self.parse_function(func2_str)

        if not func1 or not func2:
            QMessageBox.critical(self, "Error", "Failed to parse one or both functions.")
            return

        # Define range and compute values
        x = np.linspace(-10, 10, 500)
        try:  

            # Avoid division by zero
            y1 = np.array([func1(val) if val != 0 else np.nan for val in x])
            y2 = np.array([func2(val) if val != 0 else np.nan for val in x]) 

            def diff(x):
                if np.isnan(x) or x == 0:  # Avoid division by zero for the difference
                    return np.nan
                return func1(x) - func2(x)

            solution_points = []
            for i in range(len(x) - 1):
                if not np.isnan(diff(x[i])) and not np.isnan(diff(x[i + 1])):  # Skip invalid ranges
                    if diff(x[i]) * diff(x[i + 1]) < 0:  # Check for a sign change
                        sol = root_scalar(diff, bracket=[x[i], x[i + 1]], method='brentq')
                        if sol.converged:
                            solution_points.append((sol.root, func1(sol.root)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to evaluate functions: {str(e)}")
            return

        # Clear the Plot
        self.figure.clear()

        # Plot
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.plot(x, y1, label="f(x)", color='#1f77b4', linewidth=2)
        ax.plot(x, y2, label="g(x)", color='#ff7f0e', linewidth=2)

        for root, value in solution_points:
            ax.plot(root, value, 'ro')
            ax.annotate(f"({root:.2f}, {value:.2f})", (root, value), textcoords="offset points", xytext=(5, 5), fontsize=10, color='darkred')

        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_title("Function Plot", fontsize=16, fontweight='bold')
        ax.set_xlabel("x", fontsize=12)
        ax.set_ylabel("y", fontsize=12)

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MathPlotterApp()
    main_window.show()
    sys.exit(app.exec_())

