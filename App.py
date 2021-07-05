import os
from functools import partial

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QFileDialog
from googletrans import Translator as GoogleTranslator


class App:

    def __init__(self):
        super().__init__()

        # window properties...
        self.app = QtWidgets.QApplication([])
        self.app.setWindowIcon(QIcon('images/logo.png'))

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

        # maintain file handles to read de/en corpuses.
        self.de_fh = None
        self.en_fh = None

        self.gtranslator = GoogleTranslator()

        # setup buttons.
        self.translator_widget.translate_button.setEnabled(False)

        # setup event handlers.
        self.translator_widget.german_input.textChanged.connect(self.validate)
        self.translator_widget.translate_button.clicked.connect(self.on_translate_click)

        self.translator_widget.german_corpus_button.clicked.connect(partial(self.select_corpus, 'de'))
        self.translator_widget.english_corpus_button.clicked.connect(partial(self.select_corpus, 'en'))

        self.translator_widget.corpus_index_spinbox.valueChanged.connect(self.on_spinbox_change)
        self.show()

    def validate(self):
        """
        Enable Translate button if text edit box has any text.
        """
        if len(self.translator_widget.german_input.toPlainText()) > 0:
            set_state = True
        else:
            set_state = False
        self.translator_widget.translate_button.setEnabled(set_state)

    def on_translate_click(self):
        """
        Translate German to English.
        """
        text_phrase = self.translator_widget.german_input.toPlainText()

        english_translated = self.gtranslator.translate(text=text_phrase, src='de', dest='en')

        self.translator_widget.english_output.setPlainText(english_translated.text)

    def select_corpus(self, language_code: str):
        filters_str = '{} files (*.{})'.format(language_code.title(), language_code.lower())
        file_path, filter_str = QFileDialog().getOpenFileName(
            None,
            caption="Select {} corpus...".format(language_code),
            filter=filters_str
        )
        if not file_path:
            return
        fh = open(file_path, 'r', encoding='utf-8')
        if language_code == 'de':
            # close any previously opened file handle
            if self.de_fh:
                self.de_fh.close()
            self.de_fh = fh

            # set spinner box max value.
            line_count = sum([1 for x in fh.readlines()])       # noqa
            self.translator_widget.corpus_index_spinbox.setMaximum(line_count)

            # set textbox to show selected corpus.
            self.translator_widget.german_corpus_filename.setText(os.path.basename(file_path))
        elif language_code == 'en':
            # close any previously opened file handle
            if self.en_fh:
                self.en_fh.close()
            self.en_fh = fh
            self.translator_widget.english_corpus_filename.setText(os.path.basename(file_path))

    def select_phrase_from_corpus(self, language_code: str, index: int):
        if language_code == 'de':
            fh = self.de_fh
        elif language_code == 'en':
            fh = self.en_fh
        else:
            return

        if not fh:
            return

        fh.seek(0)
        for i, phrase in enumerate(fh.readlines(), 1):
            if i == index:
                return phrase

    def on_spinbox_change(self, value: int):
        phrase_german = self.select_phrase_from_corpus('de', value)
        if not phrase_german:
            return

        # get english phrase from corpus, and display it for comparison.
        phrase_english_from_corpus = self.select_phrase_from_corpus('en', value)
        self.translator_widget.english_corpus_phrase.setPlainText(phrase_english_from_corpus)

        # set german input box.
        self.translator_widget.german_input.setPlainText(phrase_german)

        # emit translate button event
        self.translator_widget.translate_button.animateClick()

    def get_widget(self):
        return self.translator_widget


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    App().run()
