# Aud working memory task
# task by Chase M
# June 2024
# see github repo seemackey/Task_AudWM

from psychopy import visual, core, event, data, gui, sound
import os
from datetime import datetime
import csv
import numpy as np
import random
from Functions_WM import play_flash, load_stimuli_parameters, show_feedback
import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(0x80000002) # prevent WINDOWS machine from sleeping
import serial
from utils import generate_tone_sequence
port = serial.Serial("COM4",115200) # serial port and baud rate for dell xps laptop

# Constants

flash_rate = 1.6  # Hz
flash_period = 1 / flash_rate  # seconds per flash
flash_duration = 0.1  # flash on time in seconds
pre_stim_flashes = 0  # Number of flashes before first sequence
inter_sequence_flashes = 0  # Flashes between sequences
cue_duration = 0.5  # Duration of each tone sequence
inter_sequence_interval = inter_sequence_flashes * flash_period  # Interval between sequences
wm_delay = 0.3  # Delay between cue and choice sounds

# Set up experiment parameters via a GUI
info = {'Participant Name': ''}
dlg = gui.DlgFromDict(dictionary=info, title='Experiment Setup')
if not dlg.OK:
    core.quit()  # User pressed cancel
participant_name = info['Participant Name']
seed = 12345
csv_filename = 'soundslist.csv'

# Create a directory for data inside the current script's directory
data_folder = "data"
data_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_folder)
if not os.path.exists(data_folder_path):
    os.makedirs(data_folder_path)

# Generate the data file path
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
data_file_name = f"{participant_name}_{timestamp}.csv"
data_file_path = os.path.join(data_folder_path, data_file_name)

# Load monitor specifications
monitor_specs = {"screen_resolution": [800, 480], "monitor_width": 800, "full_screen": True}
screen_resolution = monitor_specs["screen_resolution"]
full_screen = monitor_specs["full_screen"]

# Window setup
win = visual.Window(
    size=screen_resolution,
    units="pix",
    fullscr=True,
    monitor="debugging_monitor",
    screen=1,  # Set this to 1 to use the second display
    waitBlanking=True
)


# Visual stimulus setup
box_size = 200  # Static box size
greenBox = visual.Rect(win, width=box_size, height=box_size, pos=(-300, 0), fillColor='green')
redBox = visual.Rect(win, width=box_size, height=box_size, pos=(300, 0), fillColor='red')
flash_stim = visual.Rect(win, size=(200, 200), pos=(0, 0), fillColor='white')
yellowBox = visual.Rect(win, width=box_size, height=box_size, pos=(0, 0), fillColor='yellow')
stimuli_parameters = load_stimuli_parameters(csv_filename)

# trial setup
try:
    trials = data.TrialHandler(stimuli_parameters, nReps=400, method='random')
except Exception as e:
    print(f"Error in initializing TrialHandler: {e}")
    core.quit()
# Create a mouse object
mouse = event.Mouse(win=win)
trial_data_list = []

