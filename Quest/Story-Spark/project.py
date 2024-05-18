from llmware.models import ModelCatalog
from llmware.prompts import Prompt

def generate_story_ideas(model_name):
  model = Prompt().load_model(model_name)
  current_story = ""

  while True:
    # Initial story generation (run only once)
    if not current_story:
      genre = input("Enter story genre (e.g., fantasy, sci-fi): ")
      character = input("Describe the main character (briefly): ")
      setting = input("Describe the story setting (briefly): ")
      conflict = input("Describe the initial conflict the character faces: ")

    # Build the user prompt
    user_input = f"Write a suspenseful and character-driven continuation of the story:\n{current_story}" \
                 f"\nGenre: {genre}\nCharacter: {character}\nSetting: {setting}\nConflict: {conflict}"

    output = model.prompt_main(user_input,
                                prompt_name="generate_story",
                                temperature=0.7)
    story = output["llm_response"].strip("\n")

    # Update the current story with the generated continuation
    current_story += story + "\n\n"

    # Print generated story with a separator
    print("*** Generated Story ***")
    print(current_story)
    print("*** End of Generated Story ***")

    user_feedback = input("Do you want to continue the story (y/n) or are you happy with this length? ")

    # Exit loop if user chooses not to continue
    if user_feedback.lower() == 'n':
      break

# Run the program if executed directly
if __name__ == "__main__":
  model_name = "phi-3-gguf"
  generate_story_ideas(model_name)
