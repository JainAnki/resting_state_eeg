from pathlib import Path
import mne
import numpy as np
import warnings

datafolder = Path('data/')

n = len(sorted(list(datafolder.glob(pattern='*RS.bdf'))))

# Generator for the raw files
def raws(verbose=False):

    datafiles = sorted(list(datafolder.glob(pattern='*RS.bdf')))

    for f in datafiles:

        montage = mne.channels.make_standard_montage('biosemi64')
        eog_names = ['EXG' + str(n) for n in range(1, 5)]
        emg_names = ['EXG' + str(n) for n in range(5, 9)]
        
        raw = mne.io.read_raw_bdf(str(f), eog=eog_names,
                                  misc=emg_names +['Status'], verbose='ERROR')
                                  #verbose='ERROR')
                                  #misc=emg_names, +['Status'], verbose='ERROR')
        # Set the montage separately
        raw.set_montage(montage)

        raw.info['subject_info'] = {'pid': f.name[7:11],
                                    'group': f.name[3:6]}
        if verbose:
            print('subject: {id}'.format(id=f.name[7:11]))

        yield raw


# Generator for the events
def events():
    for raw in raws():
        # find the events in the raw data
        ev = mne.find_events(raw, verbose="ERROR")
        
        sf = raw.info['sfreq']

        #ev = mne.find_events(raw, stim_channel='Status', verbose="ERROR", output='step', uint_cast=True)
        # throw warning if the events seem off
        if ev.shape[0] != 4:
            warnings.warn("Expected 4 events, but got {events}".format(events=ev.shape[0]))

        print(f"First event at {ev[0][0]/sf} sec")
        
        eventarray = []
        et = ev[0][0]
        eyes_flag = 101
        
        while (et+60*sf)<len(raw):
            eventarray.append([et, 0, eyes_flag])
            if eyes_flag == 101:
                eyes_flag = 102
            else:
                eyes_flag = 101
            et = et + 60 * sf
        
        # manually fix issues with the triggers
        # 101 = eyes open, 102 = eyes closed
        # eventarray[:, 1] = 0
        # if eventarray.shape[0] == 4:
        #     eventarray[:, 2] = [101, 102, 101, 102]
        # elif eventarray.shape[0] == 5:
        #     eventarray[:, 2] = [101, 102, 101, 102, 101]
        # elif eventarray.shape[0] == 6:
        #     eventarray[:, 2] = [101, 102, 101, 102, 101, 102]  

        yield np.array(eventarray)



# generator for 4s chunk events
#def sliced_events(segment_length=4.0):
#    for raw in raws():
        # find the events in the raw data
#        eventarray = mne.find_events(raw, verbose='ERROR')

        # throw warning if the events seem off
#        if eventarray.shape[0] != 4:
#            warnings.warn(f"Expected 4 events, but got {eventarray.shape[0]}.")

        # manually fix issues with the triggers
        # 101 = eyes open, 102 = eyes closed
#        eventarray[:, 1] = 0
#        eventarray[:, 2] = [101, 102, 101, 102]
        
        # make a new array with 4-s chunks, same codes
#        eventarray = np.
            
#        yield eventarray

