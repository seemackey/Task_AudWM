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
duration = 0.5

def create_stereo_buffer(frequency, left_amp=1.0, right_amp=0.5):
    """
    Create a stereo buffer for a given frequency with specified amplitudes for left and right channels.
    
    :param frequency: Frequency of the tone.
    :param left_amp: Amplitude of the tone in the left channel.
    :param right_amp: Amplitude of the tone in the right channel.
    :return: Stereo signal buffer.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    mono_signal = np.sin(2 * np.pi * frequency * t)
    stereo_signal = np.array([left_amp * mono_signal, right_amp * mono_signal])
    return stereo_signal.T

def play_tone(frequency, left_amp=1.0, right_amp=0.5):
    """
    Play a tone with specified amplitudes for left and right channels.
    
    :param frequency: Frequency of the tone.
    :param left_amp: Amplitude of the tone in the left channel.
    :param right_amp: Amplitude of the tone in the right channel.
    """
    stereo_buffer = create_stereo_buffer(frequency, left_amp, right_amp)
    tone = sound.Sound(stereo_buffer, sampleRate=sample_rate)
    tone.play()
    core.wait(duration)
    tone.stop()