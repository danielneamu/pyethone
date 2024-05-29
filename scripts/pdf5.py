import tkinter as tk  # Importing tkinter for GUI
from tkinter import filedialog  # Importing filedialog for file browsing
import tkinter.font as font  # Importing font for customizing fonts
import os  # Importing os for file operations
import re  # Importing re for regex operations
from datetime import date  # Importing date for date operations
import PyPDF2  # Importing PyPDF2 for PDF text extraction

# Define color theme (adjust as desired)
background_color = "#f0f0f0"
foreground_color = "#333333"
button_color = "#4CAF50"
button_text_color = "white"
font_family = "Arial"

# Global variable to store the selected folder path
pdf_folder = ""

# Create the main window
root = tk.Tk()
root.title("File Selection GUI")
root.geometry("500x300")
root.configure(bg=background_color)

# Create a title label
title_font = font.Font(family=font_family, size=20, weight="bold")
title_label = tk.Label(root, text="Select a Folder", font=title_font, bg=background_color, fg=foreground_color)
title_label.pack(pady=20)

# Function to open file selection dialog
def browse_folder():
    global pdf_folder
    selected_folder = filedialog.askdirectory(title="Select Folder")
    if selected_folder:
        pdf_folder = selected_folder
        folder_path_label.config(text=f"Selected Folder: {selected_folder}")
        next_button.config(state="normal")

# Function to handle "Next" button click
def go_to_next():
    global pdf_folder
    if not pdf_folder:
        return

    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    # Clear all widgets from the window
    for widget in root.pack_slaves():
        widget.destroy()

    # Display confirmation of the selected folder
    confirmation_label = tk.Label(root, text=f"Selected folder: {pdf_folder}", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
    confirmation_label.pack(pady=20)

    # Process each PDF file in the selected folder
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        extracted_text = extract_text_from_pdf(pdf_path)
        processing_label = tk.Label(root, text=f"Processing: {pdf_file}", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
        processing_label.pack()

        if extracted_text:
            relevant_text = get_relevant_text(extracted_text)
            extracted_date = get_relevant_date(extracted_text)
            if relevant_text:
                new_filename = prepend_data_to_filename(pdf_path, relevant_text, extracted_date)
                result_label = tk.Label(root, text=f"File renamed: {pdf_file} to {new_filename}", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
                result_label.pack()
            else:
                error_label = tk.Label(root, text=f"No relevant text found in {pdf_file}.", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
                error_label.pack()
        else:
            error_label = tk.Label(root, text=f"Error extracting text from {pdf_file}.", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
            error_label.pack()
    
    # Add the close button to the window
    close_button.pack(pady=20)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text()
            return full_text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
        return None

# Function to get relevant text from the PDF content
def get_relevant_text(text):
    start_marker = "Identificatorul TVA"
    end_marker = " Nume"
    match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None

# Function to get the relevant date from the PDF content
def get_relevant_date(text):
    start_marker = "Data emitere "
    end_marker = "VANZATOR"
    match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
    if match:
        extracted_date = match.group(1).strip()
        return extracted_date
    else:
        return None

# Function to rename the PDF file with extracted text and date
def prepend_data_to_filename(pdf_path, extracted_text, extracted_date):
    folder, filename = os.path.split(pdf_path)
    base, ext = os.path.splitext(filename)
    new_prefix = f"{extracted_date} {extracted_text}" if extracted_date else f"{extracted_text}"
    new_filename = f"{new_prefix} {base}{ext}"
    new_path = os.path.join(folder, new_filename)

    os.rename(pdf_path, new_path)
    return new_filename

# Create a button to browse folders
browse_button_font = font.Font(family=font_family, size=12, weight="bold")
browse_button = tk.Button(root, text="Browse Folder", font=browse_button_font, bg=button_color, fg=button_text_color, command=browse_folder)
browse_button.pack(pady=20)

# Label to display selected folder path (initially empty)
folder_path_label = tk.Label(root, text="", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
folder_path_label.pack()

# "Next" button initially disabled
next_button = tk.Button(root, text="Next", font=browse_button_font, bg=button_color, fg=button_text_color, command=go_to_next, state="disabled")
next_button.pack(pady=20)

# Create a button to close the window
close_button = tk.Button(root, text="Close Window", font=browse_button_font, bg=button_color, fg=button_text_color, command=root.destroy)

# Start the event loop
root.mainloop()
