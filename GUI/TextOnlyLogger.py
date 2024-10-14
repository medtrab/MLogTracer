import tkinter as tk
from tkinter import filedialog, messagebox
import datetime
import asyncio
import websockets
import threading

class ESP32MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Data Monitor")
        self.root.geometry("600x500")  # Set a default size for the window

        # IP Address entry field
        self.ip_label = tk.Label(root, text="ESP32 IP Address:")
        self.ip_label.pack(pady=5)

        self.ip_entry = tk.Entry(root, width=20)
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, "ws://")  # Default WebSocket prefix

        # Add ESP32 button with an icon (replace with your icon path)
        self.add_esp32_icon = tk.PhotoImage(file="add_esp32_icon.png").subsample(2)   # Add your icon file path

        self.add_esp32_button = tk.Button(root, image=self.add_esp32_icon, command=self.connect_esp32)
        self.add_esp32_button.pack(pady=10)

        # Connection status label
        self.status_label = tk.Label(root, text="Status: Not Connected", fg="red", font=('Helvetica', 12))
        self.status_label.pack(pady=5)
        # Save data button
        self.save_button = tk.Button(root, text="Save Data", command=self.save_data)
        self.save_button.pack(pady=5)
        # Text area for displaying data
        self.text_area = tk.Text(root, height=20, width=120)
        self.text_area.pack(pady=10)

        

        # Data buffer and websocket variables
        self.data_buffer = []
        self.websocket = None
        self.running = True
        self.new_data = False  # Flag to indicate when new data has arrived

    def display_data(self, message):
        """Display message with a timestamp in the text area."""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        display_message = f"[{timestamp}] {message}\n"
        self.text_area.insert(tk.END, display_message)
        self.text_area.see(tk.END)
        
        # Add to the buffer for saving later
        self.data_buffer.append(display_message)
        self.new_data = True

    def save_data(self):
        """Save the buffered data to a .txt file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.writelines(self.data_buffer)

    async def websocket_handler(self, uri):
        """Handles receiving data from ESP32 via WebSocket."""
        try:
            self.websocket = await websockets.connect(uri)
            self.update_status(connected=True)
            while self.running:
                try:
                    message = await self.websocket.recv()  # Receive the message
                    self.display_data(message)
                    await asyncio.sleep(0.1)  # Add a small delay (0.1 seconds)
                except websockets.ConnectionClosedOK:
                    print("Connection closed gracefully.")
                    break
                except websockets.ConnectionClosedError as e:
                    print(f"Connection error: {e}")
                    break
        except Exception as e:
            self.update_status(connected=False)
            messagebox.showerror("Connection Error", f"Could not connect to ESP32: {e}")

    def update_status(self, connected):
        """Update the status label color and text."""
        if connected:
            self.status_label.config(text="Status: Connected", fg="green")
        else:
            self.status_label.config(text="Status: Not Connected", fg="red")

    def connect_esp32(self):
        """Connect to the ESP32 asynchronously in a separate thread."""
        esp32_ip = self.ip_entry.get().strip()
        if esp32_ip:
            threading.Thread(target=self.start_websocket, args=(esp32_ip,), daemon=True).start()
        else:
            messagebox.showerror("Input Error", "Please enter a valid ESP32 IP address")

    def start_websocket(self, ip_address):
        """Run the WebSocket handler asynchronously."""
        asyncio.run(self.websocket_handler(ip_address))

    def check_for_new_data(self):
        """Periodically check for new data to avoid GUI freezing."""
        if self.new_data:
            self.text_area.update_idletasks()  # Ensure the text area updates
            self.new_data = False
        self.root.after(100, self.check_for_new_data)  # Recheck every 100 ms

    def stop(self):
        """Stop the WebSocket connection and Tkinter loop."""
        self.running = False
        if self.websocket is not None:
            asyncio.run(self.websocket.close())  # Close the WebSocket connection gracefully
        self.root.quit()

# Setup the GUI application
root = tk.Tk()
app = ESP32MonitorApp(root)

# Ensure graceful stop on window close
root.protocol("WM_DELETE_WINDOW", app.stop)

# Periodically check for new data to avoid freezing
app.check_for_new_data()

root.mainloop()
