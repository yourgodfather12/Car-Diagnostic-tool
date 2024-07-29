import tkinter as tk
from tkinter import ttk, messagebox
import gettext
import logging
from typing import Optional
import car_issues
from nlp_utils import extract_keywords, fuzzy_match
from ui import set_status, apply_theme, Tooltip, setup_translation

# Configure logging
logging.basicConfig(
    filename='application.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

search_history = []
language = 'en'

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Diagnostic Tool")
        self.geometry("800x600")
        self.style = ttk.Style()  # Initialize ttk Style
        self.configure_ui()
        self.setup_widgets()

    def configure_ui(self):
        # Apply a custom theme
        apply_theme(self.style, "light")

    def setup_widgets(self):
        # Header
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=3, pady=10)
        header_label = ttk.Label(header_frame, text="Car Diagnostic Tool", font=("Helvetica", 24, "bold"))
        header_label.pack()

        # Input field for code or symptom with placeholder
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, columnspan=3, pady=10)
        self.entry_code = ttk.Entry(input_frame, width=40, font=("Helvetica", 14))
        self.entry_code.insert(0, "Enter Error Code or Symptom")
        self.entry_code.bind("<FocusIn>", lambda args: self.entry_code.delete('0', 'end'))
        self.entry_code.pack(side=tk.LEFT, padx=(0, 10))

        # Diagnose button without icon
        btn_diagnose = ttk.Button(input_frame, text="Diagnose", command=self.diagnose_issue)
        btn_diagnose.pack(side=tk.LEFT)

        # Display area for issue information with scrollable text
        issue_frame = ttk.Frame(self)
        issue_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")
        self.text_issue = tk.Text(issue_frame, wrap=tk.WORD, state=tk.DISABLED, height=15, width=70, font=("Helvetica", 12))
        self.text_issue.grid(row=0, column=0, sticky="nsew")
        text_scroll = ttk.Scrollbar(issue_frame, command=self.text_issue.yview)
        self.text_issue.config(yscrollcommand=text_scroll.set)
        text_scroll.grid(row=0, column=1, sticky='ns')

        # Status bar
        self.status_bar = ttk.Label(self, text="Status: Ready", style='Statusbar.TLabel', padding=10)
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky='we')

        # Tooltips
        Tooltip(self.entry_code, text="Enter a known error code or symptom.", delay=700)

        # Theme and language switchers
        theme_switcher_frame = ttk.Frame(self)
        theme_switcher_frame.grid(row=4, column=0, columnspan=3, pady=20)
        theme_label = ttk.Label(theme_switcher_frame, text="Theme:", font=("Helvetica", 12))
        theme_label.pack(side=tk.LEFT, padx=10)
        theme_switcher = ttk.Combobox(theme_switcher_frame, values=["light", "dark"], state="readonly", width=10)
        theme_switcher.current(0)
        theme_switcher.pack(side=tk.LEFT)
        theme_switcher.bind("<<ComboboxSelected>>", self.change_theme)

        language_label = ttk.Label(theme_switcher_frame, text="Language:", font=("Helvetica", 12))
        language_label.pack(side=tk.LEFT, padx=(20, 10))
        language_switcher = ttk.Combobox(theme_switcher_frame, values=["English", "Spanish"], state="readonly", width=10)
        language_switcher.current(0)
        language_switcher.pack(side=tk.LEFT)
        language_switcher.bind("<<ComboboxSelected>>", self.change_language)

    def diagnose_issue(self):
        '''Diagnose the car issue based on the error code or symptom.'''
        code_or_symptom = self.entry_code.get().upper().strip()
        if not code_or_symptom:
            set_status(self.style, self.status_bar, "Please enter an error code or symptom.", "error")
            return

        # Save to history
        search_history.append(code_or_symptom)
        logging.info(f"User entered: {code_or_symptom}")

        try:
            # Try to match by code
            issue = car_issues.car_issues.get(code_or_symptom)
            if issue:
                self.display_issue(issue)
                set_status(self.style, self.status_bar, "Diagnosis complete.", "success")
            else:
                # Try to match by keywords and fuzzy matching
                found_issues = self.search_by_keywords(code_or_symptom)
                if found_issues:
                    self.display_issue(found_issues[0])  # Display the first found issue for simplicity
                    set_status(self.style, self.status_bar, "Diagnosis complete.", "success")
                else:
                    self.suggest_fuzzy_matches(code_or_symptom)
                    set_status(self.style, self.status_bar, "No exact match found, showing suggestions.", "warning")
        except Exception as e:
            logging.error(f"Error in diagnosis process: {e}", exc_info=True)
            messagebox.showerror("Error", "An error occurred during diagnosis. Please try again.")

    def search_by_keywords(self, symptoms):
        '''Search for issues by keywords found in symptoms.'''
        try:
            found_issues = []
            symptoms_keywords = extract_keywords(symptoms, language=language)
            for code, issue in car_issues.car_issues.items():
                issue_keywords = extract_keywords(issue['description'] + " " + issue['symptoms'] + " " + issue['causes'],
                                                  language=language)
                if symptoms_keywords & issue_keywords:
                    found_issues.append(issue)
            logging.info(f"Keywords search results: {found_issues}")
            return found_issues
        except Exception as e:
            logging.error(f"Error in keyword search: {e}", exc_info=True)
            return []

    def suggest_fuzzy_matches(self, code_or_symptom):
        '''Suggest similar issues using fuzzy matching.'''
        try:
            matches = []
            for code, issue in car_issues.car_issues.items():
                score = fuzzy_match(code_or_symptom, code)
                if score > 0.8:
                    matches.append((code, issue))
            if matches:
                self.display_issue(matches[0][1])  # Display the first match for simplicity
                logging.info(f"Fuzzy match found: {matches[0]}")
            else:
                messagebox.showinfo("No matches found", "No similar issues were found.")
                logging.warning("No fuzzy matches found.")
        except Exception as e:
            logging.error(f"Error in fuzzy matching: {e}", exc_info=True)
            messagebox.showerror("Error", "An error occurred during fuzzy matching.")

    def display_issue(self, issue):
        '''Display the diagnosed issue.'''
        try:
            self.text_issue.config(state=tk.NORMAL)
            self.text_issue.delete('1.0', tk.END)
            self.text_issue.insert(tk.END, f"Issue: {issue['description']}\n")
            self.text_issue.insert(tk.END, f"Symptoms: {issue['symptoms']}\n")
            self.text_issue.insert(tk.END, f"Causes: {issue['causes']}\n")
            self.text_issue.insert(tk.END, f"Solutions: {issue['solutions']}\n")
            self.text_issue.config(state=tk.DISABLED)
            logging.info(f"Displayed issue: {issue['description']}")
        except Exception as e:
            logging.error(f"Error displaying issue: {e}", exc_info=True)
            messagebox.showerror("Error", "An error occurred while displaying the issue.")

    def change_theme(self, event):
        selected_theme = event.widget.get()
        apply_theme(self.style, selected_theme)
        set_status(self.style, self.status_bar, f"Theme changed to {selected_theme}", "info")

    def change_language(self, event):
        selected_language = event.widget.get()
        lang_code = 'en' if selected_language == "English" else 'es'
        setup_translation(lang_code)
        set_status(self.style, self.status_bar, f"Language changed to {selected_language}", "info")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
