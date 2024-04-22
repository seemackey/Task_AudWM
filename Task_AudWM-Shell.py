# simpler auditory working mem task
# adapted from Noah Markowtiz' TAMy task
# Chase M 2024

from psychopy import visual, core, event, data, gui, sound
import os
import json
import csv
import numpy as np
from utils import generate_tone_sequence
from datetime import datetime

# Constants
flash_rate = 1.6  # Hz
flash_period = 1 / flash_rate  # seconds per flash
flash_duration = 0.1  # flash on time in seconds
pre_stim_flashes = 3  # Number of flashes before first sequence
inter_sequence_flashes = 5  # Flashes between sequences
cue_duration = 0.5  # Duration of each tone sequence
inter_sequence_interval = inter_sequence_flashes * flash_period  # Interval between sequences


# Set up experiment parameters via a GUI
info = {'Participant Name': '', 'Random Seed': ''}
dlg = gui.DlgFromDict(dictionary=info, title='Experiment Setup')
if dlg.OK == False:
    core.quit()  # User pressed cancel

# user gives us the name and a random seed
participant_name = info['Participant Name']
seed = int(info['Random Seed'])

# Create a directory for data inside the current script's directory
data_folder = "data"
data_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_folder)
if not os.path.exists(data_folder_path):
    os.makedirs(data_folder_path)

# Generate the data file path
# Append the timestamp to the filename
# Generate a unique timestamp
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
data_file_name = f"{participant_name}_{timestamp}.csv"
data_file_path = os.path.join(data_folder_path, data_file_name)

# Load monitor specifications
monitor_specs = {"screen_resolution": [1920, 1080], "monitor_width": 52.5, "full_screen": True}
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



####### FUNCTIONSSSSSSSSS #######################
# Function to play a flash
def play_flash(flash_duration):
    flash_stim.setAutoDraw(True)
    win.flip()
    core.wait(flash_duration)
    flash_stim.setAutoDraw(False)
    win.flip()

# Function to read the CSV file and return a list of dicts
def load_stimuli_parameters(csv_filename):
    with open(csv_filename, mode='r') as infile:
        reader = csv.DictReader(infile)
        return [row for row in reader]
        
# Function to show feedback text
def show_feedback(win, text):
    feedback_text = visual.TextStim(win, text=text, pos=(0, -300))
    feedback_text.draw()
    win.flip()
    core.wait(1.5)  # Display feedback for 1.5 seconds
    win.flip()  # Clear the screen
    
############################################################

# Load the tone sequence parameters from the CSV
csv_filename = 'soundslist.csv'
stimuli_parameters = load_stimuli_parameters(csv_filename)


# Auditory stimulus setup
#seed = 12345  # Define a seed for reproducibility, could ask for this in the GUI



# Set up the TrialHandler
trials = data.TrialHandler(stimuli_parameters, nReps=1, method='random')


# Create a mouse object
mouse = event.Mouse(win=win)
trial_data_list = []

for trial in trials:
    
    current_params = trial
    # Move mouse off screen
    mouse.setPos(newPos=(win.size[0] * 1.5, win.size[1] * 1.5))
    
    # Convert parameters to the correct type (all values read from CSV are strings)
    cue_frequency = float(current_params['cue_frequency'])
    cue_frequency_range = float(current_params['cue_frequency_range'])
    choice_frequency = float(current_params['choice_frequency'])
    choice_frequency_range = float(current_params['choice_frequency_range'])
    coherence = float(current_params['coherence'])
    # Determine the correct response
    correct_response = 'same' if cue_frequency == choice_frequency else 'diff'
    # Generate the cue and choice tone sequences
    cue_tone_sequence = generate_tone_sequence(coherence, cue_frequency, cue_frequency_range)
    choice_tone_sequence = generate_tone_sequence(coherence, choice_frequency, choice_frequency_range)

    # present synchronized AV
        # Present synchronized AV stimuli
    clock = core.Clock()
    num_flashes = pre_stim_flashes + inter_sequence_flashes
    total_flash_duration = num_flashes * flash_period
    last_flash_time = 0
    
    # Initial pre-stimulus flashes
    for i in range(pre_stim_flashes):
        play_flash(flash_duration)
        core.wait(flash_period - flash_duration)
        
    # cue sequence (stim 1)
    cue_sound = sound.Sound(cue_tone_sequence, sampleRate=44100)
    cue_sound.play()
    core.wait(cue_sound.getDuration())
    
    # Inter-sequence flashes
    for i in range(inter_sequence_flashes):
        play_flash(flash_duration)
        core.wait(flash_period - flash_duration)
        
    # Play the choice tone sequence (stim 2)
    choice_sound = sound.Sound(choice_tone_sequence, sampleRate=44100)
    choice_sound.play()
    core.wait(choice_sound.getDuration())

    # Draw selection boxes
    greenBox.draw()
    redBox.draw()
    win.flip()
    ResponsePeriodOnset = core.getTime()

    # Hover detection
    responseDetected = False
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
            # Save data before exiting
            with open(data_file_path, "w", newline='') as f:
                fieldnames = trial_data_list[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
                writer.writeheader()
                writer.writerows(trial_data_list)
            win.close()
            core.quit()
        core.wait(0.01)
    if 'escape' in event.getKeys():
        # Save data before exiting
        with open(data_file_path, "w", newline='') as f:
            fieldnames = trial_data_list[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
            writer.writeheader()
            writer.writerows(trial_data_list)
        win.close()
        core.quit()
        

    # Record trial data
    trial_data = {
        'Trial Number': trials.thisN,
        'Participant': participant_name,
        'Response': response,
        'ResponsePeriodOnset': ResponsePeriodOnset,
        'RT': responseTime,  # 
        'Seed': seed,
        'Cue Frequency': cue_frequency,
        'Cue Frequency Range': cue_frequency_range,
        'Choice Frequency': choice_frequency,
        'Choice Frequency Range': choice_frequency_range,
        'Coherence': coherence
    }
    trial_data_list.append(trial_data)

    # Provide feedback
    # Check if the participant's response was correct
    response_correct = response == correct_response
    # Provide feedback on the response
    feedback = 'Correct' if response_correct else 'Incorrect'
    show_feedback(win, feedback) # function that displays fdback and waits
    
    win.flip()  # Clear the screen for the next trial

# Save trial data to a CSV file
with open(data_file_path, "w", newline='') as f:
    fieldnames = trial_data_list[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(trial_data_list)

# Cleanup
win.close()
core.quit()

