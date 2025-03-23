import requests
from tkinter import *
import json
from tkinter import filedialog
from fpdf import FPDF

# Set up Gemini API (Replace 'YOUR_API_KEY' with your actual key)
API_KEY = 'AIzaSyChYlxk_Up5AQJO5jJN886gje9gOhTFjzg'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Bot Presets
BOT_PRESETS = {
    "child": "Respond in a simple and friendly manner suitable for a child.",
    "coding": "Provide detailed programming help and explanations.",
    "story": "Create engaging and creative stories based on the input.",
    "study partner": "Act as a helpful study companion, explaining concepts clearly."
}

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
        output_text.insert(END, ai_response)
        output_text.config(state=DISABLED)
    except Exception as e:
        output_text.config(state=NORMAL)
        output_text.delete("1.0", END)
        output_text.insert(END, "Error: " + str(e))
        output_text.config(state=DISABLED)

# Function to save selected text to notes
def save_notes():
    selected_text = output_text.get(SEL_FIRST, SEL_LAST) if output_text.tag_ranges(SEL) else ""
    if not selected_text:
        return
    
    notes_text.insert(END, selected_text + "\n")

# Function to save final notes as a PDF
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

# UI Setup
win = Tk()
win.title("AI Chatbot")
win.state("zoomed")  # Start in fullscreen mode
win.configure(bg="#34495E")  # Darker background for better contrast

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

# Left Panel: User Input and AI Response
left_panel = Frame(main_frame, bg=frame_bg, padx=10, pady=10, bd=2, relief=RIDGE)
left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
left_panel.columnconfigure(0, weight=1)
left_panel.rowconfigure(1, weight=1)
left_panel.rowconfigure(3, weight=1)

Label(left_panel, text="AI Response:", font=("Arial", 14, "bold"), bg=frame_bg).grid(row=0, column=0, sticky="w")
output_text = Text(left_panel, wrap=WORD, state=DISABLED, font=text_font, bd=2, relief=SOLID, highlightbackground=border_color, highlightthickness=1)
output_text.grid(row=1, column=0, sticky="nsew")

Label(left_panel, text="User Input:", font=("Arial", 14, "bold"), bg=frame_bg).grid(row=2, column=0, sticky="w")
input_text = Text(left_panel, wrap=WORD, font=text_font, bd=2, relief=SOLID, height=4, highlightbackground=border_color, highlightthickness=1)
input_text.grid(row=3, column=0, sticky="nsew")

# Right Panel: Notes Section
right_panel = Frame(main_frame, bg=frame_bg, padx=10, pady=10, bd=2, relief=RIDGE)
right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
right_panel.columnconfigure(0, weight=1)
right_panel.rowconfigure(1, weight=1)

Label(right_panel, text="Notes Section:", font=("Arial", 14, "bold"), bg=frame_bg).grid(row=0, column=0, sticky="w")
notes_text = Text(right_panel, wrap=WORD, font=text_font, bd=2, relief=SOLID, highlightbackground=border_color, highlightthickness=1)
notes_text.grid(row=1, column=0, sticky="nsew")

# Buttons & Dropdown
button_frame = Frame(win, bg="#2C3E50")
button_frame.pack(fill=X, pady=10)

send_button = Button(button_frame, text="Send", command=send_message, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
send_button.pack(side=LEFT, padx=10, pady=5)

save_button = Button(button_frame, text="Save Notes", command=save_notes, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
save_button.pack(side=LEFT, padx=10, pady=5)

final_notes_button = Button(button_frame, text="Final Notes", command=save_final_notes, bg=button_bg, fg=button_fg, font=button_font, relief=RAISED, bd=3)
final_notes_button.pack(side=LEFT, padx=10, pady=5)

bot_selector = StringVar(win)
bot_selector.set("child")
bot_menu = OptionMenu(button_frame, bot_selector, *BOT_PRESETS.keys())
bot_menu.config(font=button_font, bg=button_bg, fg=button_fg, relief=RAISED, bd=3)
bot_menu.pack(side=LEFT, padx=10, pady=5)

win.mainloop()