#include <iostream>
#include <vector>
#include <map>
#include <TObject.h>
#include <TFile.h>
#include <TTree.h>

// Defining my class now!

class CAEN_Event_cpp : public TObject {
    public:
        int event_num;
        int timestamp;
        int num_samples; // should be 37500 
        int resolution; // should be 8
        int num_channels; // depends on the run
        std::map<int, std::vector<float>> event_data; // key value is channel number in int and value is a vector with the waveforms samples as floats

        CAEN_Event_cpp() : event_num{-1}, timestamp{-1}, num_samples{-1}, resolution{-1}, num_channels{-1}, event_data{{1,{0.1, 0.2, 0.3}}, {2,{0.4, 0.5, 0.6}}} { // Class constructor! Initializing all the int values to unrealistic values so that errors can be caught
            std::cout << "Object initialized.";
        }

        void print_details() const { // const so that none of the attributes get changed
            // Just prints some attributes' values as a quick check
            std::cout << "\n--------------- Event details ---------------" << std::endl;
            std::cout << "Event number: " << event_num << std::endl;
            std::cout << "Timestamp: " << timestamp << std::endl;
            std::cout << "Number of samples: " << num_samples << std::endl;
            std::cout << "Resolution (ns): " << resolution << std::endl;
            std::cout << "Number of channels: " << num_channels << std::endl;
            std::cout << "Data was found for " << event_data.size() << " channels" << std::endl;
            std::cout << "---------------------------------------------" << std::endl;
        }

        std::vector<float> get_channel_data(int ch_num) {
            // Gets data from a particular channel
            return event_data[ch_num];
        }

};
