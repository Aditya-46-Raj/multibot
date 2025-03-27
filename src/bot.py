import os
import json
import requests
from fpdf import FPDF
from tkinter import *
from tkinter import font
from tkinter import filedialog

# Set up Gemini API (Replace 'YOUR_API_KEY' with your actual key)
API_KEY = 'YOUR_API_KEY'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Bot Presets
BOT_PRESETS = {
  "study partner": "Act as a helpful study companion, explaining concepts clearly.",
  "child": "Respond in a simple and friendly manner suitable for a child.",
  "coding": "Provide detailed programming help and explanations.",
  "story": "Create engaging and creative stories based on the input."
}

# Function to apply theme
def apply_theme(theme):
  if theme == "Light":
    win.tk_setPalette(background="#FFFFFF", foreground="#000000")
  elif theme == "Dark":
    win.tk_setPalette(background="#2C3E50", foreground="#FFFFFF")
  else:
    win.tk_setPalette(background=os.environ.get("SYSTEM_THEME", "#ECF0F1"))

# Function to change theme
def change_theme(choice):
  apply_theme(choice)

# Function to send user input to the Gemini API and display response
def send_message():
  user_input = input_text.get("1.0", END).strip()
  if not user_input:
    return
  
  selected_bot = bot_selector.get()
  prompt = BOT_PRESETS.get(selected_bot, "")
  
  data = {
    "contents": [{"parts": [{"text": f"{prompt}\n{user_input}"}]}]
  }
  headers = {"Content-Type": "application/json"}
  
  try:
    response = requests.post(API_URL, headers=headers, data=json.dumps(data))
    response_json = response.json()
    ai_response = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
    
    output_text.config(state=NORMAL)
    output_text.delete("1.0", END)
    insert_formatted_text(output_text, ai_response)
    output_text.config(state=DISABLED)
  except Exception as e:
    output_text.config(state=NORMAL)
    output_text.delete("1.0", END)
    output_text.insert(END, "Error: " + str(e))
    output_text.config(state=DISABLED)

# Function to insert formatted text
def insert_formatted_text(text_widget, text):
  bold_font = font.Font(text_widget, text_widget.cget("font"))
  bold_font.configure(weight="bold")
  
  parts = text.split("**")
  for i, part in enumerate(parts):
    if i % 2 == 1:
      text_widget.insert(END, part, ("bold",))
    else:
      text_widget.insert(END, part)
  
  text_widget.tag_configure("bold", font=bold_font)

# Function to save selected text to notes
# Function to save selected text to notes while keeping formatting
# Function to save selected text to notes while preserving markdown-style formatting
def save_notes():
    if not output_text.tag_ranges(SEL):
        return

    selected_text = output_text.get(SEL_FIRST, SEL_LAST)

    # Preserve markdown-style formatting for bold text
    bold_texts = []
    bold_ranges = output_text.tag_ranges("bold")

    for i in range(0, len(bold_ranges), 2):
        start, end = bold_ranges[i], bold_ranges[i + 1]
        if output_text.compare(start, "<=", SEL_LAST) and output_text.compare(end, ">=", SEL_FIRST):
            bold_text = output_text.get(start, end)
            bold_texts.append((bold_text, start, end))

    # Replace normal bold text with markdown-style **bold**
    for bold_text, start, end in bold_texts:
        if bold_text in selected_text:
            selected_text = selected_text.replace(bold_text, f"**{bold_text}**")

    # Insert formatted text into notes section with a line gap
    notes_text.insert(END, selected_text + "\n\n")

# Function to Export notes as a PDF
def save_final_notes():
  notes = notes_text.get("1.0", END).strip()
  if not notes:
    return
  
  file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[["PDF files", "*.pdf"]])
  if file_path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, notes)
    pdf.output(file_path)

# Function to Export Response as a PDF
def export_response():
  ai_response = output_text.get("1.0", END).strip()
  if not ai_response:
    return
  
  file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[["PDF files", "*.pdf"]])
  if file_path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, ai_response)
    pdf.output(file_path)

# Function to add a new bot preset
def add_bot_preset():
  new_preset_name = new_preset_name_entry.get().strip()
  new_preset_prompt = new_preset_prompt_entry.get().strip()
  if new_preset_name and new_preset_prompt:
    BOT_PRESETS[new_preset_name] = new_preset_prompt
    bot_menu['menu'].add_command(label=new_preset_name, command=lambda value=new_preset_name: bot_selector.set(value))
    new_preset_name_entry.delete(0, END)
    new_preset_prompt_entry.delete(0, END)

# UI Setup
win = Tk()
win.title("AI Chatbot")
win.state("zoomed")  # Start in fullscreen mode
apply_theme("System")  # Default to system theme

# Configure grid for dynamic resizing
win.columnconfigure(0, weight=1)
win.columnconfigure(1, weight=1)
win.rowconfigure(0, weight=1)

# Styling
frame_bg = "#ECF0F1"
border_color = "#BDC3C7"
button_bg = "#2980B9"
button_fg = "white"
text_font = ("Arial", 12)
button_font = ("Arial", 10, "bold")

# Main Frame for Resizable Layout
main_frame = Frame(win)
main_frame.pack(fill=BOTH, expand=True)
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

# Left Panel: User Input and Notes section
left_panel = Frame(main_frame, bg=frame_bg, padx=10, pady=10, bd=2, relief=RIDGE)
left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
left_panel.columnconfigure(0, weight=1)
left_panel.rowconfigure(1, weight=1)
left_panel.rowconfigure(3, weight=1)

