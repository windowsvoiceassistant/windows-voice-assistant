import time
import re
import sys
import os
import webbrowser
import keyboard
import mouse
import pyaudio
import tkinter as tk
credential_path = r"C:\Users\Simon\Desktop\voice-python.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
from google.cloud import speech_v1 as speech
from google.cloud.speech_v1 import enums
from six.moves import queue
# Audio recording parameters
STREAMING_LIMIT = 10000
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms



def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

    def __enter__(self):

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):

        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round((self.final_request_end_time -
                                            self.bridging_offset) / chunk_time)

                    self.bridging_offset = (round((
                        len(self.last_audio_input) - chunks_from_ms)
                                                  * chunk_time))

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b''.join(data)



def sleep():
    time.sleep(0.05)

global tk_on
tk_on = False
def grid(transcript):
    global root
    global step_width
    global step_height
    tk_on = True
    root = tk.Tk()

    root.overrideredirect(True)
    root.lift()
    root.wm_attributes("-topmost", True)
    root.attributes('-alpha', 0.5)

    root.wm_attributes("-transparentcolor", "brown")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    step_peprcentage = 0.1
    step_width = int(screen_width * step_peprcentage)
    step_height = int(screen_height * step_peprcentage)

    c = tk.Canvas(root,height=screen_height, width=screen_width, bg = "brown")

    c.delete('grid_line') 

    max_size = 10
    screen_width_count = 0
    for i in range(0 , max_size):
        c.create_line([(screen_width_count, 0), (screen_width_count, screen_height)], tag='grid_line')
        screen_width_count = screen_width_count + step_width

    screen_height_count = 0
    for i in range(0 , max_size):
        c.create_line([(0, screen_height_count), (screen_width, screen_height_count)], tag='grid_line')
        screen_height_count = screen_height_count + step_height

    
    c.pack(fill=tk.BOTH, expand=True)

    column_count = 0
    row_count = 0
    for x in range(0, max_size):
        for y in range(0, max_size):
            column = int(column_count /step_height)
            row = int(row_count /step_width)
    
            number = row + 10*column+1
            l = tk.Label(root, text=str(number), bg="black",fg="white")
            l.place(relx=(row_count/screen_width), rely=(column_count/screen_height))

            column_count = column_count + step_height
        row_count = row_count + step_width
        column_count = 0
    
    root.update()

def grid_move(transcript):
    numbers = transcript.split()

    if tk_on == False:
        print("No grid yet")
    elif len(numbers) == 1:
        root.destroy()
    else:
        if numbers[1] == "V":
            numbers[1] = "5"
        if numbers[1].isnumeric():
            hold = int(numbers[1])
            square = int(numbers[1])
            column = square % 10
            square = (square-column) / 10
            row = square % 10
            if column == 0:
                column = 10
                row = row - 1
            if row == 0 and hold > 10:
                row = 10

            mouse.move((column * step_width) - step_width/2, (row * step_height) + step_height/2, absolute=True, duration=0)
            root.destroy()
        else:
            root.destroy()
    
def volume_output(num):
    previous = mouse.get_position()
    mouse.move(1360, 900, absolute=True, duration=0)
    time.sleep(0.05)
    mouse.click(button='left')
    scale = 1242 + ((1472 - 1242)/100)*num
    time.sleep(0.5)
    mouse.move(scale, 797, absolute=True, duration=0)
    time.sleep(0.05)
    mouse.click(button='left')
    time.sleep(0.05)
    mouse.move(1360, 900, absolute=True, duration=0)
    time.sleep(0.05)
    mouse.click(button='left')
    time.sleep(0.05)
    mouse.move(previous[0], previous[1], absolute=True, duration=0)

def keyboard_up():
    mouse.wheel(delta=7)
def keyboard_down():
    mouse.wheel(delta=-7)


def mouse_move(transcript):
    words = transcript.split()
    direction = words[0]
    num = 1
    if len(words) == 1:
        num = 1
    elif words[1].isnumeric():
        num = int(words[1])

    if direction == "r":
        mouse.move(50*num, 0, absolute=False, duration=0)
    elif direction == "l":
        mouse.move(-50*num, 0, absolute=False, duration=0)
    elif direction == "u":
        mouse.move(0, -50*num, absolute=False, duration=0)
    elif direction == "d":
        mouse.move(0, 50*num, absolute=False, duration=0)

def reopen(transcript):
    keyboard.press_and_release("ctrl+shift+t")

def search_for(transcript):
    parse = transcript.replace(" ","").lower()
    if "youtubefor" in parse:
        query = transcript[transcript.lower().find("youtube for ")+len("youtube for "):]
        webbrowser.open("http://www.youtube.com/results?search_query="+query)
    elif "googlefor" in parse:
        query = transcript[transcript.lower().find("google for ")+len("google for "):]
        webbrowser.open("https://www.google.com/search?q="+query)

def type_message(transcript):
    send_message = transcript[transcript.lower().find("type ")+len("type "):]
    keyboard.write(send_message)

def send_message(transcript):
    send_message = transcript[transcript.lower().find("send ")+len("send "):]
    keyboard.write(send_message)
    sleep()
    keyboard.press_and_release("enter")

def clear_message(transcript):
    keyboard.press_and_release("ctrl+a")
    sleep()
    keyboard.press_and_release("backspace")

def open_site(transcript):
    parse = transcript[transcript.lower().find("open ")+len("open "):]
    if parse.replace(" ","") != "":
        test = "www." + parse + ".com"
        webbrowser.open(test)

