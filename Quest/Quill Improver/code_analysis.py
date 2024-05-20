from llmware import Retriever

def extract_code_snippets(code):
  """
  Breaks down code into well-defined snippets (functions, classes, etc.).

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

def analyze_code(code, knowledge_base):
  """
  Analyzes user code using LLMWare's retriever and suggests improvements.

  Args:
      code (str): The user-provided code string.
      knowledge_base (dict): The knowledge base containing code examples and best practices.

  Returns:
      list: A list of findings (potential issues and optimization suggestions).
  """

  findings = []
  snippets = extract_code_snippets(code)
  retriever = Retriever(knowledge_base)

  for snippet in snippets:
    # Use LLMWare retriever to find similar snippets from the knowledge base
    similar_code, comments = retriever.get_passage(snippet)

    # Analyze retrieved comments for improvement suggestions
    for comment in comments:
      if "complexity" in comment:  # Example check for code complexity
        findings.append(f"Potential complexity issue in code snippet: {snippet}")
      elif "style" in comment:  # Example check for coding style violations
        findings.append(f"Potential coding style violation in code snippet: {snippet}")
      # Add more checks based on your knowledge base and coding standards
      # You can also implement custom logic to prioritize findings

  return findings
