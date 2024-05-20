# story_generator.py
from llmware.models import ModelCatalog
from llmware.prompts import Prompt

def generate_story_ideas(model_name, genre, character, setting, conflict, continue_story=False, current_story=""):
    model = Prompt().load_model(model_name)
    if not continue_story:
        current_story = ""

    iterations = 4  # Number of segments to generate before concluding

    # Generate the main body of the story
    for i in range(iterations - 1):  # Save the last iteration for the conclusion
        user_input = f"Continue the story:\n{current_story}" \
                     f"\nGenre: {genre}\nCharacter: {character}\nSetting: {setting}\nConflict: {conflict}"
        output = model.prompt_main(user_input, prompt_name="generate_story", temperature=0.7)
        story_segment = output["llm_response"].strip("\n")
        current_story += story_segment + "\n\n"

    # Generate a conclusive ending
    conclusion_prompt = f"Conclude the story with a meaningful ending:\n{current_story}" \
                        f"\nGenre: {genre}\nCharacter: {character}\nSetting: {setting}\nConflict: {conflict}"
    output = model.prompt_main(conclusion_prompt, prompt_name="generate_story", temperature=0.7)
    conclusion_segment = output["llm_response"].strip("\n")
    current_story += conclusion_segment + "\n\n"

    return current_story
