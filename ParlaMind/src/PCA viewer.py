import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta

# Load your data (replace with actual data)
final_df = pd.read_parquet("PCA.parquet")  # Your data source
final_df['date'] = pd.to_datetime(final_df['date'])

# Date calculations
min_date = final_df['date'].min()
max_date = final_df['date'].max()
total_days = (max_date - min_date).days + 1

class DateSliderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PCA Analysis with Triple Sliders")
        
        # Initialize data
        self.df = final_df
        self.block_slider_events = False
        
        # Setup UI
        self.create_widgets()
        self.setup_sliders()
        self.update_plot()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Center point checkbox
        self.show_center_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Show Center (0,0)", variable=self.show_center_var,
                        command=self.update_plot).pack(anchor=tk.W, pady=5)

        # Party checkboxes
        ttk.Label(control_frame, text="Select Parties:").pack(anchor=tk.W)
        self.party_vars = {}
        
        canvas = tk.Canvas(control_frame, height=200)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for party in self.df['abbreviation'].unique():
            self.party_vars[party] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.scrollable_frame, text=party, variable=self.party_vars[party],
                                command=self.update_plot)
            cb.pack(anchor=tk.W)
            
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Plot area
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_sliders(self):
        # Slider container
        slider_frame = ttk.LabelFrame(self.root, text="Date Control")
        slider_frame.pack(fill=tk.X, padx=10, pady=5)

        # Start Date slider
        ttk.Label(slider_frame, text="Start Date:").pack(anchor=tk.W)
        self.start_slider = ttk.Scale(slider_frame, from_=0, to=total_days-1, 
                                    orient=tk.HORIZONTAL, command=lambda v: self.update_sliders('start'))
        self.start_slider.pack(fill=tk.X, padx=5, pady=2)

        # End Date slider
        ttk.Label(slider_frame, text="End Date:").pack(anchor=tk.W)
        self.end_slider = ttk.Scale(slider_frame, from_=0, to=total_days-1, 
                                  orient=tk.HORIZONTAL, command=lambda v: self.update_sliders('end'))
        self.end_slider.set(total_days-1)
        self.end_slider.pack(fill=tk.X, padx=5, pady=2)

        # Window Position slider
        ttk.Label(slider_frame, text="Window Position:").pack(anchor=tk.W)
        self.window_slider = ttk.Scale(slider_frame, from_=0, to=0, 
                                     orient=tk.HORIZONTAL, command=lambda v: self.update_sliders('window'))
        self.window_slider.pack(fill=tk.X, padx=5, pady=2)

        # Date labels
        self.date_labels = ttk.Label(slider_frame, text="")
        self.date_labels.pack(pady=5)

    def update_sliders(self, source):
        if self.block_slider_events:
            return

        self.block_slider_events = True
        try:
            # Get current values
            start = int(round(float(self.start_slider.get())))
            end = int(round(float(self.end_slider.get())))
            window_pos = int(round(float(self.window_slider.get())))

            # Calculate window length
            window_length = end - start + 1
            
            if source == 'start':
                # Constrain end slider
                end = max(start, end)
                self.end_slider.set(end)
                # Update window slider
                self.window_slider.set(start)
                
            elif source == 'end':
                # Constrain start slider
                start = min(start, end)
                self.start_slider.set(start)
                # Update window slider
                self.window_slider.set(start)
                
            elif source == 'window':
                # Calculate new positions
                new_start = max(0, min(window_pos, total_days - window_length))
                new_end = new_start + window_length - 1
                self.start_slider.set(new_start)
                self.end_slider.set(new_end)
                start, end = new_start, new_end

            # Update window slider constraints
            window_length = end - start + 1
            max_window_pos = total_days - window_length
            self.window_slider.config(to=max(0, max_window_pos))
            self.window_slider.set(start)

            # Update date labels
            start_date = min_date + timedelta(days=start)
            end_date = min_date + timedelta(days=end)
            self.date_labels.config(
                text=f"Selected Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            )

            # Update plot
            self.update_plot()

        finally:
            self.block_slider_events = False

    def update_plot(self):
        try:
            # Get current parameters
            start = int(self.start_slider.get())
            end = int(self.end_slider.get())
            selected_parties = [p for p, var in self.party_vars.items() if var.get()]
            
            # Calculate date range
            start_date = min_date + timedelta(days=start)
            end_date = min_date + timedelta(days=end)
            
            # Filter data
            mask = (
                (self.df['abbreviation'].isin(selected_parties)) &
                (self.df['date'] >= start_date) &
                (self.df['date'] <= end_date))
            filtered_df = self.df[mask]
            
            # Calculate means
            grouped_means = filtered_df.groupby("abbreviation")[["PC1", "PC2"]].mean().reset_index()

            # Update plot
            self.ax.clear()
            
            # Plot parties
            self.ax.scatter(grouped_means["PC1"], grouped_means["PC2"], s=100)
            
            # Plot center point if enabled
            if self.show_center_var.get():
                self.ax.scatter(0, 0, s=100, c='red', marker='x', label='Center (0,0)')
            
            # Annotate points
            for _, row in grouped_means.iterrows():
                self.ax.annotate(row["abbreviation"], (row["PC1"], row["PC2"]),
                               textcoords="offset points", xytext=(5,5), ha='center')
            
            self.ax.set_xlabel("PC1")
            self.ax.set_ylabel("PC2")
            self.ax.set_title(f"PCA Analysis ({start_date.date()} to {end_date.date()})")
            
            if self.show_center_var.get():
                self.ax.legend()
            
            self.canvas.draw()
            
        except Exception as e:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DateSliderApp(root)
    root.mainloop()