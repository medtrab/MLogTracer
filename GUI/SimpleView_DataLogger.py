import tkinter as tk
from tkinter import messagebox, ttk
import asyncio
import websockets
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading

class WebSocketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Data Monitor")
        self.root.geometry("600x500")  # Set a default size for the window
        
        # WebSocket variables
        self.ws = None
        self.is_connected = False

        # GUI Components
        self.ip_label = tk.Label(root, text="IP:")
        self.ip_label.pack(padx=2)
        self.ip_entry = tk.Entry(root)
        self.ip_entry.pack(pady=5)

        self.port_label = tk.Label(root, text="Port:")
        self.port_label.pack(padx=2)
        self.port_entry = tk.Entry(root)
        self.port_entry.pack(pady=5)

        # Add ESP32 button with an icon (replace with your icon path)
        self.add_esp32_icon = tk.PhotoImage(file="add_esp32_icon.png").subsample(2)   # Add your icon file path

        self.add_esp32_button = tk.Button(root, image=self.add_esp32_icon, command=self.connect_to_server)
        self.add_esp32_button.pack(pady=5)

        # Connection status label
        self.status_label = tk.Label(root, text="Status: Not Connected", fg="red", font=('Helvetica', 12))
        self.status_label.pack(pady=5)


        self.data_label = tk.Label(root, text="Data to display:")
        self.data_label.pack(pady=5)

        self.data_checkboxes_frame = tk.Frame(root)
        self.data_checkboxes_frame.pack(pady=5)

        self.display_button = tk.Button(root, text="Display Data", command=self.start_display)
        self.display_button.pack(pady=5)

        self.display_options = tk.StringVar()
        self.display_list_radio = tk.Radiobutton(root, text="Display as List", variable=self.display_options, value="list")
        self.display_list_radio.pack(pady=5)

        self.display_chart_radio = tk.Radiobutton(root, text="Display as Chart", variable=self.display_options, value="chart")
        self.display_chart_radio.pack(pady=5)
        
        # Add a radio button for selecting single/multiple item display
        self.display_mode = tk.StringVar()
        self.single_radio = tk.Radiobutton(root, text="Single Item", variable=self.display_mode, value="single")
        self.single_radio.pack(pady=5)

        self.multiple_radio = tk.Radiobutton(root, text="Multiple Items", variable=self.display_mode, value="multiple")
        self.multiple_radio.pack(pady=5)

        self.display_mode.set("multiple")  # Default to multiple items


        self.display_options.set("list")  # Default option

        self.data_checkboxes = {}
        self.data_values = []
        self.data_timestamps = []
        self.selected_data = []

        # Variables for real-time chart display
        self.fig = None
        self.ax = None
        self.canvas = None
        self.chart_window = None
        self.list_window = None
        self.text_area = None

    def connect_to_server(self):
        ip = self.ip_entry.get().strip()  # Strip any leading/trailing whitespace from IP
        port = self.port_entry.get().strip()  # Strip any leading/trailing whitespace from Port

        if not ip or not port:
            messagebox.showerror("Error", "Please enter both IP and Port.")
            return
        
        try:
            port = int(port)  # Convert port to an integer after stripping whitespace
            # Start WebSocket connection on a separate thread
            threading.Thread(target=self.run_websocket, args=(ip, port), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid number.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))



    async def websocket_handler(self, ip, port):
        try:
            uri = f"ws://{ip}:{port}"
            async with websockets.connect(uri) as websocket:
                self.ws = websocket
                self.is_connected = True
                self.update_status(self.is_connected)
                messagebox.showinfo("Connected", f"Connected to {uri}")
                await self.receive_data()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            
    def update_status(self, connected):
        """Update the status label color and text."""
        if connected:
            self.status_label.config(text="Status: Connected", fg="green")
        else:
            self.status_label.config(text="Status: Not Connected", fg="red")

    async def receive_data(self):
        while self.is_connected:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                self.handle_received_data(data)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.is_connected = False
                break

    def handle_received_data(self, data):
        # Extract data from the "DataToSend" field in the JSON
        if "DataToSend" not in data:
            return

        data_to_send = data["DataToSend"]
        
        # Iterate over each category (e.g., Weather, System)
        for category_data in data_to_send:
            for category, values in category_data.items():
                # Iterate over the key-value pairs within each category
                for value_dict in values:
                    for key, value in value_dict.items():
                        # Create checkboxes dynamically for each key if not already created
                        if key not in self.data_checkboxes:
                            var = tk.BooleanVar()
                            checkbox = tk.Checkbutton(self.data_checkboxes_frame, text=key, variable=var)
                            checkbox.grid(sticky='w', padx=5, pady=5)
                            self.data_checkboxes[key] = var
        self.data_values.append(data_to_send)
        self.data_timestamps.append(datetime.now().strftime("%H:%M:%S"))

        # Update list and chart in real time
        if self.display_options.get() == "list" and self.list_window:
            self.update_list_view()
        elif self.display_options.get() == "chart" and self.chart_window:
            self.update_chart_view()

    def run_websocket(self, ip, port):
        asyncio.run(self.websocket_handler(ip, port))

    def start_display(self):
        self.selected_data = [key for key, var in self.data_checkboxes.items() if var.get()]
        
        if not self.selected_data:
            messagebox.showerror("Error", "Please select at least one data field to display.")
            return

        if self.display_options.get() == "list":
            self.open_list_view()
        else:
            # For chart view, check the display mode (single or multiple items)
            if self.display_mode.get() == "single":
                # Open single chart window with the first selected item
                self.open_chart_view(single_item=True)
            else:
                # Open separate chart windows for each selected item in "Multiple Items" mode
                for key in self.selected_data:
                    self.open_chart_view(single_item=False, specific_key=key)


    def open_list_view(self):
        if self.list_window is not None:  # Prevent opening multiple windows
            return

        self.list_window = tk.Toplevel(self.root)
        self.list_window.title("Data List")
        self.text_area = tk.Text(self.list_window)
        self.text_area.pack(expand=True, fill='both')

        # Handle window close event
        self.list_window.protocol("WM_DELETE_WINDOW", self.on_list_window_close)

        self.update_list_view()

    def on_list_window_close(self):
        """Handle the list window being closed."""
        self.list_window.destroy()
        self.list_window = None
        self.text_area = None  # Clear the reference to the text area


    def update_list_view(self):
        if self.text_area is None or not self.list_window:  # Check if window is still open
            return  # Safely exit if the window is closed

        self.text_area.delete(1.0, tk.END)  # Clear previous content

        for i, data_list in enumerate(self.data_values):
            timestamp = self.data_timestamps[i]
            for category_data in data_list:
                for category, values in category_data.items():
                    for value_dict in values:
                        display_line = f"{timestamp}: " + ", ".join([f"{key}: {value_dict[key]}" for key in self.selected_data if key in value_dict])
                        self.text_area.insert(tk.END, display_line + "\n")


    def open_chart_view(self, single_item=True, specific_key=None):
        # Create a new chart window for each item (for multiple items mode)
        chart_window = tk.Toplevel(self.root)
        
        if single_item:
            chart_window.title(f"Data Chart - {self.selected_data[0]}")
        else:
            chart_window.title(f"Data Chart - {specific_key}")

        fig, ax = plt.subplots()

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.get_tk_widget().pack(expand=True, fill='both')

        # Update the chart with data, either for a single or multiple items
        self.update_chart_view(fig, ax, canvas, single_item, specific_key)

    def update_chart_view(self, fig, ax, canvas, single_item=True, specific_key=None):
        ax.clear()  # Clear previous data on the chart

        if single_item:
            # If single item mode is selected, plot only the first selected item
            key = self.selected_data[0]  # Display the first selected item
            values = self.get_data_values_for_key(key)
            ax.plot(self.data_timestamps, values, label=key)
        else:
            # For multiple items mode, plot only the specific key in the new window
            values = self.get_data_values_for_key(specific_key)
            ax.plot(self.data_timestamps, values, label=specific_key)

        # Set axis labels and title
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.legend()

        # Improve timestamp visibility: Rotate the labels and show only every nth timestamp
        num_ticks = len(self.data_timestamps)
        if num_ticks > 10:
            n = max(1, num_ticks // 10)
            ax.set_xticks(ax.get_xticks()[::n])
            ax.tick_params(axis='x', rotation=45)

        canvas.draw()  # Redraw the chart with updated data

    def get_data_values_for_key(self, key):
        """Helper method to extract data values for a specific key."""
        values = []
        for data_list in self.data_values:
            for category_data in data_list:
                for category, data_dicts in category_data.items():
                    for data_dict in data_dicts:
                        if key in data_dict:
                            values.append(data_dict[key])
        return values


    def on_chart_window_close(self):
        """Handle the chart window being closed."""
        self.chart_window.destroy()
        self.chart_window = None
        self.fig = None  # Clear the figure reference
        self.ax = None  # Clear the axis reference
        self.canvas = None  # Clear the canvas reference


    # def update_chart_view(self):
    #     if not self.ax or not self.canvas or not self.chart_window:
    #         return

    #     self.ax.clear()  # Clear previous data on the chart

    #     if self.display_mode.get() == "single":
    #         # If single item mode is selected, only display the first selected item
    #         if self.selected_data:
    #             key = self.selected_data[0]  # Only show the first selected item
    #             values = []
    #             for data_list in self.data_values:
    #                 for category_data in data_list:
    #                     for category, data_dicts in category_data.items():
    #                         for data_dict in data_dicts:
    #                             if key in data_dict:
    #                                 values.append(data_dict[key])

    #             self.ax.plot(self.data_timestamps, values, label=key)
    #     else:
    #         # If multiple item mode is selected, plot all selected items
    #         for key in self.selected_data:
    #             values = []
    #             for data_list in self.data_values:
    #                 for category_data in data_list:
    #                     for category, data_dicts in category_data.items():
    #                         for data_dict in data_dicts:
    #                             if key in data_dict:
    #                                 values.append(data_dict[key])

    #             self.ax.plot(self.data_timestamps, values, label=key)

    #     # Set axis labels and title
    #     self.ax.set_xlabel('Time')
    #     self.ax.set_ylabel('Value')
    #     self.ax.legend()

    #     # Improve timestamp visibility: Rotate the labels and show only every nth timestamp
    #     num_ticks = len(self.data_timestamps)
    #     if num_ticks > 10:
    #         n = max(1, num_ticks // 10)
    #         self.ax.set_xticks(self.ax.get_xticks()[::n])
    #         self.ax.tick_params(axis='x', rotation=45)

    #     self.canvas.draw()  # Redraw the chart with updated data



# Main program
if __name__ == "__main__":
    root = tk.Tk()
    app = WebSocketGUI(root)
    root.mainloop()
