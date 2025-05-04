import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import shutil
import os

class SaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hollywood Animal Save Editor")
        self.current_file = None
        self.original_content = []
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_currencies_tab()
        self.create_misc_tab()
        self.create_cinemas_tab()  # New Cinemas tab
        
        # Create menu buttons
        self.create_menu_buttons()

    def create_menu_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.load_btn = tk.Button(button_frame, text="Load Save", command=self.load_file)
        self.save_btn = tk.Button(button_frame, text="Save Changes", command=self.save_file)
        self.exit_btn = tk.Button(button_frame, text="Exit", command=self.root.quit)
        
        self.load_btn.pack(side='left', padx=5)
        self.save_btn.pack(side='left', padx=5)
        self.exit_btn.pack(side='right', padx=5)

    def create_currencies_tab(self):
        currencies_frame = ttk.Frame(self.notebook)
        self.notebook.add(currencies_frame, text="Currencies")
        
        labels = ["Budget:", "Cash:", "Reputation:", "Influence:"]
        entries = ['budget', 'cash', 'reputation', 'influence']
        
        for row, (label, entry_name) in enumerate(zip(labels, entries)):
            tk.Label(currencies_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(currencies_frame, width=20)
            entry.grid(row=row, column=1, padx=5, pady=5)
            setattr(self, f"{entry_name}_entry", entry)

    def create_misc_tab(self):
        misc_frame = ttk.Frame(self.notebook)
        self.notebook.add(misc_frame, text="Misc")
        
        misc_labels = [
            ("Tag Slots Max:", "TAG_SLOT_MAX"),
            ("Movies Max Per Contract:", "CONTRACT_MOVIES_MAX"),
            ("Max Years Per Contract:", "CONTRACT_YEARS_MAX")
        ]
        
        for row, (label_text, field_name) in enumerate(misc_labels):
            tk.Label(misc_frame, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(misc_frame, width=20)
            entry.grid(row=row, column=1, padx=5, pady=5)
            setattr(self, f"{field_name}_entry", entry)

    def create_cinemas_tab(self):
        cinemas_frame = ttk.Frame(self.notebook)
        self.notebook.add(cinemas_frame, text="Cinemas")
        
        # Total Cinemas
        tk.Label(cinemas_frame, text="Total Cinemas:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.allCinemas_entry = tk.Entry(cinemas_frame, width=20)
        self.allCinemas_entry.grid(row=0, column=1, padx=5, pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.original_content = f.readlines()
                self.current_file = file_path
                
                # Currency patterns
                currency_patterns = {
                    'budget': r'"budget":(\d+)',
                    'cash': r'"cash":(\d+)',
                    'reputation': r'"reputation":"(\d+\.\d{3})"',
                    'influence': r'"influence":(\d+)'
                }
                
                # Misc patterns
                misc_patterns = {
                    'TAG_SLOT_MAX': r'"TAG_SLOT_MAX":(\d+)',
                    'CONTRACT_MOVIES_MAX': r'"CONTRACT_MOVIES_MAX":(\d+)',
                    'CONTRACT_YEARS_MAX': r'"CONTRACT_YEARS_MAX":(\d+)'
                }
                
                # Cinema patterns
                cinema_patterns = {
                    'allCinemas': r'"allCinemas":(\d+)'
                }
                
                # Process currencies
                for key, pattern in currency_patterns.items():
                    self.process_pattern(pattern, key)
                
                # Process misc values
                for key, pattern in misc_patterns.items():
                    self.process_pattern(pattern, key)
                
                # Process cinema values
                for key, pattern in cinema_patterns.items():
                    self.process_pattern(pattern, key)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def process_pattern(self, pattern, field_name):
        found = False
        for line in self.original_content:
            match = re.search(pattern, line)
            if match:
                entry = getattr(self, f"{field_name}_entry")
                entry.delete(0, tk.END)
                entry.insert(0, match.group(1))
                found = True
                break
        if not found:
            entry = getattr(self, f"{field_name}_entry")
            entry.delete(0, tk.END)
            entry.insert(0, '0')

    def save_file(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded!")
            return
            
        try:
            # Create backup
            bak_file = self.current_file + '.bak'
            if os.path.exists(self.current_file):
                shutil.copy2(self.current_file, bak_file)
            
            # Validate and collect new values
            updates = {
                # Currencies
                'budget': (r'(?<="budget":)\d+', self.budget_entry.get(), int),
                'cash': (r'(?<="cash":)\d+', self.cash_entry.get(), int),
                'reputation': (r'(?<="reputation":")\d+\.\d{3}', self.reputation_entry.get(), lambda x: f"{float(x):.3f}"),
                'influence': (r'(?<="influence":)\d+', self.influence_entry.get(), int),
                # Misc
                'TAG_SLOT_MAX': (r'(?<="TAG_SLOT_MAX":)\d+', self.TAG_SLOT_MAX_entry.get(), int),
                'CONTRACT_MOVIES_MAX': (r'(?<="CONTRACT_MOVIES_MAX":)\d+', self.CONTRACT_MOVIES_MAX_entry.get(), int),
                'CONTRACT_YEARS_MAX': (r'(?<="CONTRACT_YEARS_MAX":)\d+', self.CONTRACT_YEARS_MAX_entry.get(), int),
                # Cinemas
                'allCinemas': (r'(?<="allCinemas":)\d+', self.allCinemas_entry.get(), int)
            }
            
            # Validate all values first
            for key, (pattern, value, validator) in updates.items():
                try:
                    validated = str(validator(value))
                    updates[key] = (pattern, validated)
                except:
                    raise ValueError(f"Invalid value for {key.replace('_', ' ').title()}")
            
            # Update content
            updated_content = []
            for line in self.original_content:
                updated_line = line
                for pattern, replacement in updates.values():
                    updated_line = re.sub(pattern, replacement, updated_line)
                updated_content.append(updated_line)
            
            # Write changes
            with open(self.current_file, 'w') as f:
                f.writelines(updated_content)
            
            messagebox.showinfo("Success", "Save file updated successfully!\nBackup created: " + os.path.basename(bak_file))
            
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()
