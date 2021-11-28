# Survey Builder for IIIT Empirical Researchers
**(Software System Development Project)**
### Prerequisites
- Open terminal window in the project directory.
- Create a virtual environment for python
    > ```python3 -m venv env```
- Activate the Virtual environment you created
    > ```source env/bin/activate```
- Install Dependencies:
    > Install Flask: ```pip install Flask```
    > Install Flask SQLAlchemy: ```pip install Flask_SQLAlchemy```
    > Install Speech Recognition: ```pip install SpeechRecognition```
    > Install pydub: ```pip install pydub```
- Also need to install **ffmpeg** for converting mp3 to wav for speech recognition
    > For Mac-OS install it using Homebrew: ```brew install ffmpeg``` and then update brew using ```brew update```
    > For Linux based systems- ```sudo apt install ffmpeg```
- To deactivate the virtual environment simply enter ```deactivate```
### How to Run?
- **Enter command** ```python app.py```
    > This will start the flask server at local host and listen for incoming request at port ***5000***
- To open the application enter ```http://127.0.0.1:5000``` in browser
- You're all set, Build your custom survey and enjoy!