def close_window(transcript):
    if "close tab" in transcript:
        num_tab = transcript[transcript.lower().find("close tab ")+len("close tab "):]
        close_tab = "ctrl+" + num_tab
        try:
            keyboard.press_and_release(close_tab)
            sleep()
            keyboard.press_and_release('ctrl+w')
        except:
            print("Not Recognized")
    elif "close grid" in transcript:
        root.destroy()

    else:
        keyboard.press_and_release("alt+F4")

def minimize_window(transcript):
    keyboard.press_and_release("windows+d")

def right_click(transcript):
    mouse.right_click()

def enter_key(transcript):
    keyboard.press_and_release("enter")

def back_key(transcript):
    keyboard.press_and_release("alt+left")

def forward_key(transcript):
    keyboard.press_and_release("alt+right")
    
def fullscreen(transcript):
    keyboard.press_and_release("f")

def alt_tab(transcript):
    keyboard.press_and_release("alt+tab")

def scroll(transcript):
    up_or_down = transcript.split()
    if up_or_down[1] == "up":
        keyboard_up()
    elif up_or_down[1] == "down":
        keyboard_down()

def click(transcript):
    mouse.click(button='left')

def goto(transcript):
    if "go to tab" in transcript: 
        num_tab = transcript[transcript.find("go to tab ")+len("go to tab "):]
        go_to_tab = "ctrl+" + num_tab
        try:
            keyboard.press_and_release(go_to_tab)
        except:
            print("Not Recognized")

def copy_message(transcript):
    mouse.click(button='left')
    sleep()
    keyboard.press_and_release("ctrl+a")
    sleep()
    keyboard.press_and_release("ctrl+c")

def paste_message(transcript):
    mouse.click(button='left')
    sleep()
    keyboard.press_and_release("ctrl+v")

def zoom(transcript):
    in_or_out = transcript.split()
    if in_or_out[1] == "in":
        keyboard.press("ctrl")
        sleep()
        mouse.wheel(delta=5)
        sleep()
        keyboard.release("ctrl")

    elif in_or_out[1] == "out":
        keyboard.press("ctrl")
        sleep()
        mouse.wheel(delta=-5)
        sleep()
        keyboard.release("ctrl")

def next_cycle(transcript):
    print("Not recognized")


parse_dict = {
    "reopen" :  reopen , 
    "search" :  search_for ,  
    "type" :  type_message ,
    "send" :  send_message ,
    "clear" : clear_message ,
    "open" :  open_site ,
    "close" :  close_window ,
    "minimize" :  minimize_window ,
    "right" : right_click ,
    "enter" : enter_key ,
    "back"  : back_key ,
    "forward" : forward_key ,
    "fullscreen" : fullscreen,
    "switch" : alt_tab , 
    "scroll" : scroll ,
    "click" : click ,
    "go" : goto ,
    "copy" : copy_message ,
    "paste" : paste_message ,
    "zoom" : zoom,
    "grid" : grid,
    "section" : grid_move,
    "d": mouse_move,
    "l": mouse_move,
    "u": mouse_move,
    "r": mouse_move

}

def processInput(transcript):

    words = transcript.lower().split()
    parse_dict.get(words[0], next_cycle)(transcript)
    print(transcript)

    """


    elif "setvolumeto" in parse:
        word = parse[parse.find("setvolumeto")+len("setvolumeto"):]
        number = ""
        for i in range(len(word)):
            if word[i].isnumeric():
                number = number + word[i]
        if number.isnumeric():
            number = int(number)
            volume_output(number)
    """

    


def listen_print_loop(responses, stream):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """

    for response in responses:

        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]

        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        result_seconds = 0
        result_nanos = 0
        if result.result_end_time.seconds:
            result_seconds = result.result_end_time.seconds

        if result.result_end_time.nanos:
            result_nanos = result.result_end_time.nanos

        stream.result_end_time = int((result_seconds * 1000)
                                     + (result_nanos / 1000000))
        corrected_time = (stream.result_end_time - stream.bridging_offset
                          + (STREAMING_LIMIT * stream.restart_counter))
        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.

        if result.is_final:
            sys.stdout.write(str(corrected_time) + ': ' + transcript + '\n')

            processInput(transcript)

            stream.is_final_end_time = stream.result_end_time
            stream.last_transcript_was_final = True

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                sys.stdout.write('Exiting...\n')
                stream.closed = True
                break

        else:
            sys.stdout.write(str(corrected_time) + ': ' + transcript + '\r')
            stream.last_transcript_was_final = False


def main():
    client = speech.SpeechClient()
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code='en-US',
        speech_contexts=[speech.types.SpeechContext(
        phrases=["grid","d","l","u","r","type","close grid", "set volume to","minimize window", "close tab", "copy", "clear","paste","go to tab", "scroll up", "scroll down", "fullscreen", "back","switch","forward","enter","zoomin","zoomout"])],
        max_alternatives=1)
    streaming_config = speech.types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)
    print(mic_manager.chunk_size)
    sys.stdout.write('\nListening, say "Quit" or "Exit" to stop.\n\n')
    with mic_manager as stream:

        while not stream.closed:
            sys.stdout.write('\n' + str(
                STREAMING_LIMIT * stream.restart_counter) + ': NEW REQUEST\n')

            stream.audio_input = []
            audio_generator = stream.generator()

            requests = (speech.types.StreamingRecognizeRequest(
                audio_content=content)for content in audio_generator)

            responses = client.streaming_recognize(streaming_config,
                                                   requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses, stream)

            if stream.result_end_time > 0:
                stream.final_request_end_time = stream.is_final_end_time
            stream.result_end_time = 0
            stream.last_audio_input = []
            stream.last_audio_input = stream.audio_input
            stream.audio_input = []
            stream.restart_counter = stream.restart_counter + 1

            if not stream.last_transcript_was_final:
                sys.stdout.write('\n')
            stream.new_stream = True


if __name__ == '__main__':
    main()