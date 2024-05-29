import tkinter as tk
from tkinter import filedialog
import tkinter.font as font  # Import font library

import os
import re
from datetime import date
import PyPDF2


# Define color theme (adjust as desired)
background_color = "#f0f0f0"
foreground_color = "#333333"
button_color = "#4CAF50"
button_text_color = "white"
font_family = "Arial"  # Adjust font family if desired

# Global variable to store the selected folder path
pdf_folder = ""

# Create the main window
root = tk.Tk()
root.title("File Selection GUI")
root.geometry("500x300")  # Set window size
root.configure(bg=background_color)  # Set background color

# Create a title label
title_font = font.Font(family=font_family, size=20, weight="bold")
title_label = tk.Label(root, text="Select a Folder", font=title_font, bg=background_color, fg=foreground_color)
title_label.pack(pady=20)  # Pack with padding

# Function to open file selection dialog
def browse_folder():
  global pdf_folder  # Access the global variable
  selected_folder = filedialog.askdirectory(title="Select Folder")
  if selected_folder:
    pdf_folder = selected_folder
    folder_path_label.config(text=f"Selected Folder: {selected_folder}")
    # Enable the "Next" button after selection
    next_button.config(state="normal")  # Change state to "normal"

# Function to handle "Next" button click
def go_to_next():
  global pdf_folder  # Access the global variable
  # Clear all widgets from the window
  # Get all PDF files in the directory
  # pdf_folder = r"C:\Users\daniel.neamu\Downloads\py"
  print(pdf_folder)
  pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
  for widget in root.pack_slaves():
    widget.destroy()

  # Create a new label to display confirmation message
  confirmation_label = tk.Label(root, text=f"Selected folder: {pdf_folder}", font=font.Font(family=font_family, size=12), bg=background_color, fg=foreground_color)
  confirmation_label.pack(pady=20)

  # (Replace with your actual functionality using pdf_folder)
  # Example: Process files within the selected folder
  print(f"Processing files in: {pdf_folder}")

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

def get_relevant_text(text):
  start_marker = "Identificatorul TVA"
  end_marker = " Nume"
  match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
  if match:
    return match.group(1).strip()
  else:
    return None

def get_relevant_date(text):
  start_marker = "Data emitere "
  end_marker = "VANZATOR"
  match = re.search(f"{start_marker}(.*?){end_marker}", text, re.DOTALL)
  if match:
    extracted_date = match.group(1).strip()
    return extracted_date
  else:
    return None

def prepend_data_to_filename(pdf_path, extracted_text, extracted_date):
  folder, filename = os.path.split(pdf_path)
  base, ext = os.path.splitext(filename)

  # Prepend data using underscores (adjust separator as needed)
  new_prefix = f"{extracted_date} {extracted_text}" if extracted_date else f"{extracted_text}"
  new_filename = f"{new_prefix} {base}{ext}"
  new_path = os.path.join(folder, new_filename)

  # Check if file already exists (optional)
  # if os.path.exists(new_path):
  #   # Handle existing file scenario (e.g., print warning)
  #   print(f"File with name {new_filename} already exists.")
  # else:
  os.rename(pdf_path, new_path) 
  print(f"File renamed: {filename} to {new_filename}")
  
  # NEW Create a label to display the text in the window
  label = Label(root, text = "File renamed: " + filename + " to " + new_filename)
  label.pack()


for pdf_file in pdf_files:
  pdf_path = os.path.join(pdf_folder, pdf_file)
  extracted_text = extract_text_from_pdf(pdf_path)
  print(f"\nProcessing: {pdf_file}")
  
  # NEW Create a label to display the text
  label = Label(root, text = "Processing: " + pdf_file)
  label.pack()
  
  if extracted_text:
    relevant_text = get_relevant_text(extracted_text)
    extracted_date = get_relevant_date(extracted_text)
    if relevant_text:
      prepend_data_to_filename(pdf_path, relevant_text, extracted_date)
    else:
      print("No relevant text found in the PDF.")
  else:
    print("Error extracting text from the PDF.")

print("\nAll files processed!")



# Start the event loop
root.mainloop()
