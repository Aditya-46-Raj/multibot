import requests
from tkinter import *
import json
from tkinter import filedialog
from fpdf import FPDF

# Set up Gemini API (Replace 'YOUR_API_KEY' with your actual key)
API_KEY = 'YOUR_API_KEY'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Bot Presets
BOT_PRESETS = {
    "child": "Respond in a simple and friendly manner suitable for a child.",
    "coding": "Provide detailed programming help and explanations.",
    "story": "Create engaging and creative stories based on the input.",
    "study partner": "Act as a helpful study companion, explaining concepts clearly."
}

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

def save_notes():
    selected_text = output_text.get(SEL_FIRST, SEL_LAST) if output_text.tag_ranges(SEL) else ""
    if not selected_text:
        return
    
    notes_text.insert(END, selected_text + "\n")

def save_final_notes():
    notes = notes_text.get("1.0", END).strip()
    if not notes:
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, notes)
        pdf.output(file_path)

# UI Setup
win = Tk()
win.geometry("800x600")
win.title("AI Chatbot")
win.config(bg='lightgray')

# Input Panel (Left) - Split into two segments
input_frame = Frame(win, bg="white", padx=10, pady=10)
input_frame.place(x=10, y=10, width=380, height=540)

# Upper segment for notes (3/5 of total height)
notes_frame = Frame(input_frame, bg="white")
notes_frame.place(x=0, y=0, width=360, height=324)
Label(notes_frame, text="Notes Section:", bg="white").pack(anchor=W)
notes_text = Text(notes_frame, wrap=WORD, height=15, width=50)
notes_text.pack()

# Lower segment for user input (2/5 of total height)
user_input_frame = Frame(input_frame, bg="white")
user_input_frame.place(x=0, y=330, width=360, height=216)
Label(user_input_frame, text="User Input:", bg="white").pack(anchor=W)
input_text = Text(user_input_frame, wrap=WORD, height=5, width=50)
input_text.pack()

# Output Panel (Right)
output_frame = Frame(win, bg="white", padx=10, pady=10)
output_frame.place(x=410, y=10, width=380, height=540)
Label(output_frame, text="AI Response:", bg="white").pack(anchor=W)
output_text = Text(output_frame, wrap=WORD, height=25, width=50, state=DISABLED)
output_text.pack()

# Buttons
send_button = Button(win, text="Send", command=send_message, bg="lightblue", height=2, width=15)
send_button.place(x=200, y=560)

save_button = Button(win, text="Save Notes", command=save_notes, bg="lightgreen", height=2, width=15)
save_button.place(x=330, y=560)

final_notes_button = Button(win, text="Final Notes", command=save_final_notes, bg="orange", height=2, width=15)
final_notes_button.place(x=460, y=560)

# Dropdown menu for bot selection
bot_selector = StringVar(win)
bot_selector.set("child")  # Default selection
bot_menu = OptionMenu(win, bot_selector, *BOT_PRESETS.keys())
bot_menu.place(x=590, y=560)

win.mainloop()
