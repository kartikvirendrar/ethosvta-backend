from pyAudioAnalysis import audioBasicIO as aIO
from pyAudioAnalysis import audioSegmentation as aS
from tqdm import tqdm

import numpy as np
from deepspeech import Model 
import scipy.io.wavfile as wavfile

line_count = 0

def sort_alphanumeric(data):
    """Sort function to sort os.listdir() alphanumerically
    Helps to process audio files sequentially after splitting 
    Args:
        data : file name
    """
    
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)] 
    
    return sorted(data, key = alphanum_key)
# import wavefile
# from deepspeech import Model
# import subprocess as sp


# def silenceRemoval(input_file, smoothing_window = 1.0, weight = 0.2):
#     print("Running silenceRemoval function\n")
#     [fs, x] = aIO.read_audio_file(input_file)
#     segmentLimits = aS.silence_removal(x, fs, 0.05, 0.05, smoothing_window, weight)
#     print(segmentLimits)
#     for i, s in enumerate(segmentLimits):
#         strOut = "{0:s}_{1:.3f}-{2:.3f}.wav".format(input_file[0:-4], s[0], s[1])
#         # wavfile.write(strOut, fs, x[int(fs * s[0]):int(fs * s[1])])
#         write_file("E:/ml_ethos/ml/audio", strOut, ".wav", x[int(fs * s[0]):int(fs * s[1])], fs)
    
#     print("\nsilenceRemoval function completed")

# import os


def write_file(output_file_path, input_file_name, name_attribute, sig, fs):
    """
    Read wave file as mono.

    Args:
        - output_file_path (str) : path to save resulting wave file to.
        - input_file_name  (str) : name of processed wave file,
        - name_attribute   (str) : attribute to add to output file name.
        - sig            (array) : signal/audio array.
        - fs               (int) : sampling rate.

    Returns:
        tuple of sampling rate and audio data.
    """
    # set-up the output file name
    fname = os.path.basename(input_file_name).split(".wav")[0] + name_attribute
    fpath = os.path.join(output_file_path, fname)
    wavfile.write(filename=fpath, rate=fs, data=sig)
    print("Writing data to " + fpath + ".") 


import os
import datetime
import wave

def write_to_file(file_handle, inferred_text, limits):
    print(limits)
    """Write the inferred text to SRT file
    Follows a specific format for SRT files
    Args:
        file_handle : SRT file handle
        inferred_text : text to be written
        line_count : subtitle line count 
        limits : starting and ending times for text
    """
    global line_count
    d = str(datetime.timedelta(seconds=float(limits[0])))
    try:
        from_dur = "0" + str(d.split(".")[0]) + "," + str(d.split(".")[-1][:2])
    except:
        from_dur = "0" + str(d) + "," + "00"
        
    d = str(datetime.timedelta(seconds=float(limits[1])))
    try:
        to_dur = "0" + str(d.split(".")[0]) + "," + str(d.split(".")[-1][:2])
    except:
        to_dur = "0" + str(d) + "," + "00"
        
    file_handle.write(str(line_count) + "\n")
    file_handle.write(from_dur + " --> " + to_dur + "\n")
    file_handle.write(inferred_text + "\n\n")

def silenceRemoval(input_file, smoothing_window = 1.0, weight = 0.2):
    [fs, x] = aIO.read_audio_file(input_file)
    segmentLimits = aS.silence_removal(x, fs, 0.05, 0.05, smoothing_window, weight)
    
    for i, s in enumerate(segmentLimits):
        strOut = "{0:s}_{1:.3f}-{2:.3f}.wav".format(input_file[0:-4], s[0], s[1])
        write_file("E:/ml_ethos/ml/audio", strOut, ".wav", x[int(fs * s[0]):int(fs * s[1])], fs)
    
    print("\nsilenceRemoval function completed")


def ds_process_audio(audio_file, file_handle): 
    global line_count
    ds = Model("deepspeech-0.9.3-models.pbmm")
    ds.enableExternalScorer("deepspeech-0.9.3-models.scorer")
    
    fin = wave.open(audio_file, 'rb')
    audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
    fin.close()
    
    # Perform inference on audio segment
    infered_text = ds.stt(audio)
    
    # File name contains start and end times in seconds. Extract that
    limits = audio_file.split("/")[-1][:-4].split("_")[-1].split("-")
    print(audio_file)
    if len(infered_text) != 0:
        line_count += 1
        write_to_file(file_handle, infered_text, limits)

def main():
    print("AutoSub v0.1\n")
        
    a=line_count
    
    # Load DeepSpeech model 
    ds = Model("deepspeech-0.9.3-models.pbmm")
            
    ds.enableExternalScorer("deepspeech-0.9.3-models.scorer")
    
    input_file = "0_39.wav"
    print("\nInput file:", input_file)
    
    base_directory = os.getcwd()
    output_directory = os.path.join(base_directory, "output")
    audio_directory = os.path.join(base_directory,"ml/audio" )
    video_file_name = input_file.split("/")[-1].split(".")[0]
    audio_file_name = os.path.join(audio_directory, video_file_name + ".wav")
    srt_file_name = os.path.join(output_directory, video_file_name + ".srt")
    print(audio_file_name)
    # Extract audio from input video file
    # extract_audio(input_file, audio_file_name)
    
    print("Splitting on silent parts in audio file")
    silenceRemoval(audio_file_name)
    
    # Output SRT file
    file_handle = open(srt_file_name, "a+")
    
    print("\nRunning inference:")
    l=[]
    for file in tqdm((os.listdir(audio_directory))):
        audio_segment_path = os.path.join(audio_directory, file)
        l.append(str(audio_segment_path))
    l = sorted(l)
    print(l)
        # Dont run inference on the original audio file
    for audio_segment_path in l:
        if audio_segment_path.split("/")[-1] != audio_file_name.split("/")[-1]:
            ds_process_audio( audio_segment_path, file_handle)
            
    print("\nSRT file saved to", srt_file_name)
    file_handle.close()
        
if __name__ == "__main__":
    main()