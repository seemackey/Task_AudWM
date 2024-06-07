from psychopy import visual,core,sound
import csv
import numpy as np


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
    core.wait(0.01)  # Display feedback for 1.5 seconds
    win.flip()  # Clear the screen
  
# Functions for creating and playing stereo sounds
sample_rate = 44100
duration = 1.0

def create_stereo_buffer(frequency, left=True):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    mono_signal = np.sin(2 * np.pi * frequency * t)
    if left:
        stereo_signal = np.array([mono_signal, np.zeros_like(mono_signal)])
    else:
        stereo_signal = np.array([np.zeros_like(mono_signal), mono_signal])
    return stereo_signal.T

def play_tone(frequency, left=True):
    stereo_buffer = create_stereo_buffer(frequency, left)
    tone = sound.Sound(stereo_buffer, sampleRate=sample_rate)
    tone.play()
    core.wait(1.0)
    tone.stop()