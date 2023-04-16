import os
import random
import time
import openpyxl
import sys
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, Entry, Label, Button, OptionMenu
import cv2
from PIL import Image, ImageTk
import vlc
import pyautogui

class ExperimentApp:
    def __init__(self):
        # Initialize variables and setup GUI
        self.window = Tk()
        self.window.title("Legibility Study")
        self.window.geometry("800x600")
        self.window.configure(bg="white")
        
        self.name = StringVar()
        self.gender = StringVar()
        self.age = IntVar()

        self.user_data = []
        self.responses = []

        self.video_folder_path = "C:/Users/kevin/Documents/MS_S23/CS7633_HRI/7633_Legibility_Proj/test_videos"
        self.video_files = []
        self.load_video_files()
        self.spacebar_press_times = []
        self.reaction_times = []
        self.current_video = None
        self.start_time = None
        self.results = []

        # Start the experiment
        self.main_page()
        self.window.mainloop()

    def load_video_files(self):
        for filename in os.listdir(self.video_folder_path):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
                self.video_files.append(os.path.join(self.video_folder_path, filename))

    def main_page(self):
        # Create the main landing page interface
        self.window.bind("<Escape>", lambda e: self.window.destroy())  # Close the app with the Esc key

        # Create a grid layout and configure rows and columns to have a weight of 1
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(2, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(4, weight=1)

        # Create form labels and fields
        name_label = Label(self.window, text="Name:", bg="white")
        name_entry = Entry(self.window, textvariable=self.name)
        gender_label = Label(self.window, text="Gender:", bg="white")
        gender_menu = OptionMenu(self.window, self.gender, "Male", "Female", "Non-binary", "Other")
        age_label = Label(self.window, text="Age:", bg="white")
        age_entry = Entry(self.window, textvariable=self.age)

        # Place form labels and fields on the window
        name_label.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        name_entry.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        gender_label.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        gender_menu.grid(row=2, column=2, padx=10, pady=10, sticky="w")
        age_label.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        age_entry.grid(row=3, column=2, padx=10, pady=10, sticky="w")

        # Create and place the "Next" button
        next_button = Button(self.window, text="Next", command=self.instructions_page)
        next_button.grid(row=4, column=1, columnspan=3, pady=20)

    def instructions_page(self):
        # Clear the window
        for widget in self.window.grid_slaves():
            widget.grid_forget()

        # Create the instructions text
        instructions_text = Text(self.window, wrap="word", height=10, width=50, padx=10, pady=10, bg="white")
        instructions_text.insert("1.0", "Please read the following instructions carefully...\n\n"
                                      "1. When you click 'Start', a video will play automatically.\n"
                                      "2. As soon as the video starts, press the spacebar when you see something "
                                      "interesting.\n"
                                      "3. You will then see two buttons, 'Green' and 'Red'.\n"
                                      "4. Choose one of the buttons based on your decision.\n"
                                      "5. The process will repeat with a new video 8 times.\n\n"
                                      "Click 'Start' to begin the experiment.")
        instructions_text.config(state="disabled")  # Make the text read-only
        instructions_text.grid(row=0, column=0, padx=20, pady=20)

        # Create and place the "Start" button
        start_button = Button(self.window, text="Start", command=self.experiment_page)
        start_button.grid(row=1, column=0, pady=20)

    def experiment_page(self):
        # Clear the window
        for widget in self.window.grid_slaves():
            widget.grid_forget()

        # Create a canvas to display the video
        self.canvas = Canvas(self.window, bg="black", width=640, height=360)
        self.canvas.grid(row=0, column=0, padx=20, pady=20)

        # Create an invisible, transparent fullscreen window
        self.overlay = Toplevel(self.window)
        self.overlay.attributes("-fullscreen", True)
        self.overlay.attributes("-alpha", 0.0)  # Set window transparency to 0 (completely transparent)
        self.overlay.attributes("-topmost", True)
        self.overlay.bind("<KeyPress-space>", self.on_spacebar)
        self.overlay.focus_force()
        self.overlay.lift()  # Bring the overlay window to the top level

        self.play_video()

        # Find the current position of the mouse
        current_x, current_y = pyautogui.position()

        # Force click transparent overlay to bring into focus
        pyautogui.click(x=current_x, y=current_y)

        #reset mouse to original pos
        pyautogui.moveTo(x=current_x, y=current_y)


    def play_video(self):
        # Handle video playback and listen for spacebar press
        # Choose a random video from the folder
        video_path = random.choice(self.video_files)
        self.video_files.remove(video_path)  # Remove the video from the list so it doesn't get played again
        self.current_video = os.path.basename(video_path)  # Store the current video file name

        # Create a VLC instance and Media Player
        Instance = vlc.Instance()
        self.media_player = Instance.media_player_new()

        # Set the media to the media player
        Media = Instance.media_new(video_path)
        self.media_player.set_media(Media)

        # Set the media player's output to the canvas window
        self.media_player.set_fullscreen(True)
        self.media_player.set_xwindow(self.canvas.winfo_id())

        # Play the video
        self.media_player.play()
        time.sleep(0.1)  # Give the player some time to start

        # Start the timer
        self.start_time = time.time()

    def on_vlc_keypress(self, event):
        # Check if the pressed key is the spacebar
        if event.u.key == vlc.libvlc_key_code_t.space.value:
            # Calculate the reaction time
            reaction_time = time.time() - self.start_time 

            # Pause the video
            self.media_player.stop()

            # Show the decision screen
            self.response_page(reaction_time)

    def on_spacebar(self, event):
        # Calculate the reaction time
        reaction_time = time.time() - self.start_time

        # Pause the video
        self.media_player.stop()

        # Show the decision screen
        self.response_page(reaction_time)

    def response_page(self, reaction_time):
        # Destroy the overlay window
        self.overlay.destroy()
        # Clear the window
        for widget in self.window.grid_slaves():
            widget.grid_forget()

        # Set the window background to white
        self.window.configure(bg="white")

        # Create and place the buttons
        green_button = tk.Button(self.window, text="Green", bg="green", command=lambda: self.record_response('Green', reaction_time))
        red_button = tk.Button(self.window, text="Red", bg="red", command=lambda: self.record_response('Red', reaction_time))

        green_button.grid(row=0, column=0, padx=20, pady=20)
        red_button.grid(row=0, column=1, padx=20, pady=20)

    def record_response(self, response, reaction_time):
        # Record the reaction time and response
        self.results.append((self.current_video, reaction_time, response))

        # Check if the experiment is complete
        if len(self.results) >= 3:
            video_names, spacebar_times, button_responses = zip(*self.results)
            self.save_results(self.name.get(), self.gender.get(), self.age.get(), video_names, spacebar_times, button_responses)
            self.thank_you_screen()
        else:
            self.experiment_page()

    def save_results(self, name, gender, age, video_names, spacebar_times, button_responses):
        # Create a DataFrame with the data
        data = {
            "Name": [name] * len(video_names),
            "Gender": [gender] * len(video_names),
            "Age": [age] * len(video_names),
            "Video Name": video_names,
            "Time to Press Spacebar": spacebar_times,
            "Button Response": button_responses
        }
        df = pd.DataFrame(data)

        # Check if the results file exists
        results_file = "experiment_results.xlsx"
        try:
            existing_df = pd.read_excel(results_file, engine='openpyxl')
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=df.columns)

        # Append the new results to the existing DataFrame
        combined_df = existing_df.append(df, ignore_index=True)

        # Save the combined DataFrame to the Excel file
        combined_df.to_excel(results_file, index=False, engine='openpyxl')

        print("Results saved to", results_file)

    def run(self):
        # Display the main page and get user information
        name, gender, age = self.main_page()

        # Show the instructions page
        self.instructions_page()

        # Initialize lists to store experiment data
        video_names = []
        spacebar_times = []
        button_responses = []

        # Run the experiment 8 times
        for _ in range(3):
            # Display the experiment page and record the video name and time to press spacebar
            video_name, spacebar_time = self.experiment_page()
            video_names.append(video_name)
            spacebar_times.append(spacebar_time)

            # Display the response page and record the button response
            button_response = self.response_page()
            button_responses.append(button_response)

        # Save the results to an Excel file
        self.save_results(name, gender, age, video_names, spacebar_times, button_responses)

        # Show the Thank You screen with the option to restart the experiment
        self.thank_you_screen()

    def thank_you_screen(self):
        # Destroy all other windows
        for widget in self.window.winfo_children():
            if widget.winfo_class() != 'Toplevel':
                widget.destroy()

        # Create the thank you message, restart button, and exit button
        thank_you_label = Label(self.window, text="Thank you for participating in our study!", bg="white", font=("Helvetica", 20))
        restart_button = Button(self.window, text="Restart", command=self.main_page, bg="white", font=("Helvetica", 16))
        exit_button = Button(self.window, text="Exit", command=sys.exit(), bg="white", font=("Helvetica", 16))

        # Place the message and buttons on the window
        thank_you_label.pack(pady=50)
        restart_button.pack(pady=10)
        exit_button.pack(pady=10)


if __name__ == "__main__":
    app = ExperimentApp()
    # app.run()
    # app.window.mainloop()



