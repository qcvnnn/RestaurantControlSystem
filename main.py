import sys
from PyQt5.QtWidgets import QApplication
from windows.windows import BaseWindow


if __name__ == "__main__":
    # try:
    app = QApplication(sys.argv)
    base_window = BaseWindow()
    sys.exit(app.exec_())
    # except Exception as e:
    #     print(e)