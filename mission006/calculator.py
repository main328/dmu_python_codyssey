from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Calculator')
        self.setFixedSize(300, 400)
        self.expression = ''
        self.create_ui()

    def create_ui(self):
        layout = QVBoxLayout()

        # Display setup
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(50)
        self.display.setStyleSheet('font-size: 24px;')
        layout.addWidget(self.display)

        # Button layout
        buttons = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '−'],
            ['1', '2', '3', '+'],
            ['0', '0', '.', '=']
        ]

        grid = self.create_buttons(buttons)
        layout.addLayout(grid)
        self.setLayout(layout)
        
    def create_buttons(self, buttons):
        grid = QGridLayout()

        for row, row_values in enumerate(buttons):
            for col, button_text in enumerate(row_values):
                if row == 4 and col == 0:  # Skip the duplicate zero button slot
                    continue

                button = self.create_button(button_text)
                grid.addWidget(button, row, col)

        # Special "0" button setup to span across two columns
        zero_button, span = self.create_button('0', span=(1, 2))
        grid.addWidget(zero_button, 4, 0, span[0], span[1])

        return grid

    def create_button(self, text, span=None):
        button = QPushButton(text)
        button.setFixedSize(60, 60)
        button.setStyleSheet('font-size: 18px;')
        button.clicked.connect(self.on_button_clicked)

        if span:
            return button, span
        return button

    def on_button_clicked(self):
        sender = self.sender()
        value = sender.text()

        if value == 'C':
            self.expression = ''
        elif value == '=':
            self.calculate_result()
        elif value == '±':
            self.toggle_sign()
        elif value == '%':
            self.calculate_percentage()
        else:
            self.expression += value

        self.display.setText(self.expression)

    def calculate_result(self):
        try:
            expression = self.expression.replace('×', '*').replace('÷', '/').replace('−', '-')
            result = str(eval(expression))
            self.expression = result
        except Exception:
            self.expression = 'Error'

    def toggle_sign(self):
        if self.expression:
            self.expression = self.expression[1:] if self.expression.startswith('-') else '-' + self.expression

    def calculate_percentage(self):
        try:
            self.expression = str(eval(self.expression) / 100)
        except Exception:
            self.expression = 'Error'


app = QApplication([])
calculator = Calculator()
calculator.show()
app.exec_()
