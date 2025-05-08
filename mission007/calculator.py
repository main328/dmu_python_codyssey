from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout,
                            QVBoxLayout, QPushButton, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import locale

class CalculatorLogic:
    """
    계산기의 핵심 로직을 담당하는 클래스입니다.
    사칙연산, 음수/양수 전환, 퍼센트 계산 등의 기능을 제공합니다.
    """
    def __init__(self):
        """
        CalculatorLogic 클래스의 생성자입니다.
        계산 상태를 초기화합니다.
        """
        self.reset()

    def reset(self):
        """
        계산 상태를 초기화합니다.
        첫 번째 피연산자(operand1)와 연산자(operator)를 None으로 설정합니다.
        """
        self.operand1 = None
        self.operator = None

    def set_operand(self, operand):
        """
        첫 번째 피연산자를 설정합니다.
        새로운 숫자가 입력되거나 연산자 버튼이 눌렸을 때 호출됩니다.

        Args:
            operand (float): 첫 번째 피연산자 값.
        """
        self.operand1 = operand

    def set_operator(self, operator):
        """
        수행할 연산자를 설정합니다.
        +, -, *, / 중 하나의 값이 할당됩니다.

        Args:
            operator (str): 수행할 연산자 (+, -, *, /).
        """
        self.operator = operator

    def calculate(self, operand2):
        """
        현재 설정된 연산자와 두 번째 피연산자를 사용하여 실제 계산을 수행합니다.

        Args:
            operand2 (float): 두 번째 피연산자 값.

        Returns:
            float: 계산 결과.

        Raises:
            ZeroDivisionError: 나누기 연산 시 두 번째 피연산자가 0인 경우 발생합니다.
        """
        if self.operand1 is None or self.operator is None:
            return operand2
        if self.operator == '+':
            return self.operand1 + operand2
        elif self.operator == '-':
            return self.operand1 - operand2
        elif self.operator == '*':
            return self.operand1 * operand2
        elif self.operator == '/':
            if operand2 == 0:
                raise ZeroDivisionError
            return self.operand1 / operand2
        return operand2

    def negate(self, operand):
        """
        주어진 숫자의 부호를 반전시킵니다. (양수를 음수로, 음수를 양수로)

        Args:
            operand (float): 부호를 반전할 숫자.

        Returns:
            float: 부호가 반전된 숫자.
        """
        return -operand

    def to_percentage(self, operand):
        """
        주어진 숫자를 백분율로 변환합니다. (100으로 나눔)

        Args:
            operand (float): 백분율로 변환할 숫자.

        Returns:
            float: 백분율 값.
        """
        return operand / 100.0

