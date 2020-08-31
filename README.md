# windows-voice-assistant
Windows assistant to help control computer input and output. Powered by Google Speech-to-Text API and Python

- setup:
  - in command line:
    - Pip install keyboard
    - Pip install mouse
    - Download respective pyaudio version (from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
      - for example (pip install PyAudio-0.2.11-cp38-cp38-win_amd64.whl)
    - Pip install google-cloud
    - Pip install google-cloud-vision
    - Pip install google-cloud-speech
    - export GOOGLE_APPLICATION_CREDENTIALS="voice-python-[secretname].json"
    - python transcript.py
  - get the "secretname" by visiting google cloud console and registering api credentials for the Speech-to-text api.

Huge thank you to: https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/speech/microphone/transcribe_streaming_infinite.py
