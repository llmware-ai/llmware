import sys
import json
import os
from PyQt6 import QtWidgets, QtGui, QtCore, uic
from llmware.prompts import Prompt
from llmware.models import ModelCatalog
import unittest
import threading

class CodeGeneratorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('app.ui', self)
        self.model = None
        self.test_case_file = ""
        self.initUI()
        self.load_model_in_background()

    def initUI(self):
        self.generate_button.clicked.connect(self.on_generate_code_clicked)
        self.browse_button.clicked.connect(self.browse_test_case_file)

    def browse_test_case_file(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("JSON files (*.json)")
        if file_dialog.exec():
            self.test_case_file = file_dialog.selectedFiles()[0]
            self.test_case_input.setText(self.test_case_file)

    def load_model_in_background(self):
        self.output_text.append("Loading Model in Background...\n")
        threading.Thread(target=self.load_model).start()

    def load_model(self):
        model_name = "bling-phi-3-gguf"
        self.model = ModelCatalog().load_model(model_name, temperature=0.7, max_output=150)
        self.display_text("Model loaded successfully.\n")

    def on_generate_code_clicked(self):
        prompt = self.prompt_input.text()
        if not prompt:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a question.")
            return
        if self.model is None:
            QtWidgets.QMessageBox.warning(self, "Model Loading", "The model is still loading, please wait.")
            return
        if not self.test_case_file:
            QtWidgets.QMessageBox.warning(self, "Test Case File Missing", "Please select a test case file.")
            return
        threading.Thread(target=self.generate_code, args=(prompt,)).start()

    def generate_code(self, prompt):
        self.display_text(f"Generating code for prompt: {prompt}\n")
        generate_code(self.model, prompt, self.display_text)
        self.run_tests()

    def run_tests(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneratedFunction)
        result = unittest.TextTestRunner(verbosity=2).run(suite)

        if result.wasSuccessful():
            self.display_text("All test cases passed.\n")
        else:
            self.display_text(f"Test case failed: regenerating code and retrying...\n")
            self.display_text(f"{result.failures[0]}\n")
            generate_code(self.model, self.prompt_input.text(), self.display_text, result.failures[0])
            self.run_tests()

    def display_text(self, text):
        QtCore.QMetaObject.invokeMethod(self.output_text, "append", QtCore.Q_ARG(str, text))

def generate_code(model, prompt=None, display_text=None, failed_case=None):
    base_prompt = f"Create a python function named run which does: {prompt}. Output only code."
    if failed_case:
        base_prompt += f" Error : {failed_case}."
        print(base_prompt)
    response = model.inference(base_prompt)
    with open("c.py", "w") as f:
        if display_text:
            display_text(f"\nTest inference - response: {response}")
        code = response['llm_response']
        formatted_code = code.replace("\r\n", "\n")
        if display_text:
            display_text(f"Generated Code: \n {formatted_code}")
        f.write(formatted_code)

def load_test_cases(filename):
    with open(filename, 'r') as f:
        test_cases = json.load(f)
    return test_cases['test_cases']

class TestGeneratedFunction(unittest.TestCase):
    def setUp(self):
        global run
        from c import run

    def test_generated_code(self):
        test_cases = load_test_cases(mainWin.test_case_file)
        for case in test_cases:
            inputs = case['inputs']
            expected_output = case['expected_output']
            with self.subTest(inputs=inputs, expected_output=expected_output):
                result = run(*inputs)
                print(f"Testing case {inputs} expecting {expected_output}: got {result}")
                if result == expected_output:
                    print(f"{case} OK")
                else:
                    self.fail(f"{case} Test case failed.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = CodeGeneratorApp()
    mainWin.show()
    sys.exit(app.exec())
