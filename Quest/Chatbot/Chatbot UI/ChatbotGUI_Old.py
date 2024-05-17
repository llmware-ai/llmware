import tkinter as tk
from tkinter import scrolledtext
from llmware.models import ModelCatalog
from llmware.prompts import Prompt

class ChatbotUI:
	def __init__(self, root):
		self.root = root
		self.root.title("LLMWARE Chatbot Interface")

		self.chat_frame = tk.Frame(root)
		self.chat_frame.pack(expand=True, fill=tk.BOTH)

		self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD)
		self.chat_display.pack(expand=True, fill=tk.BOTH)

		self.input_frame = tk.Frame(root, bg="lightgray")
		self.input_frame.pack(side=tk.BOTTOM, fill=tk.X)

		self.input_entry = tk.Entry(self.input_frame)
		self.input_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

		self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
		self.send_button.pack(side=tk.RIGHT)

		self.previous_sender = None

def send_message():
    user_input = entry.get()
    chat_history.insert(tk.END, f"You: {user_input}\n")
    chat_history.yview(tk.END)  # Scroll to the bottom
    entry.delete(0, tk.END)  # Clear the entry field
    
    # Get bot response
    output = model.prompt_main(user_input, prompt_name="default_with_context", temperature=0.30)
    bot_response = output["llm_response"].strip("\n")
    
    # Display bot response
    chat_history.insert(tk.END, f"Bot: {bot_response}\n\n")
    chat_history.yview(tk.END)  # Scroll to the bottom

# Create main window
root = tk.Tk()
root.title("LLMWARE Chatbot Interface")

# Load the model
model_name = "phi-3-gguf"
model = Prompt().load_model(model_name)

# Create chat history window
chat_history = tk.Text(root, width=50, height=15)
chat_history.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

# Create entry field for user input
entry = tk.Entry(root, width=40)
entry.grid(row=1, column=0, padx=10, pady=10)

# Create send button
send_button = tk.Button(root, text="Send", width=8, command=send_message)
send_button.grid(row=1, column=1, padx=10, pady=10)

# Start the GUI event loop
root.mainloop()