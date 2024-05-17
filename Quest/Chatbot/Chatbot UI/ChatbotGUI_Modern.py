import customtkinter as ctk
from tkinter import LEFT, RIGHT, BOTH, X, Y, END, WORD
from llmware.prompts import Prompt


class Chatbot:

    def __init__(self, root, model):
        self.model = model
        self.root = root
        self.root.title("LLMWARE Chatbot Interface")
        self.root.geometry("400x600")
        self.root.overrideredirect(True)  # Remove default title bar

        ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
        ctk.set_default_color_theme(
            "dark-blue"
        )  # Themes: blue (default), dark-blue, green

        # Create custom title bar
        self.title_bar = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.title_bar.pack(fill=X)

        self.title_label = ctk.CTkLabel(
            self.title_bar, text="LLMWARE Chatbot Interface", anchor="w", padx=10
        )
        self.title_label.pack(side=LEFT, fill=Y)

        self.minimize_button = ctk.CTkButton(
            self.title_bar, text="_", width=30, command=self.minimize_window
        )
        self.minimize_button.pack(side=RIGHT, padx=(0, 5), pady=(5, 0))

        self.close_button = ctk.CTkButton(
            self.title_bar, text="X", width=30, command=self.close_window
        )
        self.close_button.pack(side=RIGHT, padx=(0, 5), pady=(5, 0))

        self.chat_frame = ctk.CTkFrame(root)
        self.chat_frame.pack(expand=True, fill=BOTH, padx=10, pady=(0, 10))

        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap=WORD,
            state="disabled",
            fg_color="#333333",
            text_color="white",
        )
        self.chat_display.pack(expand=True, fill=BOTH, padx=10, pady=10)

        self.input_frame = ctk.CTkFrame(root)
        self.input_frame.pack(side=ctk.BOTTOM, fill=X, padx=10, pady=10)

        self.input_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Type your message here..."
        )
        self.input_entry.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))

        self.send_button = ctk.CTkButton(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side=RIGHT)

        self.previous_sender = None  # To keep track of the previous message sender

        self.make_window_draggable()

    def make_window_draggable(self):
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        new_x = self.root.winfo_x() + deltax
        new_y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{new_x}+{new_y}")

    def stop_move(self, event):
        self.x = None
        self.y = None

    def minimize_window(self):
        self.root.iconify()

    def close_window(self):
        self.root.destroy()

    def send_message(self):
        message = self.input_entry.get().strip()
        if message != "":
            self.chat_display.configure(state="normal")
            if self.previous_sender == "Bot":
                self.chat_display.insert(END, "\n\n")
            self.chat_display.insert(END, "You: " + message + "\n")
            self.chat_display.insert(
                END, "Bot: " + self.generate_bot_response(message) + "\n\n"
            )
            self.chat_display.configure(state="disabled")
            self.chat_display.see(END)  # Scroll to the end
            self.input_entry.delete(0, END)
            self.previous_sender = "You"

    def generate_bot_response(self, user_message="Hi"):
        model = Prompt().load_model(self.model)

        output = model.prompt_main(
            user_message, prompt_name="default_with_context", temperature=0.30
        )
        bot_response = output["llm_response"].strip("\n")
        # bot_response = output["llm_response"].strip("\n").split("\n")[0]

        return bot_response


if __name__ == "__main__":
    root = ctk.CTk()
    app = Chatbot(root, "phi-3-gguf")
    root.mainloop()