Label(left_panel, text="Notes Section:", font=("Arial", 14, "bold"), bg=frame_bg).grid(row=0, column=0, sticky="w")
notes_text = Text(left_panel, wrap=WORD, font=text_font, bd=2, relief=SOLID, highlightbackground=border_color, highlightthickness=1)
notes_text.grid(row=1, column=0, sticky="nsew")

Label(left_panel, text="User Input:", font=("Arial", 14, "bold"), bg=frame_bg).grid(row=2, column=0, sticky="w")
input_text = Text(left_panel, wrap=WORD, font=text_font, bd=2, relief=SOLID, height=4, highlightbackground=border_color, highlightthickness=1)
input_text.grid(row=3, column=0, sticky="nsew")

# Button Frame for better alignment
button_frame_left = Frame(left_panel, bg=frame_bg)
button_frame_left.grid(row=4, column=0, sticky="ew", pady=5)
button_frame_left.columnconfigure(0, weight=1)
button_frame_left.columnconfigure(1, weight=0)

# Bot Selector inside Button Frame
bot_selector = StringVar(win)
bot_selector.set("study partner")  # Default selection
bot_menu = OptionMenu(button_frame_left, bot_selector, *list(BOT_PRESETS.keys()) + ["Add New Preset"], command=lambda choice: show_new_preset_fields(choice))
bot_menu.config(font=button_font, bg=button_bg, fg=button_fg, relief=RAISED, bd=3)
bot_menu.grid(row=0, column=0, sticky="e", padx=5)

# Send Button inside Button Frame
send_button = Button(button_frame_left, text="Send", command=send_message, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
send_button.grid(row=0, column=1, sticky="e", padx=5)

# Right Panel: AI Response Section
right_panel = Frame(main_frame, bg=frame_bg, padx=10, pady=10, bd=2, relief=RIDGE)
right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
right_panel.columnconfigure(0, weight=1)
right_panel.rowconfigure(1, weight=1)

Label(right_panel, text="AI Response:", font=("Arial", 14, "bold"), bg=frame_bg).grid(row=0, column=0, sticky="w")
output_text = Text(right_panel, wrap=WORD, state=DISABLED, font=text_font, bd=2, relief=SOLID, highlightbackground=border_color, highlightthickness=1)
output_text.grid(row=1, column=0, sticky="nsew")

# Button Frame for better alignment
button_frame_right = Frame(right_panel, bg=frame_bg)
button_frame_right.grid(row=2, column=0, sticky="e", pady=5)

final_notes_button = Button(button_frame_right, text="Export Response", command=save_final_notes, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
final_notes_button.pack(side=LEFT, padx=5)

save_button = Button(button_frame_right, text="Add to Notes", command=save_notes, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
save_button.pack(side=LEFT, padx=5)

# Buttons & Dropdown
button_frame = Frame(win, bg="#2C3E50")
button_frame.pack(fill=X, pady=10)

final_notes_button = Button(button_frame, text="Export Notes", command=save_final_notes, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
final_notes_button.pack(side=LEFT, padx=10, pady=5)


# Frame for new preset entry fields and button
new_preset_frame = Frame(button_frame, bg=frame_bg)
new_preset_frame.pack(side=LEFT, padx=10, pady=5)
new_preset_frame.pack_forget()  # Hide initially

# Entry fields for new bot preset
new_preset_name_entry = Entry(new_preset_frame, font=text_font, bd=2, relief=SOLID)
new_preset_name_entry.pack(side=LEFT, padx=10, pady=5)
new_preset_name_entry.insert(0, "Preset Name")

new_preset_prompt_entry = Entry(new_preset_frame, font=text_font, bd=2, relief=SOLID)
new_preset_prompt_entry.pack(side=LEFT, padx=10, pady=5)
new_preset_prompt_entry.insert(0, "Preset Prompt")

# Button to add new bot preset
add_preset_button = Button(new_preset_frame, text="Add Preset", command=lambda: [add_bot_preset(), new_preset_frame.pack_forget()], bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
add_preset_button.pack(side=LEFT, padx=10, pady=5)

# Function to show/hide new preset entry fields
def show_new_preset_fields(choice):
  if choice == "Add New Preset":
    new_preset_frame.pack(side=LEFT, padx=10, pady=5)
  else:
    new_preset_frame.pack_forget()

# Update bot_menu to call show_new_preset_fields when a new option is selected
bot_menu['menu'].entryconfig("Add New Preset", command=lambda: show_new_preset_fields("Add New Preset"))
for preset in BOT_PRESETS.keys():
  bot_menu['menu'].entryconfig(preset, command=lambda value=preset: [bot_selector.set(value), new_preset_frame.pack_forget()])

# Theme Selector
theme_var = StringVar(win)
theme_var.set("System")
theme_menu = OptionMenu(button_frame, theme_var, "Light", "Dark", "System", command=change_theme)
theme_menu.config(font=button_font, bg=button_bg, fg=button_fg, relief=RAISED, bd=3)
theme_menu.pack(side=LEFT, padx=10, pady=5)

win.mainloop()
# Note: The above code is a complete and functional example of a Tkinter-based GUI application that interacts with the Gemini API.
# It includes features for user input, AI response display, note-taking, and theme selection.