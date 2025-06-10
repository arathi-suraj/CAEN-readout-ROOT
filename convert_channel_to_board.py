import numpy as np # Needed to hold data before stowing into my TTree
import ROOT     # Needed to use TTrees 
from array import array    # Needed to package data so that it can be stored in a TTree, weird hold-over because ROOT needs C++ pointers
import os       # For converting rel. paths to abs.
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import matplotlib.pyplot as plt # for plotting and debugging purposes. comment out if you don't need it.

completer = PathCompleter()

file_path = prompt("Please enter the absolute path to the root file: ", completer=completer)
print(f"You selected: {file_path}")

#tree_name = str(input("Enter the tree name: "))

#  Reading from a tree
infile = ROOT.TFile(file_path, "READ") # put your file name here
t = infile.Get("tree")
print(f"There are {t.GetEntries()} entries in this tree.")

event_nums = []
channel_nums = []
timestamps = []
num_samples = None
resolution = None

###### Prep work tree so that user doesn't have to be prompted ######
for entry in t: # iterating over the tree for prep work
    if (t.event_id not in event_nums):
        event_nums.append(t.event_id)
    if (t.channel not in channel_nums):
        channel_nums.append(t.channel)
    if (t.timestamp not in timestamps):
        timestamps.append(t.timestamp)
    if (num_samples != t.numberOfSamples):
        num_samples = t.numberOfSamples
    if (resolution != t.resolution):
        resolution = t.resolution
#####################################################################


# Setting up vars for the next loop
channel_nums.sort() # this is a must-have to convert to my format!
total_num_channels = len(channel_nums) # usually 36
total_events = len(event_nums)
master_list = [None] * total_events * total_num_channels


###### Main data transfer loop ######
for entry in t:
    print(f"Working on event {t.event_id}, channel {t.channel}.")
    # you must decode t.waveform_samples here to avoid doing it downstream!
    # We follow the numpy casts tutorial on the cppyy documentation website for this
    temp_data = np.array(t.waveform_samples, dtype=np.float32)
    master_list[(t.event_id *  total_num_channels) + channel_nums.index(t.channel)] = temp_data
#####################################
for elem in master_list[0]:
    print(elem)
# print(np.asarray(master_list).shape) # it seems like it works?
# for ind in range(len(master_list[0])):
#     print(np.array(master_list[0][ind])) # it seems like it works?

infile.Close()

#for elem in master_list:
#    print(elem)
    #plt.plot(elem)
# plt.savefig() # all of these are correct!

############## ISSUE ##############
# master_list puts in garbage values when decoded from cppyy.LowLevelView object. We need to convert the values correctly.
# I tried converting the data directly at t.waveform_samples because it's a cppyy.LowLevelView object there too. I used numpy casting
# as shown in the tutorial on the cppyy docs webpage.
# Let's see if it works.
# OKAY.
# Using np.frombuffer will NOT WORK. It just creates a view and not a new copy of the array. 
# To store the values correctly, cast the waveform array into an np.array(dtype=np.float32) and then append that to the master list.
###################################

# We're done with the file per channel root file here, so onto per event!

new_file_path = os.path.dirname(file_path)
new_filename = os.path.join(new_file_path, "test.root")

outfile = ROOT.TFile(new_filename, "RECREATE")

# Catching TFile opening errors here
if (outfile.IsOpen() == False):
    print("Error in opening TFile.")

t2 = ROOT.TTree("test_tree", "test_tree")

# initializing all branch variables
event_num = array("i", [0])
timestamp = array("L", [0])
num_of_samples = array("i", [0])
one_sample_in_ns = array("i", [0])
channels = array("i", [0])
actives = array("i", total_num_channels*[0])
waveform_data = array("f", total_num_channels*num_samples*[0.0])

# actually creating the branches
t2.Branch("event_num", event_num, "event_num/I")
t2.Branch("timestamp", timestamp, "timestamp/l")
t2.Branch("num_of_samples", num_of_samples, "num_of_samples/I")
t2.Branch("resolution", one_sample_in_ns, "resolution/I")
t2.Branch("num_of_channels", channels, "num_of_channels/I")
t2.Branch("active_channels", actives, "active_channels[" + str(total_num_channels) + "]/I")
t2.Branch("waveform_data", waveform_data, "waveform_data[" + str(total_num_channels*num_samples) + "]/F")

for event in range(total_events):
    event_num[0] = event
    timestamp[0] = timestamps[event]
    num_of_samples[0] = num_samples
    one_sample_in_ns[0] = resolution
    channels[0] = total_num_channels

    for ch in range(total_num_channels):
        actives[ch] = channel_nums[ch] 
        for times in range(num_samples):
            #print(np.array(master_list[0]))
            waveform_data[(num_samples*ch)+times] = master_list[(total_num_channels * event) + ch][times]
    
    # one event fully populated! time to fill the TTree!
    print(f"Filling event {event} in the ROOT TTree")
    t2.Fill()

t2.Write()
outfile.Close()
print("Final root file saved.")