def save_data(trial_data_list, data_file_path):
    """Save trial data to a CSV file."""
    try:
        with open(data_file_path, "w", newline='') as f:
            fieldnames = trial_data_list[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
            writer.writeheader()
            writer.writerows(trial_data_list)
    except Exception as e:
        print(f"Failed to save data: {e}")

# Main experiment loop
try:
    for trial in trials:
        current_params = trial
        # Move mouse off screen
        mouse.setPos(newPos=(win.size[0] * 1.5, win.size[1] * 1.5))
        #mouse.setVisible(False)
        # Convert parameters to the correct type (all values read from CSV are strings)
        cue_frequency = float(current_params['cue_frequency'])
        cue_frequency_range = float(current_params['cue_frequency_range'])
        choice_frequency = float(current_params['choice_frequency'])
        choice_frequency_range = float(current_params['choice_frequency_range'])
        coherence = float(current_params['coherence'])
        correct_response = 'same' if cue_frequency == choice_frequency else 'diff'
        # Generate the cue and choice tone sequences, returns numpy array
        cue_tone_sequence = generate_tone_sequence(coherence, cue_frequency, cue_frequency_range,sampleRate = 44100,tone_duration = 0.025,sequence_duration = 0.5, seed = seed)
        choice_tone_sequence = generate_tone_sequence(coherence, choice_frequency, choice_frequency_range,sampleRate = 44100,tone_duration = 0.025,sequence_duration = 0.5, seed = seed)

        # cue sequence (stim 1), a numpy array we play as a sound
        cue_sound = sound.Sound(cue_tone_sequence, sampleRate=44100)
        cue_sound.play()
        core.wait(cue_sound.getDuration())
        
        core.wait(wm_delay)
        # Play the choice tone sequence (stim 2)
        choice_sound = sound.Sound(choice_tone_sequence, sampleRate=44100)
        choice_sound.play()
        core.wait(choice_sound.getDuration())
        

        greenBox.draw()
        redBox.draw()
        win.flip()
        ResponsePeriodOnset = core.getTime()
        responseDetected = False
        response = 'NA'
        max_response_time = 10  # Set maximum response time in seconds

        while not responseDetected:
            if greenBox.contains(mouse.getPos()):
                response = 'same'
                responseDetected = True
                responseTime = core.getTime() - ResponsePeriodOnset
            elif redBox.contains(mouse.getPos()):
                response = 'diff'
                responseDetected = True
                responseTime = core.getTime() - ResponsePeriodOnset

            if 'escape' in event.getKeys():
                save_data(trial_data_list, data_file_path)
                win.close()
                core.quit()

            if core.getTime() - ResponsePeriodOnset > max_response_time:
                responseDetected = True
                responseTime = max_response_time
                response = 'NA'  # Indicate no response within time limit

            core.wait(0.01)

        if response == 'NA':
            yellowBox.draw()
            win.flip()
            hover_detected = False
            last_move_time = core.getTime()  # Track the last time the mouse was moved
            move_interval = 120  # Move the mouse every 2 minutes 

            while not hover_detected:
                # Check for hover over the yellow box
                if yellowBox.contains(mouse.getPos()):
                    hover_detected = True

                # Check if enough time has passed to move the mouse
                if core.getTime() - last_move_time > move_interval:
                    # Move the mouse slightly in a random direction
                    current_mouse_pos = mouse.getPos()
                    new_x = current_mouse_pos[0] + random.uniform(-10, 10)  # Move by +/-10 pixels randomly
                    new_y = current_mouse_pos[1] + random.uniform(-10, 10)  # Move by +/-10 pixels randomly
                    mouse.setPos((new_x, new_y))
                    last_move_time = core.getTime()  # Reset the move timer

                # Check for escape key to quit the experiment
                if 'escape' in event.getKeys():
                    save_data(trial_data_list, data_file_path)
                    win.close()
                    core.quit()

                # Wait for a short interval before checking again
                core.wait(0.01)

        response_correct = response == correct_response
        feedback = 'Correct' if response_correct else 'Incorrect'
        show_feedback(win, feedback)

        if 'escape' in event.getKeys():
            save_data(trial_data_list, data_file_path)
            win.close()
            core.quit()

        trial_data = {
            'Trial Number': trials.thisN,
            'Participant': participant_name,
            'Response': response,
            'ResponsePeriodOnset': ResponsePeriodOnset,
            'RT': responseTime,
            'Seed': seed,
            'Cue Frequency': cue_frequency,
            'Cue Frequency Range': cue_frequency_range,
            'Choice Frequency': choice_frequency,
            'Choice Frequency Range': choice_frequency_range,
            'Coherence': coherence
        }

        trial_data_list.append(trial_data)
        win.flip()
        if response_correct:
            if 'port' in globals() and port:
                port.write(str.encode('r4'))  # REWARD
                core.wait(1)
            else:
                core.wait(1)
        else:
            core.wait(6)

        # Save data after each trial
        save_data(trial_data_list, data_file_path)
        
except Exception as e:
    print(f"An error occurred during the experiment: {e}")
    save_data(trial_data_list, data_file_path)
    # Restore the system's normal behavior after the experiment finishes
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
    win.close()
    core.quit()
finally:
    # Final save
    save_data(trial_data_list, data_file_path)
    # Restore the system's normal behavior after the experiment finishes
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
    win.close()
    core.quit()
