"""
RFID Cloner Studio - Desktop GUI Application

Step-by-step interface for duplicating 13.56MHz RFID tags via Arduino + MFRC522.
"""

import customtkinter as ctk
from typing import Optional
import serial
import serial.tools.list_ports
import json
import time
from tkinter import messagebox


class SerialManager:
    """Handles serial communication with Arduino."""
    
    def __init__(self):
        self.connection: Optional[serial.Serial] = None
        self.port: Optional[str] = None
    
    def find_arduino(self) -> Optional[str]:
        """
        Scan available COM ports and identify Arduino.
        Return port name or None if not found.
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "FTDI" in port.description or "CH340" in port.description:
                return port.device
        return None
    
    def get_available_ports(self) -> list[str]:
        """Return list of available COM port names."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Establish serial connection to Arduino."""
        try:
            self.connection = serial.Serial(port, baudrate, timeout=2)
            self.port = port
            # Wait for Arduino reset
            time.sleep(2)
            return True
        except serial.SerialException:
            self.connection = None
            self.port = None
            return False
    
    def send_command(self, command: str) -> str:
        """
        Send command to Arduino and wait for response.
        Commands: CHECK_HW, READ_UID, WRITE_UID:XXXX
        """
        if not self.connection or not self.connection.is_open:
            return '{"status": "ERROR", "message": "Not connected"}'
        
        try:
            # Clear input buffer
            self.connection.reset_input_buffer()
            # Write command
            self.connection.write((command + "\n").encode())
            # Read response with timeout
            self.connection.timeout = 5
            response = self.connection.readline().decode().strip()
            return response if response else '{"status": "ERROR", "message": "No response"}'
        except serial.SerialException as e:
            return f'{{"status": "ERROR", "message": "{str(e)}"}}'
    
    def disconnect(self):
        """Close serial connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
        self.connection = None
        self.port = None
    
    def is_connected(self) -> bool:
        """Check if serial connection is active."""
        return self.connection is not None and self.connection.is_open


class RFIDClonerApp(ctk.CTk):
    """Main application window with step-by-step cloning workflow."""
    
    def __init__(self):
        super().__init__()
        self.serial = SerialManager()
        self.source_uid: Optional[str] = None
        self.source_type: Optional[str] = None
        
        # Configure window
        self.title("RFID Cloner Studio")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.create_ui()
    
    def create_ui(self):
        """Build the GUI with step-by-step workflow."""
        # Main container with padding
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="🔐 RFID Cloner Studio",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # === Connection Frame ===
        self.conn_frame = ctk.CTkFrame(self.main_frame)
        self.conn_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(self.conn_frame, text="Connection", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        conn_row = ctk.CTkFrame(self.conn_frame, fg_color="transparent")
        conn_row.pack(fill="x", padx=10, pady=(0, 10))
        
        self.port_var = ctk.StringVar(value="Select Port")
        self.port_dropdown = ctk.CTkOptionMenu(
            conn_row,
            variable=self.port_var,
            values=["Select Port"],
            command=self.on_port_selected,
            width=150
        )
        self.port_dropdown.pack(side="left", padx=(0, 10))
        
        self.refresh_btn = ctk.CTkButton(conn_row, text="🔄", width=40, command=self.refresh_ports)
        self.refresh_btn.pack(side="left", padx=(0, 10))
        
        self.connect_btn = ctk.CTkButton(conn_row, text="Connect", width=100, command=self.connect_device)
        self.connect_btn.pack(side="left", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(conn_row, text="● Disconnected", text_color="red")
        self.status_label.pack(side="left")
        
        # === Step 1 Frame ===
        self.step1_frame = ctk.CTkFrame(self.main_frame)
        self.step1_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            self.step1_frame,
            text="Step 1: Tap Original Key",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            self.step1_frame,
            text="Place the original RFID card/fob on the reader",
            text_color="gray"
        ).pack(anchor="w", padx=10)
        
        self.read_btn = ctk.CTkButton(
            self.step1_frame,
            text="📖 Read Card",
            command=self.read_source_card,
            state="disabled",
            height=40
        )
        self.read_btn.pack(pady=10, padx=10, fill="x")
        
        self.source_info_label = ctk.CTkLabel(
            self.step1_frame,
            text="No card read yet",
            text_color="gray"
        )
        self.source_info_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # === Step 2 Frame ===
        self.step2_frame = ctk.CTkFrame(self.main_frame)
        self.step2_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            self.step2_frame,
            text="Step 2: Tap Virgin Tag",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            self.step2_frame,
            text="Place a writable blank tag on the reader",
            text_color="gray"
        ).pack(anchor="w", padx=10)
        
        self.write_btn = ctk.CTkButton(
            self.step2_frame,
            text="✍️ Write Card",
            command=self.write_target_card,
            state="disabled",
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.write_btn.pack(pady=10, padx=10, fill="x")
        
        self.write_info_label = ctk.CTkLabel(
            self.step2_frame,
            text="Read a source card first",
            text_color="gray"
        )
        self.write_info_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # === Log Frame ===
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.log_frame, text="Log", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(self.log_frame, height=120)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Initial port scan
        self.refresh_ports()
    
    def log(self, message: str):
        """Append message to log text area."""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
    
    def refresh_ports(self):
        """Scan and populate COM port dropdown."""
        ports = self.serial.get_available_ports()
        if ports:
            self.port_dropdown.configure(values=ports)
            self.port_var.set(ports[0])
            self.log(f"Found {len(ports)} port(s): {', '.join(ports)}")
        else:
            self.port_dropdown.configure(values=["No ports found"])
            self.port_var.set("No ports found")
            self.log("No COM ports found")
    
    def on_port_selected(self, port_name: str):
        """Handle port selection from dropdown - auto-connect."""
        if port_name and port_name != "No ports found" and port_name != "Select Port":
            self.log(f"Selected port: {port_name}")
    
    def connect_device(self):
        """Toggle connect/disconnect for Arduino device."""
        if self.serial.is_connected():
            # Disconnect
            self.serial.disconnect()
            self.connect_btn.configure(text="Connect")
            self.status_label.configure(text="● Disconnected", text_color="red")
            self.read_btn.configure(state="disabled")
            self.write_btn.configure(state="disabled")
            self.log("Disconnected from device")
        else:
            # Connect
            port = self.port_var.get()
            if port and port not in ["No ports found", "Select Port"]:
                self.log(f"Connecting to {port}...")
                self.update()
                
                if self.serial.connect(port):
                    self.connect_btn.configure(text="Disconnect")
                    self.status_label.configure(text="● Connected", text_color="green")
                    self.read_btn.configure(state="normal")
                    self.log(f"Connected to {port}")
                    self.check_hardware()
                else:
                    self.log(f"Failed to connect to {port}")
                    messagebox.showerror("Connection Error", f"Could not connect to {port}")
    
    def check_hardware(self):
        """Send CHECK_HW command to verify MFRC522 is working."""
        self.log("Checking hardware...")
        response = self.serial.send_command("CHECK_HW")
        
        try:
            data = json.loads(response)
            status = data.get("status", "ERROR")
            message = data.get("message", "Unknown")
            
            if status == "READY":
                self.status_label.configure(text="● Ready", text_color="green")
                self.log(f"Hardware OK: {message}")
            else:
                self.status_label.configure(text="● HW Error", text_color="orange")
                self.log(f"Hardware Error: {message}")
                messagebox.showwarning("Hardware Warning", f"MFRC522 issue: {message}")
        except json.JSONDecodeError:
            self.log(f"Raw response: {response}")
            self.status_label.configure(text="● Connected", text_color="green")
    
    def read_source_card(self):
        """Step 1: Read UID from source card."""
        self.read_btn.configure(state="disabled", text="Reading...")
        self.source_info_label.configure(text="Scanning...", text_color="yellow")
        self.update()
        
        self.log("Reading card... Place card on reader")
        response = self.serial.send_command("READ_UID")
        
        try:
            data = json.loads(response)
            status = data.get("status", "ERROR")
            
            if status == "SUCCESS":
                self.source_uid = data.get("uid", "")
                self.source_type = data.get("type", "Unknown")
                
                self.source_info_label.configure(
                    text=f"✓ UID: {self.source_uid} | Type: {self.source_type}",
                    text_color="green"
                )
                self.write_btn.configure(state="normal")
                self.write_info_label.configure(text="Ready to write", text_color="yellow")
                self.log(f"Read successful - UID: {self.source_uid}")
                messagebox.showinfo("Success", f"Card read successfully!\nUID: {self.source_uid}")
            else:
                error_msg = data.get("message", "Failed to read card")
                self.source_info_label.configure(text=f"✗ {error_msg}", text_color="red")
                self.log(f"Read failed: {error_msg}")
                messagebox.showerror("Read Error", error_msg)
        except json.JSONDecodeError:
            # Handle non-JSON response (legacy format: UID|Type)
            if "|" in response:
                parts = response.split("|")
                self.source_uid = parts[0]
                self.source_type = parts[1] if len(parts) > 1 else "Unknown"
                
                self.source_info_label.configure(
                    text=f"✓ UID: {self.source_uid} | Type: {self.source_type}",
                    text_color="green"
                )
                self.write_btn.configure(state="normal")
                self.log(f"Read successful - UID: {self.source_uid}")
            else:
                self.source_info_label.configure(text=f"✗ Error: {response}", text_color="red")
                self.log(f"Read error: {response}")
        
        self.read_btn.configure(state="normal", text="📖 Read Card")
    
    def write_target_card(self):
        """Step 2: Write UID to target card."""
        if not self.source_uid:
            messagebox.showwarning("No Source", "Please read a source card first!")
            return
        
        # Confirm before writing
        confirm = messagebox.askyesno(
            "Confirm Write",
            f"Write UID {self.source_uid} to target card?\n\nThis may be irreversible on some tags."
        )
        if not confirm:
            return
        
        self.write_btn.configure(state="disabled", text="Writing...")
        self.write_info_label.configure(text="Writing...", text_color="yellow")
        self.update()
        
        self.log(f"Writing UID {self.source_uid}... Place blank tag on reader")
        response = self.serial.send_command(f"WRITE_UID:{self.source_uid}")
        
        try:
            data = json.loads(response)
            status = data.get("status", "ERROR")
            
            if status == "SUCCESS":
                self.write_info_label.configure(text="✓ Write successful!", text_color="green")
                self.log("Write successful!")
                messagebox.showinfo("Success", "Card cloned successfully!")
            elif status == "ERROR_LOCKED":
                self.write_info_label.configure(text="✗ Card is locked/not writable", text_color="red")
                self.log("Write failed: Card is locked")
                messagebox.showerror("Write Error", "This card is locked and cannot be written to.\nTry a different blank card.")
            else:
                error_msg = data.get("message", "Write failed")
                self.write_info_label.configure(text=f"✗ {error_msg}", text_color="red")
                self.log(f"Write failed: {error_msg}")
                messagebox.showerror("Write Error", error_msg)
        except json.JSONDecodeError:
            if "SUCCESS" in response.upper():
                self.write_info_label.configure(text="✓ Write successful!", text_color="green")
                self.log("Write successful!")
                messagebox.showinfo("Success", "Card cloned successfully!")
            else:
                self.write_info_label.configure(text=f"✗ {response}", text_color="red")
                self.log(f"Write error: {response}")
                messagebox.showerror("Write Error", response)
        
        self.write_btn.configure(state="normal", text="✍️ Write Card")


def main():
    """Application entry point."""
    app = RFIDClonerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
