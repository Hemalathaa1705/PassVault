import sqlite3
import random
import string
import csv

# ---------- Database Setup ----------
conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

# ---------- Password Generator ----------
def generate_password(length=12):
    if length < 8:
        print("❌ Password too short! Minimum length is 8.")
        return None
    if length > 32:
        print("❌ Password too long! Maximum length is 32.")
        return None
    
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.<>?"
    return ''.join(random.choice(characters) for _ in range(length))

# ---------- Save Password ----------
def save_password(service, username, password):
    cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)", 
                   (service, username, password))
    conn.commit()
    print(f"✅ Password saved for {service}")

# ---------- View Passwords ----------
def view_passwords():
    cursor.execute("SELECT id, service, username, password FROM passwords")
    rows = cursor.fetchall()
    if not rows:
        print("⚠ No passwords saved yet.")
    else:
        for row in rows:
            print(f"ID: {row[0]} | Service: {row[1]} | Username: {row[2]} | Password: {row[3]}")

# ---------- Export Passwords to CSV ----------
def export_to_csv(filename="passwords_export.csv"):
    cursor.execute("SELECT service, username, password FROM passwords")
    rows = cursor.fetchall()

    if not rows:
        print("⚠ No data to export.")
        return

    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Service", "Username", "Password"])  # Header row
        writer.writerows(rows)

    print(f"✅ Passwords exported successfully to {filename}")

# ---------- Modify Password ----------
def modify_password():
    view_passwords()
    try:
        entry_id = int(input("Enter the ID of the entry you want to modify: "))
        cursor.execute("SELECT * FROM passwords WHERE id=?", (entry_id,))
        record = cursor.fetchone()

        if record:
            print(f"Selected -> Service: {record[1]}, Username: {record[2]}, Old Password: {record[3]}")
            choice = input("Do you want to (1) Enter new password or (2) Auto-generate one? ")
            
            if choice == "1":
                new_password = input("Enter new password: ")
            elif choice == "2":
                try:
                    length = int(input("Enter length for new password (8-32): "))
                    new_password = generate_password(length)
                except ValueError:
                    print("❌ Invalid length. Aborting update.")
                    return
            else:
                print("❌ Invalid choice. Aborting update.")
                return

            cursor.execute("UPDATE passwords SET password=? WHERE id=?", (new_password, entry_id))
            conn.commit()
            print("✅ Password updated successfully!")

        else:
            print("❌ No record found with that ID.")

    except ValueError:
        print("❌ Invalid input. Please enter a valid ID.")

# ---------- Main Program ----------
while True:
    print("\n--- Password Manager ---")
    print("1. Generate and Save Password")
    print("2. View Saved Passwords")
    print("3. Export Passwords to CSV")
    print("4. Exit")
    print("5. Modify an Existing Password")
    choice = input("Choose an option: ")

    if choice == "1":
        service = input("Enter service name (e.g., Gmail): ")
        username = input("Enter username/email: ")
        try:
            length = int(input("Enter password length (8-32): "))
            password = generate_password(length)
            if password:
                print("Generated Password:", password)
                save_password(service, username, password)
        except ValueError:
            print("❌ Please enter a valid number.")

    elif choice == "2":
        view_passwords()

    elif choice == "3":
        export_to_csv()

    elif choice == "4":
        print("👋 Exiting Password Manager. Goodbye!")
        break

    elif choice == "5":
        modify_password()

    else:
        print("❌ Invalid choice! Try again.")

conn.close()
