import sys
import re
import time
import json
from llmware.prompts import Prompt

def run_test(model_name, query):
    try:
        print(f"\n > Loading model '{model_name}'", file=sys.stderr)
        prompter = Prompt().load_model(model_name)
        start_time = time.time()
        print(f"query - {query}", file=sys.stderr)
        response = prompter.prompt_main(query,temperature=0.30, max_output=800)
        time_taken = round(time.time() - start_time, 2)
        llm_response = re.sub("[\n\n]", "\n", response['llm_response'])
        print(f"llm_response - {llm_response}", file=sys.stderr)
        print(f"time_taken - {time_taken}", file=sys.stderr)
        return llm_response, time_taken
    except Exception as e:
        print(f"Error during model execution: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        query = sys.argv[1] if len(sys.argv) > 1 else "Cool names for kids"
        model_name = "phi-3-gguf"
        result, time_taken = run_test(model_name, query)
        # Print the result as a JSON object
        print(json.dumps({'llm_response': result, 'time_taken': time_taken}))
    except Exception as e:
        print(f"Error in main: {str(e)}", file=sys.stderr)
        sys.exit(1)
