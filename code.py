#https://learn.adafruit.com/classic-midi-synth-control-with-trellis-m4/code-with-circuitpython
import time
import board
import busio
import audioio
import adafruit_fancyled.adafruit_fancyled as fancy
import adafruit_trellism4
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode



midiuart = busio.UART(board.SDA, board.SCL, baudrate=31250)

#midi_mode = True
midi_mode = False

with open ("settings.txt", "r") as myfile:
    data=myfile.readlines()
#print(data[0])
#print('\n******\n')
#print(print(data[1]))
# The keyboard object!
time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
tempo = 240
  # Starting BPM
# You can use the accelerometer to speed/slow down tempo by tilting!
ENABLE_TILT_TEMPO = False
MIN_TEMPO = 10
MAX_TEMPO = 400
SAMPLE_FOLDER = "/samples/"  # the name of the folder containing the samples
# You get 4 voices, they must all have the same sample rate and must
# all be mono or stereo (no mix-n-match!)
VOICES = [SAMPLE_FOLDER+"rats_clip1.wav",
          SAMPLE_FOLDER+"rats_clip2.wav",
          SAMPLE_FOLDER+"rats_clip3.wav",
          SAMPLE_FOLDER+"rats_clip4.wav"]
# four colors for the 4 voices, using 0 or 255 only will reduce buzz
DRUM_COLOR = ((120, 0, 255),
              (120, 0, 255),
              (120, 0, 255),
              (120, 0, 255))
ACTIVE_COLOR = (120, 0, 255)
INACTIVE_COLOR = (0, 0, 120)
CURRENT_NOTE_COLOR=(120, 0, 60)
SECOND_NOTE_COLOR=(120, 0, 30)


# the color for the sweeping ticker bar
TICKER_COLOR = (0, 0, 255)
# Our keypad + neopixel driver
trellis = adafruit_trellism4.TrellisM4Express(rotation=90)
trellis.pixels.brightness = (0.31)


#Create a list of all step XY locations
step_list=[]
for y in range(4):
    for x in range(8):
        step_list.append((y, x))


# Parse the first file to figure out what format its in
with open(VOICES[0], "rb") as f:
    wav = audioio.WaveFile(f)
    print("%d channels, %d bits per sample, %d Hz sample rate " %
          (wav.channel_count, wav.bits_per_sample, wav.sample_rate))
    # Audio playback object - we'll go with either mono or stereo depending on
    # what we see in the first file
    if wav.channel_count == 1:
        audio = audioio.AudioOut(board.A1)
    elif wav.channel_count == 2:
        audio = audioio.AudioOut(board.A1, right_channel=board.A0)
    else:
        raise RuntimeError("Must be mono or stereo waves!")
    mixer = audioio.Mixer(voice_count=4,
                          sample_rate=wav.sample_rate,
                          channel_count=wav.channel_count,
                          bits_per_sample=wav.bits_per_sample,
                          samples_signed=True)
    audio.play(mixer)
samples = []
# Read the 4 wave files, convert to stereo samples, and store
# (show load status on neopixels and play audio once loaded too!)
for v in range(4):
    #trellis.pixels[(v, 0)] = DRUM_COLOR[v]
    wave_file = open(VOICES[v], "rb")
    # OK we managed to open the wave OK
    sample = audioio.WaveFile(wave_file)
    while mixer.playing:
        pass
    samples.append(sample)
# Clear all pixels
trellis.pixels.fill(0)
# Our global state


current_step = 7 # we actually start on the last step since we increment first
# the state of the sequencer
beatset = [[False] * 8, [False] * 8, [False] * 8, [False] * 8]
prior_beatset=beatset
# currently pressed buttons
current_press = set()
key_chars='0123456789abcdefghijklmnopqrstuvwxyz'
rows=['A', 'B', 'C', 'D']
current_step_row=[0, 0, 0, 0]
previous_step_row=[0, 0, 0, 0]
cycle_count=0
dividend_list=[[1, 1, 1, 1], [1, 1, 1, 2], [1, 1, 2, 4], [1, 2, 4, 8]]
idle_count=0
pressed_list=[]
#step_list=[]
previous_step_list=[]
step_number=0
step_count=0
divided_step_number=0
previous_divided_step_number=0
sequence_length=0
previous_path=[]
path=[]
previous_step_number=1000
row=0
column=1
step_log_temp=[]
single_note_pressed=False
single_note_pressed=(0,0)
for step in step_list:
    trellis.pixels[step] = INACTIVE_COLOR
###########################################################################################
################ Everything above executes a single time on startup #######################
######################## Everything below repeats on a loop ###############################
###########################################################################################

