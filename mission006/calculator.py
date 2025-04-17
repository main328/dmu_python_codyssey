from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout
)
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Calculator')
        self.setFixedSize(300, 400)
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout()

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(50)
        self.display.setStyleSheet('font-size: 24px;')
        layout.addWidget(self.display)

        buttons = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '−'],
            ['1', '2', '3', '+'],
            ['0', '0', '.', '=']
        ]

        grid = QGridLayout()
        for row, row_values in enumerate(buttons):
            for col, button_text in enumerate(row_values):
                if row == 4 and col == 0:
                    continue
                button = QPushButton(button_text)
                button.setFixedSize(60, 60)
                button.setStyleSheet('font-size: 18px;')
                button.clicked.connect(self.on_button_clicked)
                grid.addWidget(button, row, col)

        zero_button = QPushButton('0')
        zero_button.setFixedHeight(60)
        zero_button.setStyleSheet('font-size: 18px;')
        zero_button.clicked.connect(self.on_button_clicked)
        grid.addWidget(zero_button, 4, 0, 1, 2)

        layout.addLayout(grid)
        self.setLayout(layout)
        self.expression = ''

    def on_button_clicked(self):
        sender = self.sender()
        value = sender.text()

        if value == 'C':
            self.expression = ''
        elif value == '=':
            try:
                expression = self.expression.replace('×', '*').replace('÷', '/').replace('−', '-')
                result = str(eval(expression))
                self.expression = result
            except Exception:
                self.expression = 'Error'
        elif value == '±':
            if self.expression:
                if self.expression.startswith('-'):
                    self.expression = self.expression[1:]
                else:
                    self.expression = '-' + self.expression
        elif value == '%':
            try:
                self.expression = str(eval(self.expression) / 100)
            except Exception:
                self.expression = 'Error'
        else:
            self.expression += value

        self.display.setText(self.expression)


app = QApplication([])
calculator = Calculator()
calculator.show()
app.exec_()
