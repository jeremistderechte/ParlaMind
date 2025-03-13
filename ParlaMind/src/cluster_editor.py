import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# --- Initial cluster dictionary ---
cluster_dict = {
    "Example" : ("example",)
}

# A list to hold loaded dictionaries (each as a tuple: (filename, dict))
loaded_dicts = []

# --- Helper: Update an OptionMenu from a search field ---
def update_option_menu_field(search_entry, option_menu, variable):
    search_text = search_entry.get().strip()
    if search_text:
        filtered_keys = [k for k in cluster_dict.keys() if search_text.lower() in k.lower()]
    else:
        filtered_keys = list(cluster_dict.keys())
    menu = option_menu["menu"]
    menu.delete(0, "end")
    for key in filtered_keys:
        # Use a default argument to bind current key
        menu.add_command(label=key, command=lambda value=key: variable.set(value))
    if filtered_keys:
        variable.set(filtered_keys[0])
    else:
        variable.set("")

def update_join_listbox_field(search_entry, listbox):
    search_text = search_entry.get().strip()
    listbox.delete(0, tk.END)
    for key in cluster_dict.keys():
        if search_text.lower() in key.lower():
            listbox.insert(tk.END, key)

def open_cluster_editor():
    # Create the main window (1600x1200 for a large screen)
    root = tk.Tk()
    root.title("Cluster Editor")
    root.geometry("1600x1200")
    
    # Use a larger default font for readability
    default_font = ("Helvetica", 14)
    
    # Tkinter variables for dropdowns
    rename_var = tk.StringVar(root)
    edit_var = tk.StringVar(root)
    split_var = tk.StringVar(root)
    delete_var = tk.StringVar(root)

    # Helper to update all OptionMenus based on current search fields
    def update_all_option_menus():
        update_option_menu_field(rename_search, rename_option, rename_var)
        update_option_menu_field(edit_search, edit_option, edit_var)
        update_option_menu_field(split_search, split_option, split_var)
        update_option_menu_field(delete_search, delete_option, delete_var)
        update_join_listbox_field(join_search, join_listbox)
    
    # Create a Notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # --- Tab 1: Rename Cluster ---
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Rename")
    # Row 0: Label and OptionMenu for cluster selection and a search field
    tk.Label(tab1, text="Select Cluster:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    rename_option = tk.OptionMenu(tab1, rename_var, *cluster_dict.keys())
    rename_option.config(width=30, font=default_font)
    rename_option.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    tk.Label(tab1, text="Search:", font=default_font).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    rename_search = tk.Entry(tab1, font=default_font, width=20)
    rename_search.grid(row=0, column=3, sticky="w", padx=5, pady=5)
    rename_search.bind("<KeyRelease>", lambda event: update_option_menu_field(rename_search, rename_option, rename_var))
    
    # Preview label for Rename tab
    tk.Label(tab1, text="Preview (first 5 terms):", font=(default_font[0], default_font[1], "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    rename_preview_label = tk.Label(tab1, text="", wraplength=600, justify="left", fg="blue", font=default_font)
    rename_preview_label.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    
    tk.Label(tab1, text="New Name:", font=default_font).grid(row=2, column=0, sticky="w", padx=5, pady=5)
    rename_entry = tk.Entry(tab1, width=40, font=default_font)
    rename_entry.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    
    def update_rename_preview(*args):
        cluster = rename_var.get()
        if cluster in cluster_dict:
            terms = cluster_dict[cluster]
            preview = ", ".join(terms[:5])
            rename_preview_label.config(text=preview)
        else:
            rename_preview_label.config(text="")
    
    rename_var.trace("w", update_rename_preview)
    
    def do_rename():
        old_name = rename_var.get()
        new_name = rename_entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Please enter a valid new name.")
            return
        if new_name in cluster_dict:
            messagebox.showerror("Error", f"Cluster '{new_name}' already exists.")
            return
        cluster_dict[new_name] = cluster_dict.pop(old_name)
        rename_var.set(new_name)
        edit_var.set(new_name)
        split_var.set(new_name)
        delete_var.set(new_name)
        update_all_option_menus()
        rename_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Cluster '{old_name}' renamed to '{new_name}'.")
        
    tk.Button(tab1, text="Rename", command=do_rename, font=default_font, width=20).grid(row=3, column=0, columnspan=4, pady=10)
    
    # --- Tab 2: Edit Cluster Terms ---
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Edit Terms")
    tk.Label(tab2, text="Select Cluster:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    edit_option = tk.OptionMenu(tab2, edit_var, *cluster_dict.keys())
    edit_option.config(width=30, font=default_font)
    edit_option.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    tk.Label(tab2, text="Search:", font=default_font).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    edit_search = tk.Entry(tab2, font=default_font, width=20)
    edit_search.grid(row=0, column=3, sticky="w", padx=5, pady=5)
    edit_search.bind("<KeyRelease>", lambda event: update_option_menu_field(edit_search, edit_option, edit_var))
    
    tk.Label(tab2, text="Terms (one per line):", font=default_font).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
    edit_text = tk.Text(tab2, height=15, width=60, font=default_font)
    edit_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
    
    def load_edit_terms(*args):
        cluster = edit_var.get()
        terms = cluster_dict.get(cluster, ())
        edit_text.delete("1.0", tk.END)
        edit_text.insert(tk.END, "\n".join(terms))
        
    edit_var.trace("w", load_edit_terms)
    load_edit_terms()
    
    def do_edit():
        cluster = edit_var.get()
        terms = [line.strip() for line in edit_text.get("1.0", tk.END).splitlines() if line.strip()]
        cluster_dict[cluster] = tuple(terms)
        messagebox.showinfo("Success", f"Terms for '{cluster}' updated.")
        
    tk.Button(tab2, text="Update Terms", command=do_edit, font=default_font, width=20).grid(row=2, column=0, columnspan=4, pady=10)
    
    # --- Tab 3: Split Cluster ---
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Split")
    tk.Label(tab3, text="Select Cluster to Split:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    split_option = tk.OptionMenu(tab3, split_var, *cluster_dict.keys())
    split_option.config(width=30, font=default_font)
    split_option.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    tk.Label(tab3, text="Search:", font=default_font).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    split_search = tk.Entry(tab3, font=default_font, width=20)
    split_search.grid(row=0, column=3, sticky="w", padx=5, pady=5)
    split_search.bind("<KeyRelease>", lambda event: update_option_menu_field(split_search, split_option, split_var))
    
    tk.Label(tab3, text="New Name 1:", font=default_font).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    split_name1 = tk.Entry(tab3, width=40, font=default_font)
    split_name1.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    tk.Label(tab3, text="New Name 2:", font=default_font).grid(row=2, column=0, sticky="w", padx=5, pady=5)
    split_name2 = tk.Entry(tab3, width=40, font=default_font)
    split_name2.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    
    tk.Label(tab3, text="Terms for Cluster 1 (one per line):", font=default_font).grid(row=3, column=0, sticky="nw", padx=5, pady=5)
    split_text1 = tk.Text(tab3, height=10, width=50, font=default_font)
    split_text1.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    
    tk.Label(tab3, text="Terms for Cluster 2 (one per line):", font=default_font).grid(row=4, column=0, sticky="nw", padx=5, pady=5)
    split_text2 = tk.Text(tab3, height=10, width=50, font=default_font)
    split_text2.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    
    def prepopulate_split(*args):
        cluster = split_var.get()
        terms = cluster_dict.get(cluster, ())
        split_text1.delete("1.0", tk.END)
        split_text1.insert(tk.END, "\n".join(terms))
        split_text2.delete("1.0", tk.END)
        split_name1.delete(0, tk.END)
        split_name1.insert(0, f"{cluster}_1")
        split_name2.delete(0, tk.END)
        split_name2.insert(0, f"{cluster}_2")
        
    split_var.trace("w", prepopulate_split)
    prepopulate_split()
    
    def do_split():
        original = split_var.get()
        name1 = split_name1.get().strip()
        name2 = split_name2.get().strip()
        if not name1 or not name2:
            messagebox.showerror("Error", "Please provide valid names for both new clusters.")
            return
        if name1 in cluster_dict or name2 in cluster_dict:
            messagebox.showerror("Error", "One of the new cluster names already exists.")
            return
        terms1 = [line.strip() for line in split_text1.get("1.0", tk.END).splitlines() if line.strip()]
        terms2 = [line.strip() for line in split_text2.get("1.0", tk.END).splitlines() if line.strip()]
        cluster_dict.pop(original, None)
        cluster_dict[name1] = tuple(terms1)
        cluster_dict[name2] = tuple(terms2)
        messagebox.showinfo("Success", f"Cluster '{original}' split into '{name1}' and '{name2}'.")
        split_var.set(name1)
        update_all_option_menus()
        
    tk.Button(tab3, text="Split Cluster", command=do_split, font=default_font, width=20).grid(row=5, column=0, columnspan=4, pady=10)
    
    # --- Tab 4: Join Clusters ---
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="Join")
    tk.Label(tab4, text="Search Clusters:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    join_search = tk.Entry(tab4, font=default_font, width=30)
    join_search.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    join_search.bind("<KeyRelease>", lambda event: update_join_listbox_field(join_search, join_listbox))
    
    tk.Label(tab4, text="Select Clusters (Ctrl+Click):", font=default_font).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    join_listbox = tk.Listbox(tab4, selectmode=tk.MULTIPLE, width=40, height=10, font=default_font)
    join_listbox.grid(row=2, column=0, padx=5, pady=5)
    # Initially fill join_listbox
    for key in cluster_dict.keys():
        join_listbox.insert(tk.END, key)
    
    tk.Label(tab4, text="New Cluster Name:", font=default_font).grid(row=3, column=0, sticky="w", padx=5, pady=5)
    join_entry = tk.Entry(tab4, width=40, font=default_font)
    join_entry.grid(row=4, column=0, padx=5, pady=5)
    
    def do_join():
        selected_indices = join_listbox.curselection()
        selected = [join_listbox.get(i) for i in selected_indices]
        new_name = join_entry.get().strip()
        if not selected:
            messagebox.showerror("Error", "Please select at least one cluster to join.")
            return
        if not new_name:
            messagebox.showerror("Error", "Please provide a valid new name.")
            return
        if new_name in cluster_dict:
            messagebox.showerror("Error", "New cluster name already exists.")
            return
        combined_terms = []
        for key in selected:
            combined_terms.extend(cluster_dict.get(key, ()))
        seen = set()
        combined_terms = [x for x in combined_terms if x not in seen and not seen.add(x)]
        for key in selected:
            cluster_dict.pop(key, None)
        cluster_dict[new_name] = tuple(combined_terms)
        messagebox.showinfo("Success", f"Clusters {selected} joined into '{new_name}'.")
        join_entry.delete(0, tk.END)
        update_all_option_menus()
        
    tk.Button(tab4, text="Join Clusters", command=do_join, font=default_font, width=20).grid(row=5, column=0, columnspan=2, pady=10)
    
    # --- Tab 5: Load/Join Dictionaries ---
    tab5 = ttk.Frame(notebook)
    notebook.add(tab5, text="Load/Join Dicts")
    tk.Label(tab5, text="Loaded Dictionary Files:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    loaded_listbox = tk.Listbox(tab5, width=60, height=10, font=default_font)
    loaded_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    
    def update_loaded_listbox():
        loaded_listbox.delete(0, tk.END)
        for filename, _ in loaded_dicts:
            loaded_listbox.insert(tk.END, filename)
    
    def load_dict_files():
        file_paths = filedialog.askopenfilenames(
            title="Select Cluster Dictionary Files",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All Files", "*.*")]
        )
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                loaded_data = {k: tuple(v) for k, v in data.items()}
                loaded_dicts.append((file_path, loaded_data))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {file_path}:\n{e}")
        update_loaded_listbox()
    
    tk.Button(tab5, text="Load Dictionary File(s)", command=load_dict_files, font=default_font, width=25).grid(row=2, column=0, padx=5, pady=5)
    def clear_loaded():
        loaded_dicts.clear()
        update_loaded_listbox()
    tk.Button(tab5, text="Clear Loaded Dictionaries", command=clear_loaded, font=default_font, width=25).grid(row=2, column=1, padx=5, pady=5)
    
    def join_loaded_dicts():
        for _, loaded in loaded_dicts:
            for key, terms in loaded.items():
                new_key = key
                if new_key in cluster_dict:
                    i = 1
                    while new_key in cluster_dict:
                        new_key = f"{key}_{i}"
                        i += 1
                cluster_dict[new_key] = terms
        messagebox.showinfo("Success", "Loaded dictionaries have been merged into the current clusters.")
        update_all_option_menus()
    tk.Button(tab5, text="Join Loaded Dictionaries", command=join_loaded_dicts, font=default_font, width=30).grid(row=3, column=0, columnspan=2, pady=10)
    
    # --- Tab 6: Delete Cluster ---
    tab6 = ttk.Frame(notebook)
    notebook.add(tab6, text="Delete")
    tk.Label(tab6, text="Select Cluster to Delete:", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    delete_option = tk.OptionMenu(tab6, delete_var, *cluster_dict.keys())
    delete_option.config(width=30, font=default_font)
    delete_option.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    tk.Label(tab6, text="Search:", font=default_font).grid(row=0, column=2, sticky="w", padx=5, pady=5)
    delete_search = tk.Entry(tab6, font=default_font, width=20)
    delete_search.grid(row=0, column=3, sticky="w", padx=5, pady=5)
    delete_search.bind("<KeyRelease>", lambda event: update_option_menu_field(delete_search, delete_option, delete_var))
    
    tk.Label(tab6, text="Preview (first 5 terms):", font=(default_font[0], default_font[1], "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
    delete_preview_label = tk.Label(tab6, text="", wraplength=600, justify="left", fg="blue", font=default_font)
    delete_preview_label.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
    
    def update_delete_preview(*args):
        cluster = delete_var.get()
        if cluster in cluster_dict:
            terms = cluster_dict[cluster]
            preview = ", ".join(terms[:5])
            delete_preview_label.config(text=preview)
        else:
            delete_preview_label.config(text="")
    delete_var.trace("w", update_delete_preview)
    
    def do_delete():
        cluster = delete_var.get()
        if not cluster:
            messagebox.showerror("Error", "No cluster selected.")
            return
        answer = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the cluster '{cluster}'?")
        if answer:
            cluster_dict.pop(cluster, None)
            messagebox.showinfo("Deleted", f"Cluster '{cluster}' has been deleted.")
            update_all_option_menus()
    tk.Button(tab6, text="Delete Cluster", command=do_delete, font=default_font, width=20).grid(row=2, column=0, columnspan=4, pady=10)
    
    # --- Bottom Frame: Save to File and Save & Close Buttons ---
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(pady=10)
    
    def save_to_file():
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({k: list(v) for k, v in cluster_dict.items()}, f, indent=2)
                messagebox.showinfo("Success", f"Clusters saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    save_file_button = tk.Button(bottom_frame, text="Save to File", command=save_to_file, font=default_font, width=25)
    save_file_button.pack(side=tk.LEFT, padx=10)
    
    def on_save_close():
        root.destroy()
    
    save_close_button = tk.Button(bottom_frame, text="Close", command=on_save_close, font=default_font, width=25)
    save_close_button.pack(side=tk.LEFT, padx=10)
    
    update_all_option_menus()
    root.mainloop()

# Open the cluster editor window
open_cluster_editor()

print("Updated cluster_dict:\n")
print(cluster_dict)
