import random
import string
import json
from tkinter import *
from tkinter import messagebox
import os  # Import os module for path manipulation

# ---------------------------- CONSTANTS ------------------------------- #
BG_COLOR = "#F7F5F2"
FONT_NAME = "Courier"
LOGO_FILE = "logo.png"
DATA_FILE = "data.json"


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate_strong_password():
    """Generates one strong password and returns it as a string."""
    letters = string.ascii_letters
    numbers = string.digits
    symbols = "!#$%&()*+"

    # Ensure a good mix of characters
    password_letters = [random.choice(letters) for _ in
                        range(random.randint(8, 12))]  # Increased range for more letters
    password_symbols = [random.choice(symbols) for _ in range(random.randint(2, 4))]
    password_numbers = [random.choice(numbers) for _ in range(random.randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers
    random.shuffle(password_list)

    return "".join(password_list)


def show_password_choices():
    """Creates a popup window with a list of generated passwords for the user to choose from."""
    popup_window = Toplevel(window)
    popup_window.title("Choose a Password")
    popup_window.config(padx=20, pady=20, bg=BG_COLOR)
    popup_window.resizable(False, False)
    popup_window.grab_set()  # Forces focus on the popup

    info_label = Label(popup_window, text="Click a password to select it:", bg=BG_COLOR, font=(FONT_NAME, 11))
    info_label.pack(pady=(0, 10))

    password_listbox = Listbox(popup_window, width=35, height=10, font=(FONT_NAME, 12),
                               relief="solid")  # Slightly wider
    password_listbox.pack()

    # Populate the listbox with 10 password options
    for _ in range(10):
        password_listbox.insert(END, generate_strong_password())

    def on_password_select(event):
        """Called when a user clicks a password in the listbox."""
        selected_indices = password_listbox.curselection()
        if not selected_indices:
            return

        selected_password = password_listbox.get(selected_indices[0])

        # Clear the password entry and insert the new one
        password_entry.delete(0, END)
        password_entry.insert(0, selected_password)

        # Close the popup
        popup_window.destroy()

    # Bind the function to the listbox selection event
    password_listbox.bind('<<ListboxSelect>>', on_password_select)


# ---------------------------- SAVE PASSWORD ------------------------------- #
def save_data():
    """Saves the website, email, and password to a JSON file."""
    website = website_entry.get().strip()  # .strip() removes leading/trailing whitespace
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    # Use lowercase for website keys for consistent storage and retrieval
    website_key = website.lower()

    new_data = {
        website_key: {
            "email": email,
            "password": password,
        }
    }

    if not website or not password:  # Simpler check for empty fields
        messagebox.showerror(title="Oops", message="Please don't leave Website or Password fields empty!")
        return

    # Optional: More thorough email validation (basic check)
    if "@" not in email or "." not in email:
        messagebox.showwarning(title="Invalid Email", message="Please enter a valid email address.")
        return

    # Before asking, try to load existing data to check for duplicates
    existing_data = {}
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:  # Check if file exists and is not empty
            with open(DATA_FILE, "r") as data_file:
                existing_data = json.load(data_file)
    except json.JSONDecodeError:
        # Handle cases where the file might be corrupted or malformed JSON
        messagebox.showwarning(title="Data Warning", message="Existing data file is corrupted. Starting fresh.")
        existing_data = {}  # Treat as empty if corrupted

    if website_key in existing_data:
        response = messagebox.askyesno(
            title="Website Exists",
            message=f"Details for '{website}' already exist.\n\n"
                    f"Email: {existing_data[website_key]['email']}\n"
                    f"Password: {existing_data[website_key]['password']}\n\n"
                    f"Do you want to update it with the new details?"
        )
        if not response:
            return  # User chose not to update

    is_ok = messagebox.askokcancel(title=website.title(),
                                   message=f"Details to save:\n\nEmail: {email}\nPassword: {password}\n\nIs it okay?")

    if is_ok:
        try:
            # Load existing data
            if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                with open(DATA_FILE, "r") as data_file:
                    data = json.load(data_file)
            else:
                data = {}  # Initialize empty if file doesn't exist or is empty
        except json.JSONDecodeError:
            # If the file exists but is empty or malformed JSON, start with empty data
            data = {}
        except FileNotFoundError:
            data = {}  # This case is covered by os.path.exists, but good for explicit handling

        data.update(new_data)  # Update existing data with new entry

        # Always write back to the file
        with open(DATA_FILE, "w") as data_file:
            json.dump(data, data_file, indent=4)  # 'indent=4' makes the JSON file human-readable

        messagebox.showinfo(title="Success", message="Password details saved!")
        website_entry.delete(0, END)
        password_entry.delete(0, END)
        website_entry.focus()


# ---------------------------- FIND PASSWORD ------------------------------- #
def find_password():
    """Finds and displays the password for a given website."""
    website = website_entry.get().lower().strip()  # Ensure consistent casing and no leading/trailing spaces
    if not website:
        messagebox.showerror(title="Error", message="Please enter a website to search.")
        return

    try:
        # Check if file exists and is not empty before attempting to load
        if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
            messagebox.showerror(title="No Data", message="No saved passwords yet. Save some first!")
            return

        with open(DATA_FILE, "r") as data_file:
            data = json.load(data_file)
            if website in data:
                entry = data[website]
                email = entry["email"]
                password = entry["password"]
                messagebox.showinfo(title=f"{website.title()} Details", message=f"Email: {email}\nPassword: {password}")
            else:
                messagebox.showerror(title="Not Found", message=f"No details for '{website.title()}' exist.")
    except json.JSONDecodeError:
        messagebox.showerror(title="Error", message="The data file is corrupted or empty. Cannot read passwords.")
    except FileNotFoundError:  # This is mostly covered by the os.path.exists check, but good to keep.
        messagebox.showerror(title="Error", message="Data file not found. Save some passwords first.")


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50, bg="sky blue")  # Changed window background to constant

# This part loads and displays the logo
canvas = Canvas(width=400, height=400, bg=BG_COLOR, highlightthickness=0)  # Adjusted canvas size
try:
    logo_img = PhotoImage(file=LOGO_FILE)  # Using the constant
    canvas.create_image(200, 200, image=logo_img)  # Adjusted image position for new canvas size
except TclError:
    # This will show up if logo.png is missing
    canvas.create_text(100, 100, text="Logo Not Found", font=(FONT_NAME, 12, "bold"), fill="red")  # Added fill color
canvas.grid(row=0, column=1, pady=(0, 20))

# --- The rest of your UI ---
website_label = Label(text="Website:", bg=BG_COLOR, font=(FONT_NAME, 12,"bold"))
website_label.grid(row=1, column=0, sticky="E")
email_label = Label(text="Email/Username:", bg=BG_COLOR, font=(FONT_NAME, 12,"bold"))
email_label.grid(row=2, column=0, sticky="E", pady=5)
password_label = Label(text="Password:", bg=BG_COLOR, font=(FONT_NAME, 12,"bold"))
password_label.grid(row=3, column=0, sticky="E")

website_entry = Entry(width=21, font=(FONT_NAME, 12,"bold"))
website_entry.grid(row=1, column=1, sticky="EW", padx=5)
website_entry.focus()
email_entry = Entry(width=35, font=(FONT_NAME, 12))
email_entry.grid(row=2, column=1, columnspan=2, sticky="EW", padx=5, pady=5)
email_entry.insert(0, "your.email@example.com")  # Default email
password_entry = Entry(width=21, font=(FONT_NAME, 12))
password_entry.grid(row=3, column=1, sticky="EW", padx=5)

search_button = Button(text="Search", font=(FONT_NAME, 10,"bold"), command=find_password)
search_button.grid(row=1, column=2, sticky="EW", padx=5)
generate_button = Button(text="Generate Password", font=(FONT_NAME, 10,"bold"), command=show_password_choices)
generate_button.grid(row=3, column=2, sticky="EW", padx=5)
add_button = Button(text="Add", font=(FONT_NAME, 12, "bold"), command=save_data)
add_button.grid(row=4, column=1, columnspan=2, sticky="EW", pady=(10, 0), padx=5)

window.mainloop()