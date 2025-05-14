import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np

class CameraAppWithKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera with Virtual Keyboard")
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.width, self.height = 640, 480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Main frames
        self.camera_frame = ttk.Frame(root)
        self.camera_frame.pack(side=tk.TOP, padx=10, pady=10)
        
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(side=tk.TOP, padx=10, pady=10)
        
        # Camera display
        self.canvas = tk.Canvas(self.camera_frame, width=self.width, height=self.height)
        self.canvas.pack()
        
        # Text entry
        self.text_var = tk.StringVar()
        self.entry = ttk.Entry(self.control_frame, textvariable=self.text_var, width=50, font=('Arial', 14))
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Keyboard button
        self.keyboard_btn = ttk.Button(self.control_frame, text="⌨", 
                                     command=self.toggle_keyboard)
        self.keyboard_btn.pack(side=tk.LEFT, padx=5)
        
        # Capture button
        self.capture_btn = ttk.Button(self.control_frame, text="Capture", 
                                     command=self.capture_image)
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # Keyboard variables
        self.keyboard_window = None
        self.shift_pressed = False
        
        # Start camera update
        self.update_camera()
    
    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.img = Image.fromarray(self.frame)
            self.img_tk = ImageTk.PhotoImage(image=self.img)
            
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        
        self.root.after(10, self.update_camera)
    
    def capture_image(self):
        if hasattr(self, 'frame'):
            # Add text to the image if any
            text = self.text_var.get()
            if text:
                frame_with_text = self.frame.copy()
                cv2.putText(frame_with_text, text, (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                self.img = Image.fromarray(frame_with_text)
            else:
                self.img = Image.fromarray(self.frame)
            
            # Save the image
            filename = f"capture_{len(dir(self))}.png"
            self.img.save(filename)
            print(f"Image saved as {filename}")
    
    def toggle_keyboard(self):
        if self.keyboard_window and self.keyboard_window.winfo_exists():
            self.keyboard_window.destroy()
            self.keyboard_window = None
        else:
            self.keyboard_window = VirtualKeyboard(self.root, self.text_var)
    
    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

class VirtualKeyboard:
    def __init__(self, root, target_entry):
        self.root = root
        self.target_entry = target_entry
        self.shift_pressed = False
        
        # Create keyboard window
        self.keyboard_window = tk.Toplevel(root)
        self.keyboard_window.title("Virtual Keyboard")
        self.keyboard_window.resizable(False, False)
        
        # Keyboard layout
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '⌫'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '⏎'],
            ['⇧', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '⇧'],
            [' ', 'Esc']
        ]
        
        self.shift_keys = [
            ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '⌫'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '⏎'],
            ['⇧', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', '⇧'],
            [' ', 'Esc']
        ]
        
        self.create_keyboard()
    
    def create_keyboard(self):
        for row in self.shift_keys if self.shift_pressed else self.keys:
            row_frame = ttk.Frame(self.keyboard_window)
            row_frame.pack()
            
            for key in row:
                if key == '⇧':
                    btn = ttk.Button(row_frame, text=key, width=3,
                                   command=self.toggle_shift)
                elif key == '⌫':
                    btn = ttk.Button(row_frame, text=key, width=3,
                                   command=self.backspace)
                elif key == '⏎':
                    btn = ttk.Button(row_frame, text=key, width=3,
                                   command=self.return_key)
                elif key == ' ':
                    btn = ttk.Button(row_frame, text=key, width=20,
                                   command=lambda k=key: self.key_press(k))
                elif key == 'Esc':
                    btn = ttk.Button(row_frame, text=key, width=3,
                                   command=self.keyboard_window.destroy)
                else:
                    btn = ttk.Button(row_frame, text=key, width=3,
                                   command=lambda k=key: self.key_press(k))
                
                btn.pack(side=tk.LEFT, padx=1, pady=1)
    
    def toggle_shift(self):
        self.shift_pressed = not self.shift_pressed
        # Clear and recreate keyboard with new state
        for widget in self.keyboard_window.winfo_children():
            widget.destroy()
        self.create_keyboard()
    
    def key_press(self, key):
        current = self.target_entry.get()
        
        if self.shift_pressed and key.isalpha():
            key = key.upper()
            self.shift_pressed = False
            self.toggle_shift()  # This will update the keyboard
        
        self.target_entry.set(current + key)
    
    def backspace(self):
        current = self.target_entry.get()
        self.target_entry.set(current[:-1])
    
    def return_key(self):
        current = self.target_entry.get()
        self.target_entry.set(current + '\n')

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraAppWithKeyboard(root)
    root.mainloop()