from psychopy import visual, core, event, data, gui, sound
import os
from datetime import datetime
import csv
import numpy as np
import random
from Functions_WM import play_flash, load_stimuli_parameters, show_feedback, create_stereo_buffer, play_tone

# Constants

flash_rate = 1.6  # Hz
flash_period = 1 / flash_rate  # seconds per flash
flash_duration = 0.1  # flash on time in seconds
pre_stim_flashes = 0  # Number of flashes before first sequence
inter_sequence_flashes = 0  # Flashes between sequences
cue_duration = 0.5  # Duration of each tone sequence
inter_sequence_interval = inter_sequence_flashes * flash_period  # Interval between sequences
wm_delay = 1.0 #Delay between cue and choice sounds

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
    fullscr=full_screen,
    monitor="debugging_monitor",
    screen=1,  # Set this to 1 to use the second display
    waitBlanking=True
)

# Visual stimulus setup

box_size = 200  # Static box size
greenBox = visual.Rect(win, width=box_size, height=box_size, pos=(-300, 0), fillColor='green')
redBox = visual.Rect(win, width=box_size, height=box_size, pos=(300, 0), fillColor='red')
flash_stim = visual.Rect(win, size=(200, 200), pos=(0, 0), fillColor='white')
stimuli_parameters = load_stimuli_parameters(csv_filename)

# Auditory stimulus setup

trials = data.TrialHandler(stimuli_parameters, nReps=100, method='random')

# Create a mouse object

mouse = event.Mouse(win=win)
trial_data_list = []

# Main experiment loop
for trial in trials:
    current_params = trial
    # Convert parameters to the correct type (all values read from CSV are strings)
    cue_frequency = float(current_params['cue_frequency'])
    cue_frequency_range = float(current_params['cue_frequency_range'])
    choice_frequency = float(current_params['choice_frequency'])
    choice_frequency_range = float(current_params['choice_frequency_range'])
    coherence = float(current_params['coherence'])
    correct_response = 'same' if cue_frequency == choice_frequency else 'diff'

    if cue_frequency == choice_frequency:
        play_tone(cue_frequency, left=True)
        core.wait(wm_delay)
        play_tone(choice_frequency, left=True)
    else:
        play_tone(cue_frequency, left=False)
        core.wait(wm_delay)
        play_tone(choice_frequency, left=False)

    for i in range(inter_sequence_flashes):
        play_flash(win, flash_stim, flash_duration)
        core.wait(flash_period - flash_duration)

    greenBox.draw()
    redBox.draw()
    win.flip()
    ResponsePeriodOnset = core.getTime()
    responseDetected = False
    response = 'NA'

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
            with open(data_file_path, "w", newline='') as f:
                fieldnames = trial_data_list[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
                writer.writeheader()
                writer.writerows(trial_data_list)
            win.close()
            core.quit()
        core.wait(0.01)

    response_correct = response == correct_response
    feedback = 'Correct' if response_correct else 'Incorrect'
    show_feedback(win, feedback)

    if 'escape' in event.getKeys():
        with open(data_file_path, "w", newline='') as f:
            fieldnames = trial_data_list[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
            writer.writeheader()
            writer.writerows(trial_data_list)

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
        core.wait(1)
    else:
        core.wait(5)

with open(data_file_path, "w", newline='') as f:
    fieldnames = trial_data_list[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(trial_data_list)

win.close()
core.quit()