while True:
    #print(idle_count)
    idle_count+=1
    step_count+=1
    stamp = time.monotonic()

    if trellis.pixels[single_note_pressed] == ACTIVE_COLOR:
        #play sound here
        keyboard_layout.write(key_chars[single_note_pressed[0]*8+single_note_pressed[1]])
        print(single_note_pressed)
        pass
    else:
        pass
        
    
    if step_count>=sequence_length*3+1:
        path=[]
        sequence_length=len(path)
        for step in step_list:
            trellis.pixels[step] = INACTIVE_COLOR

    if sequence_length>0:
        trellis.pixels[path[step_number]] = CURRENT_NOTE_COLOR
        #convert step to alpha numeric character then print
        ##### ENABLE WHEN DONE TROUBLESHOOTING ############
        keyboard_layout.write(key_chars[path[step_number][0]*8+path[step_number][1]])
        print(key_chars[path[step_number][0]*8+path[step_number][1]])
        step_log_temp.append(path[step_number])
        if previous_step_number<100:
            trellis.pixels[path[previous_step_number]] = ACTIVE_COLOR
        previous_step_number=step_number
        step_number+=1
        if step_number>=sequence_length:
            step_number=0
            #print(f'Step Log: {step_log_temp}')
            step_log_temp=[]
    ####################################################
    ################ Second Path #######################
    ####################################################           
            
    if sequence_length>0:
        if (step_count+1)%3==0:
            trellis.pixels[path[divided_step_number]] = SECOND_NOTE_COLOR
            #convert step to alpha numeric character then print
            ##### ENABLE WHEN DONE TROUBLESHOOTING ############
            keyboard_layout.write(key_chars[path[divided_step_number][0]*8+path[divided_step_number][1]])
            print(key_chars[path[divided_step_number][0]*8+path[divided_step_number][1]])

            if previous_divided_step_number<100:
                if previous_divided_step_number!=previous_step_number:
                    trellis.pixels[path[previous_divided_step_number]] = ACTIVE_COLOR
            previous_divided_step_number=divided_step_number
            divided_step_number+=1
            if divided_step_number>=sequence_length:
                divided_step_number=0           
            
                
            
            
            
            

    #####################################################################
    # handle button presses while we're waiting for the next tempo beat #
    while time.monotonic() - stamp < 60/tempo:
        # Check for pressed buttons
        pressed = set(trellis.pressed_keys)
        pressed_list=list(pressed)
        if len(pressed_list)==0:
            if single_note_pressed not in path:
                trellis.pixels[single_note_pressed] = INACTIVE_COLOR
        elif len(pressed_list)==1:
            single_note_pressed=pressed_list[0]
            trellis.pixels[single_note_pressed] = ACTIVE_COLOR

        elif len(pressed_list)>1:
            if single_note_pressed not in path:
                trellis.pixels[single_note_pressed] = INACTIVE_COLOR

            print(pressed_list)
            line=[]
            path=[]
            first_press=0
            second_press=1

            #
            if pressed_list[first_press][column]==pressed_list[second_press][column]:
                path.append(pressed_list[first_press])
                pass
                #print('pass')
            elif pressed_list[first_press][column]<pressed_list[second_press][column]:
                #print('first column logic executed')
                for step in range(pressed_list[first_press][column], pressed_list[second_press][column]+1):
                    line.append((pressed_list[first_press][row], step))
                path=line

            else:
                #print('second column logic executed')
                for step in range(pressed_list[second_press][column], pressed_list[first_press][column]+1):
                    line.append((pressed_list[first_press][row], step))
                path=sorted(line, reverse=True)

                #last_point=(pressed_list[first_press][row], step)
                #print(last_point)


            last_point=path[-1]
            line=[]

            if pressed_list[first_press][row] == pressed_list[second_press][row]:
                pass
            elif pressed_list[first_press][row] < pressed_list[1][row]:
                #print('first row logic executed')
                for step in range(pressed_list[first_press][row]+1, pressed_list[second_press][row]+1):
                    line.append((step, pressed_list[second_press][column]))
                path+=line

            else:
                #print('second row logic executed')
                for step in range(pressed_list[second_press][row], pressed_list[first_press][row]+1):
                    if (step, last_point[column]) not in path:
                        line.append((step, last_point[column]))
                path+=sorted(line, reverse=True)

            print(f"Points: {pressed_list}\nPath:\n{path}")


            if path != previous_path:
                print('path changed')
                sequence_length=len(path)
                step_number=0
                previous_path=path
                #re
                for step in step_list:
                    if step not in path:
                        trellis.pixels[step] = INACTIVE_COLOR
                    else:
                        trellis.pixels[step] = ACTIVE_COLOR
                previous_step_number=1000
                previous_divided_step_number=1000
                step_count=0
                step_log_temp=[]
            

        time.sleep(0.1)  # a little delay here helps avoid debounce annoyances
