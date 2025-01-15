import pytest
from PySide2.QtWidgets import QApplication
from main import MathPlotterApp  
import numpy as np
from PySide2.QtCore import Qt
from scipy.optimize import root_scalar
from unittest.mock import patch
from PySide2.QtWidgets import QMessageBox

@pytest.fixture
def app_instance(qtbot):
    app = MathPlotterApp()
    qtbot.addWidget(app)
    return app

def test_validate_function(app_instance):
    valid_functions = ["x^2", "log(x)", "sqrt(x)", "2*x + 3", "x^3 + x^2 - x", "log10(x) + 1"]
    invalid_functions = ["abc", "x//y", "x**", "2*x @ 3","sqrt(", "(x+1))"]

    for func in valid_functions:
        assert app_instance.validate_function(func) is True

    for func in invalid_functions:
        assert app_instance.validate_function(func) is False

def test_parse_function(app_instance):
    func_str = "x^2 + 2*x + 1"
    parsed_func = app_instance.parse_function(func_str)

    x = 2
    expected_value = x**2 + 2*x + 1
    assert parsed_func(x) == expected_value

def test_solve_and_plot(app_instance, qtbot):
    qtbot.keyClicks(app_instance.function1_input, "x^2")
    qtbot.keyClicks(app_instance.function2_input, "2*x + 1")
    qtbot.mouseClick(app_instance.solve_button, Qt.LeftButton)

    assert app_instance.canvas is not None

    x = np.linspace(-10, 10, 500)
    f1 = lambda x: x**2
    f2 = lambda x: 2*x + 1
    diff = lambda x: f1(x) - f2(x)
    
    solution_points = []
    for i in range(len(x) - 1):
        if diff(x[i]) * diff(x[i + 1]) < 0:
            sol = root_scalar(diff, bracket=[x[i], x[i + 1]], method='brentq')
            if sol.converged:
                solution_points.append((sol.root, f1(sol.root)))

    for root, value in solution_points:
        assert any(abs(root - x) < 1e-2 for x, _ in solution_points)
        assert any(abs(value - y) < 1e-2 for _, y in solution_points)

def test_invalid_input_handling(app_instance, qtbot):
    with patch.object(QMessageBox, 'warning', return_value=None):
        qtbot.keyClicks(app_instance.function1_input, "invalid_func")
        qtbot.keyClicks(app_instance.function2_input, "x^2")
        qtbot.mouseClick(app_instance.solve_button, Qt.LeftButton)

    assert app_instance.function1_input.text() == "invalid_func"
    assert app_instance.function2_input.text() == "x^2"

def test_validate_function_empty(app_instance):
    assert app_instance.validate_function("") is False

def test_validate_function_with_spaces(app_instance):
    valid_function = "  x + 1  "
    invalid_function = " x@2 + 1 "
    assert app_instance.validate_function(valid_function.strip()) is True
    assert app_instance.validate_function(invalid_function.strip()) is False

def test_validate_function_invalid_characters(app_instance):
    invalid_functions = ["x@", "x#", "log10(x)*$", "sqrt(x)@"]
    for func in invalid_functions:
        assert app_instance.validate_function(func) is False

def test_validate_function_complex(app_instance):
    valid_functions = ["x^2 + 2*x - 3", "sqrt(x) + log10(x)", "x^3 + 5*x^2 + 4"]
    for func in valid_functions:
        assert app_instance.validate_function(func) is True

def test_solve_and_plot_edge_cases(app_instance, qtbot):
    edge_case_functions = [
        ("1/(x-2)", "x^2 - 4"),        # Function with a vertical asymptote
        ("x^3", "x"),                  # Higher-degree polynomial intersecting a line
    ]

    with patch.object(QMessageBox, 'critical', return_value=None):
        for func1, func2 in edge_case_functions:
            qtbot.keyClicks(app_instance.function1_input, func1)
            qtbot.keyClicks(app_instance.function2_input, func2)
            qtbot.mouseClick(app_instance.solve_button, Qt.LeftButton)
            assert app_instance.canvas is not None  # Check if canvas is updated

def test_division_by_zero_handling(app_instance, qtbot):
    with patch.object(QMessageBox, 'critical', return_value=None):
        qtbot.keyClicks(app_instance.function1_input, "1/x")
        qtbot.keyClicks(app_instance.function2_input, "x^2")
        qtbot.mouseClick(app_instance.solve_button, Qt.LeftButton)

def test_function_with_large_values(app_instance, qtbot):
    qtbot.keyClicks(app_instance.function1_input, "10^x")
    qtbot.keyClicks(app_instance.function2_input, "x")
    qtbot.mouseClick(app_instance.solve_button, Qt.LeftButton)
    assert app_instance.canvas is not None

def test_function_with_negative_domain(app_instance, qtbot):
    """Check valid domain for functions"""""
    assert app_instance.validate_function("sqrt(x)") is True

    assert app_instance.validate_function("sqrt(-x)") is False

    assert app_instance.validate_function("log(-x)") is False

    assert app_instance.validate_function("log10(-x)") is False

    # UI test for invalid domain
    with patch.object(QMessageBox, 'warning', return_value=None) as mock_warning:
        qtbot.keyClicks(app_instance.function1_input, "sqrt(-x)")
        qtbot.mouseClick(app_instance.solve_button, Qt.LeftButton)

        mock_warning.assert_called_once()

