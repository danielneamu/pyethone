# Importing libraries
import tkinter as tk                            # Importing tkinter for GUI
from tkinter import filedialog            # Importing filedialog for file browsing
import tkinter.font as font                 # Importing font for customizing fonts
from tkinter import messagebox       # Importing messagebox for displaying messages to the user
import os                                            # Importing os for file operations
import re                                            # Importing re for regex operations
from datetime import date                # Importing date for date operations
import PyPDF2                                   # Importing PyPDF2 for PDF text extraction
import time
import openpyxl


# Define GUI parameters
BACKGROUND_COLOR = "#FFFFFF"
FOREGROUND_COLOR = "#333333"
BUTTON_COLOR = "#008000"
BUTTON_TEXT_COLOR = "white"
FONT_FAMILY = "Arial"
# Define a dictionary for the disabled state style
DISABLED_STYLE = {"background": "#ECFFDC"}
ENABLED_STYLE = {"background": "#008000", "fg": "white"}

array_facturi = []

class PDFProcessorApp:
    # GUI INITIALIZATION
    def __init__(self, root):
        self.root = root
        self.root.title("Redenumire fisiere PDF")
        self.root.geometry("600x400")
        self.root.configure(bg=BACKGROUND_COLOR)
        self.pdf_folder = ""
        self.create_widgets()

    def create_widgets(self):
        self.create_title_label()
        self.create_browse_button()
        self.create_folder_path_label()
        self.create_next_button()

    def create_title_label(self):
        title_font = font.Font(family=FONT_FAMILY, size=20, weight="bold")
        self.title_label = tk.Label(self.root, text="Select a Folder", font=title_font, bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
        self.title_label.pack(pady=20)

    def create_browse_button(self):
        browse_button_font = font.Font(family=FONT_FAMILY, size=12, weight="bold")
        self.browse_button = tk.Button(self.root, text="Browse Folder", font=browse_button_font, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=self.browse_folder)
        self.browse_button.pack(pady=20)

    def create_folder_path_label(self):
        self.folder_path_label = tk.Label(self.root, text="", font=font.Font(family=FONT_FAMILY, size=12), bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
        self.folder_path_label.pack()

    def create_next_button(self):
        self.next_button = tk.Button(self.root, text="Next", font=font.Font(family=FONT_FAMILY, size=12, weight="bold"), bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=self.go_to_next, state="disabled", disabledforeground="gray")
        self.next_button.config(**DISABLED_STYLE)
        self.next_button.pack(pady=20)
    #END OF GUI INITIALISATION

    # Defingin relevant functions used in the main action - they can stay OUTSIDE the class
    def browse_folder(self):
        selected_folder = filedialog.askdirectory(title="Select Folder")
        if selected_folder:
            self.pdf_folder = selected_folder

            # Check for presence of PDF files
            has_pdf_files = False
            for filename in os.listdir(selected_folder):
                if filename.lower().endswith(".pdf"):  # Check for lowercase extension
                    has_pdf_files = True
                    break  # Stop iterating if a PDF is found

            if has_pdf_files:
                self.folder_path_label.config(text=f"Selected Folder: {selected_folder}")
                self.next_button.config(state="normal")
                self.next_button.config(**ENABLED_STYLE)
            else:
                # Show error message
                message_box = messagebox.showerror(title="No PDF Files Found", message="Folderul selectat nu contine nici un fisier de tip PDF.")
                self.folder_path_label.config(text="")  # Clear previous selection

    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page in pdf_reader.pages:
                    full_text += page.extract_text()
                    # print(full_text)
                return full_text
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
            return None

    def get_relevant_text(self, text):
        start_marker = "Identificatorul TVA"
        end_marker = " Nume"
        match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return None

    def get_relevant_date(self, text):
        start_marker = "Data emitere "
        end_marker = "VANZATOR"
        match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
        if match:
            extracted_date = match.group(1).strip()
            return extracted_date
        else:
            return None
    
    def get_relevant_cui(self, text):
        start_marker = "Denumire"
        end_marker = " Identificatorul"
        match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
        if match:
            extracted_cui = match.group(1).strip()
            return extracted_cui
        else:
            return None
            
    def get_relevant_value(self, text):
        pattern = r"(\d+\.\d+)\s+TOTAL PLATATOTAL NET"
        match = re.search(pattern, text)
        if match:
            extracted_value = match.group(1)
            return float(extracted_value)
        else:
            return None

    def get_relevant_invoice(self, text):
        start_marker = "RO eFactura"
        end_marker = " Nr. factura"
        match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
        if match:
            extracted_invoice = match.group(1).strip()
            return extracted_invoice
        else:
            return None

    def add_invoice_to_table(self, array_facturi):
        # Load the workbook
        workbook_path = "facturi.xlsx"
        workbook = openpyxl.load_workbook(workbook_path)

        # Assuming the sheet name is "Facturi" (you can adjust this)
        sheet_name = "Facturi"
        sheet = workbook[sheet_name]

        # Get the column index for "Factura" (adjust as needed)
        factura_col_index = 3  # Assuming it's the first column (C)

        # Check each line in the array
        for line in array_facturi:
            relevant_invoice = line[2]  # Assuming relevant_invoice is at index 2
            print(relevant_invoice)
            invoice_exists = any(cell.value == relevant_invoice for cell in sheet[f"C:C"])

            if not invoice_exists:
                # Append the line to the table
                sheet.append(line)

        # Save the modified workbook
        workbook.save(workbook_path)
            

    def prepend_data_to_filename(self, pdf_path, extracted_text, extracted_date):
        folder, filename = os.path.split(pdf_path)
        base, ext = os.path.splitext(filename)
        new_prefix = f"{extracted_date} {extracted_text}" if extracted_date else f"{extracted_text}"
        new_filename = f"{new_prefix} {base}{ext}"
        new_path = os.path.join(folder, new_filename)
        try:
            os.rename(pdf_path, new_path)
            return new_filename
        except (PermissionError, FileNotFoundError) as e:
            # Display error message to the user
            messagebox.showerror("File Rename Error", f"Failed to rename file: {pdf_path}\nError: {e}")
            return None

    def generate_new_filename(self, pdf_path, extracted_text, extracted_date):
        folder, filename = os.path.split(pdf_path)
        base, ext = os.path.splitext(filename)
        new_prefix = f"{extracted_date} {extracted_text}" if extracted_date else f"{extracted_text}"
        new_filename = f"{new_prefix} {base}{ext}"
        return new_filename

    def clear_window(self):
        """
        Print all widgets in the root window and then clear them.
        """
        for widget in self.root.winfo_children():
            print(widget)
            widget.destroy()

    # THE MAIN  trigger of the program is the click on the NEXT buttton
    def go_to_next(self):
        # Conditional check if pdf_folder is assigned. Since NEXT button is not enabled (in our scenario) until pdf_folder is assigned, this check is redundant
        #if not self.pdf_folder:
        #    messagebox.showinfo("Folder Not Selected", "Please select a folder before proceeding.")
        #    return
        
        # Clearing the current window after clicking next
        self.clear_window() # Clear the window before adding new labels

        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.endswith(".pdf")]

        confirmation_label = tk.Label(self.root, text=f"Selected folder: {self.pdf_folder}", font=font.Font(family=FONT_FAMILY, size=12), bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
        confirmation_label.pack(pady=20)

        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_folder, pdf_file)
            extracted_text = self.extract_text_from_pdf(pdf_path)
            # processing_label = tk.Label(self.root, text=f"Processing: {pdf_file}", font=font.Font(family=FONT_FAMILY, size=12), bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
            # processing_label.pack()

            if extracted_text:
                relevant_text = self.get_relevant_text(extracted_text)
                extracted_date = self.get_relevant_date(extracted_text)
                
                # ARRAY SCRIPT
                relevant_cui = self.get_relevant_cui(extracted_text)
                relevant_value = self.get_relevant_value(extracted_text)
                relevant_invoice = self.get_relevant_invoice(extracted_text)
                
                if relevant_text:
                    ####################################################
                    # UNCOMMENT FOLLOWING LINE TO START RENAMING THE FILES #
                    ####################################################

                    new_filename = self.prepend_data_to_filename(pdf_path, relevant_text, extracted_date)
                    new_filename = self.generate_new_filename(pdf_path, relevant_text, extracted_date)
                    result_label = tk.Label(self.root, text=f"{pdf_file} --> {new_filename}", font=font.Font(family=FONT_FAMILY, size=12), bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
                    result_label.pack()
                    self.root.update_idletasks()
                    time.sleep(0.3)
                
                    # ARRAY SCRIPT
                    array_facturi.append([relevant_text, relevant_cui, relevant_invoice,  extracted_date, relevant_value])
                    

                else:
                    error_label = tk.Label(self.root, text=f"No relevant text found in {pdf_file}.", font=font.Font(family=FONT_FAMILY, size=12), bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
                    error_label.pack()
            else:
                error_label = tk.Label(self.root, text=f"Error extracting text from {pdf_file}.", font=font.Font(family=FONT_FAMILY, size=12), bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR)
                error_label.pack()
        
        print(array_facturi)
        self.add_invoice_to_table(array_facturi)
        print("Invoices added successfully!")
        
        close_button = tk.Button(self.root, text="Close Window", font=font.Font(family=FONT_FAMILY, size=12, weight="bold"), bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=self.root.destroy)
        close_button.pack(pady=20)


# Create the main window
root = tk.Tk()
app = PDFProcessorApp(root)
root.mainloop()