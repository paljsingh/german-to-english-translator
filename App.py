from functools import partial

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow
from googletrans import Translator as GoogleTranslator
from googletrans.models import Translated


class App:

    def __init__(self):
        super().__init__()

        # window properties...
        self.app = QtWidgets.QApplication([])

        self.translator_window = G2ETranslator()
        self.translator = self.translator_window.get_widget()

    def run(self):
        self.app.exec_()


class G2ETranslator(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, self.maximumWidth(), self.maximumHeight())

        # load ui file.
        loader = QUiLoader()
        file = QFile("translator.ui")
        file.open(QFile.ReadOnly)
        self.translator_widget = loader.load(file, self)
        file.close()

        self.gtranslator = GoogleTranslator()

        # setup buttons.
        self.translator_widget.translate_button.setEnabled(False)

        # setup event handlers.
        self.translator_widget.german_entry.textChanged.connect(partial(self.validate))

        # self.translator_widget.german_entry.enterEvent.connect(partial(self.translate))
        self.translator_widget.translate_button.clicked.connect(partial(self.translate))

        self.show()

    def validate(self):
        """
        Enable Translate button if text edit box has any text.
        """
        if len(self.translator_widget.german_entry.toPlainText()) > 0:
            self.translator_widget.translate_button.setEnabled(True)

    def translate(self, *args, **kvargs):
        """
        Translate German to English.
        """
        text_phrase = self.translator_widget.german_entry.toPlainText()

        english_translated = self.gtranslator.translate(text=text_phrase, src='de', dest='en')

        self.translator_widget.english_entry.setText(english_translated.text)

    def get_widget(self):
        return self.translator_widget


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    App().run()
