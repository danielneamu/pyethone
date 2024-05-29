import os
import re
from datetime import date
import PyPDF2
#NEW - import for window, title and close button
from tkinter import Tk, Label, Button

# still to do
# 1. choose or enter the folder to be processed
# 2. comment the code for better understanding
# 3. show feedback on a graphical interface/window with the confirmation or errors

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

# Get all PDF files in the directory
pdf_folder = r"C:\Users\daniel.neamu\Downloads\py"
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

############################################################
# NEW
#
# Function to close the window
def close_window():
  root.destroy()
#
# Create the main window with a width and height
root = Tk()
root.title("Procesare Facturi!")
root.geometry("600x400")  # Set window size (width x height)

# Create a label to display the text
label = Label(root, text="Hello World!")
label.pack()

# Create a close button at the bottom
close_button = Button(root, text="Close", command=close_window)
close_button.pack(side="bottom", padx=10, pady=10)  # Pack at bottom with padding
#############################################################

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

# NEW Start the event loop
root.mainloop()
