import os
import re
import argparse
from llmware import Retriever, RatingFunction
import warnings

def extract_code_snippets(code):
    """
    Breaks down code into well-defined snippets (functions, classes, etc.)

    Args:
        code (str): The user-provided code string.

    Returns:
        list: A list of code snippets extracted from the input.
    """

    # Improved regular expression for robust snippet extraction
    snippet_regex = r"""
    (?ix)
    (?:  # Function definitions
        def\s+([^\s\(]+)\(.*?\):\s*.*?(?<!\\)\n.*?^}
    |   # Class definitions
        class\s+([^\s\(]+)\(.*?\):\s*.*?(?<!\\)\n.*?^}
    |   # Conditional statements (if, else, elif)
        if\s.*?:\s*.*?(?<!\\)\n.*?^fi|
        else\s.*?:\s*.*?(?<!\\)\n.*?^fi|
        elif\s.*?:\s*.*?(?<!\\)\n.*?^fi
    |   # Loops (for, while)
        for\s.*?:\s*.*?(?<!\\)\n.*?^next|
        while\s.*?:\s*.*?(?<!\\)\n.*?^done
    |   # Try-except blocks
        try\s*.*?:\s*.*?(?<!\\)\n.*?^except|
        except\s.*?:\s*.*?(?<!\\)\n.*?^finally
    )
    """

    snippets = re.findall(snippet_regex, code, flags=re.DOTALL)
    return snippets

def analyze_code(code, knowledge_base, rating_function=None):
    """
    Analyzes user code using LLMWare's retriever and suggests improvements.

    Args:
        code (str): The user-provided code string.
        knowledge_base (dict): The knowledge base containing code examples and best practices.
        rating_function (callable, optional): A function to prioritize relevant responses.

    Returns:
        list: A list of findings (potential issues and optimization suggestions).
    """

    findings = []
    snippets = extract_code_snippets(code)
    retriever = Retriever(knowledge_base)

    for snippet in snippets:
        # Use LLMWare retriever to find similar snippets from the knowledge base
        similar_code, comments = retriever.get_passage(snippet, rating_function=rating_function)

        # Analyze retrieved comments for improvement suggestions
        for comment in comments:
            if "complexity" in comment:  # Example check for code complexity
                findings.append(f"Potential complexity issue in code snippet: {snippet}")
            elif "style" in comment:  # Example check for coding style violations
                findings.append(f"Potential coding style violation in code snippet: {snippet}")
            # Add more checks based on your knowledge base and coding standards

    return findings

def load_knowledge_base(filepath):
    """
    Loads the code quality knowledge base from a file.

    Args:
        filepath (str): The path to the knowledge base file.

    Returns:
        dict: The loaded knowledge base.
    """

    knowledge_base = {}
    if not os.path.exists(filepath):
        warnings.warn(f"Knowledge base file not found: {filepath}. Using an empty knowledge base.")
    else:
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    code_snippet, comment = line.strip().split(':', 1)
                    knowledge_base[code_snippet.strip()] = comment.strip()
        except FileNotFoundError:
            warnings.warn(f"Error opening knowledge base file: {filepath}. Using an empty knowledge base.")
        except ValueError:  # Handle malformed lines in the knowledge base
            warnings.warn(f"Error parsing knowledge base file {filepath}. Skipping invalid lines.")

    return knowledge_base

def main():
    """
    The main entry point for the application.
    """

    parser = argparse.ArgumentParser(description="AI-powered code quality checker")
    parser.add_argument("-c", "--code", type=str, required=True,
                        help="The code to analyze (provide as a string or path to a file).")
    parser.add_argument("-k", "--knowledge_base", type=str, required=True,
                        help="The path to the knowledge base file.", default="knowledge_base.txt")
    args = parser.parse_args()

    knowledge_base = load_knowledge_base(args.knowledge_base)
    findings = analyze_code(args.code, knowledge_base)

    if findings:
        print("Code Quality Findings:")
        for finding in findings:
            print(f"- {finding}")
    else:
        print("Your code appears to be well-structured!")


if __name__ == "__main__":
    main()