class Calculator(QWidget):
    """
    PyQt5를 이용하여 GUI 기반의 계산기 위젯을 구현하는 클래스입니다.
    화면 구성, 사용자 입력 처리, 결과 표시 등의 역할을 담당합니다.
    """
    def __init__(self):
        """
        Calculator 클래스의 생성자입니다.
        UI를 초기화하고, 계산 로직 객체를 생성하며, 입력 중 상태 플래그를 초기화합니다.
        """
        super().__init__()
        self.calc = CalculatorLogic()  # 계산 로직 객체 생성
        self.is_typing = False        # 현재 숫자 버튼을 누르고 있는지 여부를 나타내는 플래그
        self.initUI()

    def initUI(self):
        """
        계산기 UI를 초기화하고 화면에 표시합니다.
        출력 창(QLineEdit), 버튼 레이아웃(QGridLayout), 전체 레이아웃(QVBoxLayout) 등을 설정합니다.
        """
        # 출력 창 설정
        self.display = QLineEdit('0')
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setStyleSheet('QLineEdit { background-color: black; color: white; border: none; padding: 15px; }') # 폰트 크기 제거
        font = QFont()
        font.setPointSize(60)
        self.display.setFont(font) # 초기 폰트 설정
        # 버튼 레이아웃 설정
        grid = QGridLayout()
        grid.setSpacing(12)  # 버튼 사이 간격 설정

        # 버튼 데이터: (텍스트, 행, 열, 행 병합, 열 병합, 배경색, 글자색, *추가 스타일)
        buttons_data = [
            ('AC', 0, 0, 1, 1, '#a9a9a9', 'black'),
            ('+/-', 0, 1, 1, 1, '#a9a9a9', 'black'),
            ('%', 0, 2, 1, 1, '#a9a9a9', 'black'),
            ('/', 0, 3, 1, 1, '#ffa500', 'white'),
            ('7', 1, 0, 1, 1, '#333333', 'white'),
            ('8', 1, 1, 1, 1, '#333333', 'white'),
            ('9', 1, 2, 1, 1, '#333333', 'white'),
            ('*', 1, 3, 1, 1, '#ffa500', 'white'),
            ('4', 2, 0, 1, 1, '#333333', 'white'),
            ('5', 2, 1, 1, 1, '#333333', 'white'),
            ('6', 2, 2, 1, 1, '#333333', 'white'),
            ('-', 2, 3, 1, 1, '#ffa500', 'white'),
            ('1', 3, 0, 1, 1, '#333333', 'white'),
            ('2', 3, 1, 1, 1, '#333333', 'white'),
            ('3', 3, 2, 1, 1, '#333333', 'white'),
            ('+', 3, 3, 1, 1, '#ffa500', 'white'),
            ('0', 4, 0, 1, 2, '#333333', 'white', 'left', 25),  # 0 버튼은 왼쪽 정렬 및 패딩 추가
            ('.', 4, 2, 1, 1, '#333333', 'white'),
            ('=', 4, 3, 1, 1, '#ffa500', 'white')
        ]

        # 버튼 생성 및 레이아웃에 추가
        for text, row, col, row_span, col_span, bg_color, color, *extra in buttons_data:
            button = QPushButton(text)
            style = f'QPushButton {{ background-color: {bg_color}; color: {color}; font-size: 32px; border-radius: 35px; min-height: 70px; }} QPushButton:pressed {{ background-color: {"#808080" if bg_color == "#a9a9a9" else "#cc8400" if bg_color == "#ffa500" else "#555555"}; }}'
            if extra:
                if 'left' in extra:
                    style += ' QPushButton { text-align: left; padding-left: 25px; }'
            button.setStyleSheet(style)
            button.clicked.connect(self.button_clicked)  # 버튼 클릭 시 button_clicked 메서드 호출
            grid.addWidget(button, row, col, row_span, col_span)

        # 전체 레이아웃 설정
        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(grid)
        vbox.setContentsMargins(10, 10, 10, 10)  # 전체 레이아웃 여백 설정
        self.setLayout(vbox)

        # 윈도우 스타일 및 속성 설정
        self.setStyleSheet('QWidget { background-color: black; }')  # 배경색 설정
        self.setWindowTitle('계산기')
        self.setGeometry(300, 300, 350, 500)  # 창 위치 및 크기 설정
        self.show()  # 윈도우를 화면에 표시

    def _format_with_commas(self, text):
        """
        주어진 숫자 문자열에 세 자리마다 콤마를 추가합니다.

        Args:
            text (str): 콤마를 추가할 숫자 문자열.

        Returns:
            str: 콤마가 추가된 숫자 문자열.
        """
        if '.' in text:
            integer_part, decimal_part = text.split('.')
            try:
                formatted_integer = locale.format_string("%d", int(integer_part), grouping=True)
                return f"{formatted_integer}.{decimal_part}"
            except ValueError:
                return text  # 정수 부분이 유효하지 않으면 원래 텍스트 반환
        else:
            try:
                formatted_integer = locale.format_string("%d", int(text), grouping=True)
                return formatted_integer
            except ValueError:
                return text  # 정수 부분이 유효하지 않으면 원래 텍스트 반환
    
    def _adjust_font_size(self, text):
        font = self.display.font()
        initial_font_size = 60
        min_font_size = 12  # 너무 작아지는 것을 방지하기 위한 최소 크기
        font.setPointSize(initial_font_size)

        available_width = self.display.width() - 20  # 좌우 여백 고려
        text_width = self.display.fontMetrics().width(text)

        if text_width > available_width:
            # 텍스트가 위젯 너비를 얼마나 초과하는지 비율 계산
            overflow_ratio = available_width / text_width

            # 초기 폰트 크기에 비율을 곱하여 새로운 폰트 크기 계산
            new_font_size = int(initial_font_size * overflow_ratio * 0.9) # 약간의 여유 공간을 위해 0.9 곱함
            if new_font_size < min_font_size:
                new_font_size = min_font_size  # 최소 폰트 크기 보장

            font.setPointSize(new_font_size)

        self.display.setFont(font)       
    
    def update_display(self, value):
        """
        계산 결과를 화면에 표시하고, 결과가 길어질 경우 폰트 크기를 조정하며, 숫자에 콤마를 추가합니다.

        Args:
            value (float or str): 화면에 표시할 값.
        """
        formatted_value = self.format_output(value)  # 결과 포맷팅
        text_with_commas = self._format_with_commas(formatted_value) # 콤마 추가
        self.display.setText(text_with_commas)
        self._adjust_font_size(text_with_commas)  # 폰트 크기 조정

    def format_output(self, value):
        """
        계산 결과를 적절한 형태로 포맷팅합니다.
        소수점 아래 불필요한 0을 제거하고, 정수 형태일 경우 소수점을 표시하지 않습니다.

        Args:
            value (float or int): 포맷팅할 값.

        Returns:
            str: 포맷팅된 문자열.
        """
        if isinstance(value, float):
            if abs(value - round(value)) < 1e-7:  # 정수와 거의 같은 경우
                return str(int(round(value)))
            else:
                return "{:.6f}".format(value).rstrip('0').rstrip('.')  # 소수점 아래 0 제거
        return str(value)
    
    def button_clicked(self):
        """
        버튼이 클릭되었을 때 호출되는 메서드입니다.
        클릭된 버튼의 텍스트에 따라 숫자 입력, 연산자 설정, 계산 수행 등의 동작을 처리합니다.
        """
        sender = self.sender()         # 클릭된 버튼 객체 가져오기
        button_text = sender.text()   # 클릭된 버튼의 텍스트 가져오기

        # 숫자 버튼 클릭 처리
        if button_text.isdigit():
            current_text = self.display.text().replace(',', '') # 기존 콤마 제거
            if current_text == '0' and button_text == '0':
                return  # '0'이 이미 표시되어 있고 '0'을 다시 누르면 무시
            if not self.is_typing or current_text == '0':
                self.display.setText(button_text)  # 처음 입력이거나 화면이 '0'일 경우 덮어쓰기
            else:
                self.display.setText(current_text + button_text)  # 기존 숫자에 추가 (콤마 없이)
            self.is_typing = True  # 숫자 입력 중 상태로 변경
            formatted_text = self._format_with_commas(self.display.text()) # 콤마 포맷팅 적용
            self.display.setText(formatted_text)
            self._adjust_font_size(formatted_text) # 입력 중 폰트 크기 조정
        # 소수점 버튼 클릭 처리
        elif button_text == '.':
            if '.' not in self.display.text():  # 이미 소수점이 없으면 추가
                self.display.setText(self.display.text() + '.')
                self.is_typing = True
                self._adjust_font_size(self.display.text()) # 입력 중 폰트 크기 조정
        # AC (All Clear) 버튼 클릭 처리
        elif button_text == 'AC':
            self.calc.reset()          # 계산 로직 초기화
            self.display.setText('0')  # 화면 초기화
            self.is_typing = False
            self._adjust_font_size(self.display.text()) # 초기 상태 폰트 크기 조정
        # +/- (부호 변경) 버튼 클릭 처리
        elif button_text == '+/-':
            try:
                current_value = float(self.display.text().replace(',', '')) # 콤마 제거 후 float 변환
                self.update_display(self.calc.negate(current_value))
            except ValueError:
                self.display.setText('Error')
                self.is_typing = False
                self._adjust_font_size(self.display.text()) # 오류 메시지 폰트 크기 조정
        # % (퍼센트) 버튼 클릭 처리
        elif button_text == '%':
            try:
                current_value = float(self.display.text().replace(',', '')) # 콤마 제거 후 float 변환
                self.update_display(self.calc.to_percentage(current_value))
            except ValueError:
                self.display.setText('Error')
                self.is_typing = False
                self._adjust_font_size(self.display.text()) # 오류 메시지 폰트 크기 조정
        # 사칙연산 버튼 클릭 처리
        elif button_text in ['+', '-', '*', '/']:
            try:
                operand = float(self.display.text().replace(',', '')) # 콤마 제거 후 float 변환
                self.calc.set_operand(operand)      # 첫 번째 피연산자 설정
                self.calc.set_operator(button_text)  # 연산자 설정
                self.is_typing = False
            except ValueError:
                self.display.setText('Error')
                self.is_typing = False
                self._adjust_font_size(self.display.text()) # 오류 메시지 폰트 크기 조정
        # = (등호) 버튼 클릭 처리
        elif button_text == '=':
            try:
                operand = float(self.display.text().replace(',', '')) # 콤마 제거 후 float 변환
                result = self.calc.calculate(operand)  # 계산 수행
                self.update_display(result)           # 결과 화면에 표시
                self.is_typing = False
            except ValueError:
                self.display.setText('Error')
                self.is_typing = False
                self._adjust_font_size(self.display.text()) # 오류 메시지 폰트 크기 조정
            except ZeroDivisionError:
                self.display.setText('Error: Division by zero')
                self.is_typing = False
                self._adjust_font_size(self.display.text()) # 오류 메시지 폰트 크기 조정

if __name__ == '__main__':
    # 현재 로케일 설정 (콤마가 제대로 표시되도록)
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # UTF-8 로케일 시도

    app = QApplication([])
    calc_ui = Calculator()
    app.exec_()