# main.py
import sys
from PyQt5.QtWidgets import QApplication
from b import ModernDashboard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = ModernDashboard()
    dashboard.show()
    sys.exit(app.exec_())
