## Quill Improver: AI-powered Code Quality Checker with LLMWare

**Quill Improver** leverages the power of LLMWare, an open-source AI framework developed by AI Bloks, to assist developers in writing cleaner and more maintainable code. It utilizes a customizable knowledge base to identify potential issues and suggest improvements in your code.

### Purpose

Quill Improver helps developers:

- **Enhance code quality:** Identify potential issues like complexity violations, style inconsistencies, and other areas for improvement based on your knowledge base.
- **Write code for maintainability:** By focusing on best practices and clear structure, Quill Improver guides you towards writing code that's easier to understand and modify in the future.
- **Boost development efficiency:** Automated suggestions expedite the review process and highlight areas that might need attention, saving you valuable development time.

### Installation

**Prerequisites:**

- Python 3.x
- `pip` package installer

**Steps:**

1. Clone this repository or download the project files.
2. Open a terminal in the project directory.
3. Install the required dependencies using `pip install -r requirements.txt`.

### Usage

1. **Create a knowledge base:** Build a text file named `code_quality_knowledge.txt` in the project directory. Each line should follow the format:

   ```
   Code Snippet : Improvement Comment
   ```

   - Replace `Code Snippet` with an example of code that demonstrates the potential issue.
   - Replace `Improvement Comment` with a suggestion for improvement or best practice related to the code snippet.

2. Run the application using:

   ```bash
   python main.py -c "your_code_here" -k "code_quality_knowledge.txt"
   ```

   - Replace `"your_code_here"` with the code you want to analyze (either as a string or the path to a file containing the code).
   - Replace `"code_quality_knowledge.txt"` with the actual filename of your knowledge base file if it's named differently.

3. The script will analyze the provided code and display findings or a message indicating well-structured code if no issues are detected.

**Note:** This is a basic implementation. For more advanced analysis, consider expanding the knowledge base and potential checks.

### Contributing

We welcome contributions! Feel free to submit pull requests for bug fixes, feature enhancements, or improved knowledge base examples. Make sure to follow the existing code style and documentation practices.

### License

This project is licensed under the MIT License. See the `LICENSE` file for details.

### See it in action!

A video demonstration of Quill Improver is available on YouTube: