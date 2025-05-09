import struct   # Needed to read the binary file
import ROOT     # Needed to use TTrees 
from array import array    # Needed to package data so that it can be stored in a TTree, weird hold-over because ROOT needs C++ pointers
import os       # For converting rel. paths to abs.
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import numpy as np
import matplotlib.pyplot as plt

completer = PathCompleter()

file_path = prompt("Please enter the absolute path to the root file: ", completer=completer)
print(f"You selected: {file_path}")

#  Reading from a tree
infile = ROOT.TFile(file_path) # put your file name here
t = infile.Get("test_tree")
print(f"There are {t.GetEntries()} entries in this tree.")

t.GetEntry(0) # put your entry number here instead of 0
one_event_data = np.array(t.waveform_data)
event_2D = {}

for ch in range(t.num_of_channels):
    ch_id = t.active_channels[ch]
    print(f"Reading channel {ch_id}")
    waveform = []
    for times in range(t.num_of_samples):
        sample = one_event_data[(t.num_of_samples*ch)+times]
        waveform.append(sample)
    event_2D[ch_id] = np.array(waveform)

for waveform in event_2D.values():
    plt.plot(waveform)
plt.savefig("waveform.png")


infile.Close() # Close the file or bad things happen
