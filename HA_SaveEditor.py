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
        self.policy_enabled = False
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_studio_tab()
        self.create_cinemas_tab()
        self.create_policy_tab()
        self.create_misc_tab()
        
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

    def create_studio_tab(self):
        studio_frame = ttk.Frame(self.notebook)
        self.notebook.add(studio_frame, text="Studio")
        
        # Currencies Subgroup
        currencies_frame = tk.LabelFrame(studio_frame, text="Currencies")
        currencies_frame.pack(padx=10, pady=5, fill='x')
        
        currency_labels = ["Budget:", "Cash:", "Reputation:", "Influence:"]
        currency_entries = ['budget', 'cash', 'reputation', 'influence']
        
        for row, (label, entry_name) in enumerate(zip(currency_labels, currency_entries)):
            tk.Label(currencies_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(currencies_frame, width=20)
            entry.grid(row=row, column=1, padx=5, pady=5)
            setattr(self, f"{entry_name}_entry", entry)
            entry.bind('<KeyRelease>', lambda e: self.update_independent_cinemas())

        # Misc Subgroup
        misc_frame = tk.LabelFrame(studio_frame, text="Misc")
        misc_frame.pack(padx=10, pady=5, fill='x')
        
        misc_labels = [
            ("Max Plot Elements:", "TAG_SLOT_MAX"),
            ("Max Movies Per Contract:", "CONTRACT_MOVIES_MAX"),
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
        self.allCinemas_entry.bind('<KeyRelease>', lambda e: self.update_independent_cinemas())

        # Independent Cinemas
        tk.Label(cinemas_frame, text="Independent Cinemas:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.independent_cinemas = tk.Label(cinemas_frame, text="0", foreground="grey")
        self.independent_cinemas.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Cinema Ownership
        ownership_frame = tk.LabelFrame(cinemas_frame, text="Cinema Ownership")
        ownership_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        studios = [
            ("PL", "Player Studio"),
            ("GB", "Gerstein Brothers"),
            ("EM", "Evergreen Movies"),
            ("SU", "Supreme"),
            ("HE", "Hephaestus"),
            ("MA", "Marginese")
        ]
        
        for i, (code, name) in enumerate(studios):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(ownership_frame, text=f"{name}:").grid(row=row, column=col, padx=5, pady=2, sticky="e")
            entry = tk.Entry(ownership_frame, width=10)
            entry.grid(row=row, column=col+1, padx=5, pady=2, sticky="w")
            setattr(self, f"cinema_{code}_entry", entry)
            entry.bind('<KeyRelease>', lambda e: self.update_independent_cinemas())

    def create_misc_tab(self):
        misc_frame = ttk.Frame(self.notebook)
        self.notebook.add(misc_frame, text="Version Info")
        
        # Version info (read-only)
        tk.Label(misc_frame, text="First Save Version:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.first_save_version = tk.Label(misc_frame, text="", foreground="grey")
        self.first_save_version.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(misc_frame, text="Last Save Version:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.last_save_version = tk.Label(misc_frame, text="", foreground="grey")
        self.last_save_version.grid(row=1, column=1, padx=5, pady=2, sticky="w")

    def create_policy_tab(self):
        self.policy_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.policy_frame, text="Policy")
        
        # Policy status
        self.policy_status = tk.Label(self.policy_frame, text="Policies are not unlocked (1933)")
        self.policy_status.pack(pady=10)
        
        # Policy dropdown
        self.policy_var = tk.StringVar()
        policies = [
            "POLICY_TRASH",
            "POLICY_MAJOR", 
            "POLICY_BOUTIQUE",
            "POLICY_CONVEYOR",
            "POLICY_AVERAGE"
        ]
        self.policy_dropdown = ttk.Combobox(
            self.policy_frame,
            textvariable=self.policy_var,
            values=policies,
            state="readonly"
        )
        self.policy_dropdown.pack(pady=10)
        self.policy_dropdown.pack_forget()

    def update_independent_cinemas(self):
        try:
            total = int(self.allCinemas_entry.get())
        except:
            total = 0
        
        try:
            owned = sum(
                int(getattr(self, f"cinema_{code}_entry").get())
                for code in ["GB", "EM", "SU", "HE", "MA", "PL"]
            )
        except:
            owned = 0
        
        independent = total - owned
        self.independent_cinemas.config(
            text=str(max(independent, 0)),
            foreground="red" if independent < 0 else "black"
        )

    def load_file(self):
    # Set default save directory with proper LocalLow path
        save_dir = os.path.join(
            os.getenv('USERPROFILE'),
            'AppData',
            'LocalLow',
            'Weappy',
            'Holly',
            'Saves',
            'Profiles',
            '0'
        )
        
        file_path = filedialog.askopenfilename(
            title="Select Save File",
            initialdir=save_dir,
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.current_file = file_path
                self.original_content = content.split('\n')
                
                # Process policy state
                policy_match = re.search(r'"Policy":(true|false)', content)
                if policy_match:
                    self.policy_enabled = policy_match.group(1) == 'true'
                
                # Update policy UI
                if self.policy_enabled:
                    self.policy_status.config(text="Active Policy:")
                    self.policy_dropdown.pack()
                    
                    # Get current policy
                    policy_match = re.search(r'"ACTIVE_POLICY":"(\w+)"', content)
                    if policy_match:
                        self.policy_var.set(policy_match.group(1))
                    else:
                        self.policy_var.set("POLICY_BOUTIQUE")
                else:
                    self.policy_status.config(text="Policies not unlocked")
                    self.policy_dropdown.pack_forget()
                
                # Process standard fields
                self.process_pattern(r'"budget":(\d+)', 'budget')
                self.process_pattern(r'"cash":(\d+)', 'cash')
                self.process_pattern(r'"reputation":"(\d+\.\d{3})"', 'reputation')
                self.process_pattern(r'"influence":(\d+)', 'influence')
                self.process_pattern(r'"TAG_SLOT_MAX":(\d+)', 'TAG_SLOT_MAX')
                self.process_pattern(r'"CONTRACT_MOVIES_MAX":(\d+)', 'CONTRACT_MOVIES_MAX')
                self.process_pattern(r'"CONTRACT_YEARS_MAX":(\d+)', 'CONTRACT_YEARS_MAX')
                self.process_pattern(r'"allCinemas":(\d+)', 'allCinemas')

                # Process cinema ownership
                ownership_match = re.search(r'"ownedCinemas":\s*({[^}]+})', content)
                if ownership_match:
                    ownership_data = ownership_match.group(1)
                    studios = ["GB", "EM", "SU", "HE", "MA", "PL"]
                    for code in studios:
                        match = re.search(fr'"{code}":(\d+)', ownership_data)
                        if match:
                            entry = getattr(self, f"cinema_{code}_entry")
                            entry.delete(0, tk.END)
                            entry.insert(0, match.group(1))

                # Update independent cinemas
                self.update_independent_cinemas()

                # Process version info
                first_ver = re.search(r'"firstSaveVersion":"([^"]+)"', content)
                last_ver = re.search(r'"lastSaveVersion":"([^"]+)"', content)
                self.first_save_version.config(text=first_ver.group(1) if first_ver else "Unknown")
                self.last_save_version.config(text=last_ver.group(1) if last_ver else "Unknown")
                
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
            shutil.copy2(self.current_file, bak_file)
            
            # Read original content
            with open(self.current_file, 'r') as f:
                content = f.read()
            
            # Build updates dictionary
            updates = {
                'budget': (r'(?<="budget":)\d+', self.budget_entry.get()),
                'cash': (r'(?<="cash":)\d+', self.cash_entry.get()),
                'reputation': (r'(?<="reputation":")\d+\.\d{3}', f"{float(self.reputation_entry.get()):.3f}"),
                'influence': (r'(?<="influence":)\d+', self.influence_entry.get()),
                'TAG_SLOT_MAX': (r'(?<="TAG_SLOT_MAX":)\d+', self.TAG_SLOT_MAX_entry.get()),
                'CONTRACT_MOVIES_MAX': (r'(?<="CONTRACT_MOVIES_MAX":)\d+', self.CONTRACT_MOVIES_MAX_entry.get()),
                'CONTRACT_YEARS_MAX': (r'(?<="CONTRACT_YEARS_MAX":)\d+', self.CONTRACT_YEARS_MAX_entry.get()),
                'allCinemas': (r'(?<="allCinemas":)\d+', self.allCinemas_entry.get())
            }

            # Validate numerical values
            for key, (pattern, value) in updates.items():
                if not re.match(r'^\d+$', value):
                    if key == 'reputation' and not re.match(r'^\d+\.\d{3}$', value):
                        raise ValueError(f"Invalid value for {key.replace('_', ' ').title()}")
                    elif key != 'reputation':
                        raise ValueError(f"Invalid value for {key.replace('_', ' ').title()}")

            # Build cinema ownership string
            studios = ["GB", "EM", "SU", "HE", "MA", "PL"]
            ownership_items = []
            for code in studios:
                entry = getattr(self, f"cinema_{code}_entry")
                value = entry.get()
                if not value.isdigit():
                    raise ValueError(f"Invalid cinema value for {code}")
                ownership_items.append(f'"{code}":{value}')
            new_ownership = "{" + ",".join(ownership_items) + "}"
            
            # Replace ownership data
            content = re.sub(
                r'"ownedCinemas":\s*{[^}]+}',
                f'"ownedCinemas":{new_ownership}',
                content
            )

            # Apply other updates
            for pattern, replacement in updates.values():
                content = re.sub(pattern, replacement, content)

            # Update policy if enabled
            if self.policy_enabled:
                content = re.sub(
                    r'"ACTIVE_POLICY":"\w+"',
                    f'"ACTIVE_POLICY":"{self.policy_var.get()}"',
                    content
                )

            # Write changes
            with open(self.current_file, 'w') as f:
                f.write(content)
            
            messagebox.showinfo("Success", "Save file updated successfully!\nBackup created: " + os.path.basename(bak_file))
            
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditor(root)
    root.mainloop()