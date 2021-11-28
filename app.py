from flask import Flask, redirect, render_template, request, url_for, session,jsonify,send_file
from flask_sqlalchemy import SQLAlchemy
from survey import SurveySystem
from database import db, app
from data_models import User, Question, Survey, Response
from werkzeug.utils import secure_filename
import os
import shutil
import speech_recognition as sr
from pydub import AudioSegment
import contextlib, wave, math
import subprocess
from io import StringIO
from pydub.utils import make_chunks


system = SurveySystem()

@app.route("/", methods=["GET", "POST"])
def index():
    # check post login data
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # attempt to authenticate
        if system.authenticate(username, password):
            surveys = Survey.query.filter_by(uid=session["user_id"]).all()
            return render_template("dashboard.html", surveys=surveys)

        return render_template("login.html", error=1)

    # check user login and redirect to their dashboard
    if system.check_login():
        #get all surveys this user created
        surveys = Survey.query.filter_by(uid=session["user_id"]).all()
        return render_template("dashboard.html", surveys=surveys)
        # return render_template("dashboard.html")

    # else, return login page
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def registerGuest():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username.isspace() or password.isspace() or username == "" or password == "":
            return render_template("register.html", error=3)

        if system.create_user(None, username, password, 1):
            # create pending enrolment
            return redirect(url_for('index'))
        else:
            return render_template("register.html", error=1)

    return render_template("register.html")


@app.route("/logout", methods=["GET"])
def logout():
    system.logout()
    return redirect(url_for('index'))



@app.route("/surveys/create", methods=["GET","POST"])
def create_survey():

    if not system.check_login(): return redirect(url_for('index'))
    
    survey_count = Survey.query.count() 
    questions = Question.query.filter_by(survey_id = survey_count+1).all()
    #getting all surveys count from database
    if request.method == "POST":
        surveyName = request.form["name"]
        surveyQs = request.form.getlist("questions")

        if surveyName.isspace() or surveyName == "" or not surveyQs:
            return render_template("create_survey.html", questions=questions, error=1)

        if system.create_survey(surveyName,survey_count+1, surveyQs):
            return redirect(url_for('index'))
            # return render_template("create_survey.html", questions=questions, success=1)
        else:
            return render_template("create_survey.html", questions=questions, error=2)
    else:
        return render_template("create_survey.html", questions=questions, survey_id=survey_count+1)


@app.route("/<sid>/question/add", methods=["GET", "POST"])
def addQuestion(sid):
    if not system.check_login(): return redirect(url_for('index'))
    if request.method == "POST":
        qText = request.form["question"]
        responses = list(filter(None, request.form.getlist("responses")))
        qType = 1
        if request.form["type"] == 'Text':
            qType = 2
            responses = []
        required = 1
        if request.form['optional'] == '1':
            required = 0

        if qText.isspace() or qText == "" or qType == 1 and (len(responses) < 2 or all(responses[i].isspace() for i in range(0, len(responses)-1))):
            return render_template("addQuestion.html", error=1)
        if system.add_question(qText, qType, required, responses,sid):
            #take out all the questions having the same survey id
            questions = Question.query.filter_by(survey_id = sid).all()
            return redirect(url_for('create_survey'))
            # return render_template("create_survey.html", questions=questions, survey_id=sid)
        else:
            return render_template("addQuestion.html", error=2)
    return render_template("addQuestion.html")


#survey page - allows responses to be collected
@app.route("/survey/<sid>", methods=["GET", "POST"])
def survey(sid):
    if not system.check_login() == 1: return redirect(url_for('index'))
    #check whether student is enrolled in course and hasn't already taken survey
    # course_ids = [r[0] for r in Enrolment.query.filter_by(u_id=session['user_id']).with_entities(Enrolment.c_id).all()]

    survey = Survey.query.filter_by(id=sid).first()

    if not survey: return render_template("survey.html", error=3)

    if Response.query.filter_by(s_id=sid, u_id=session['user_id']).first():
        return render_template("survey.html", survey=survey, success=1)

    questions = []
    for questionID in survey.questionsList():
        questions.append(system.find_question(questionID))

    if request.method == "POST":
        error = 0

        #check for required fields
        for question in questions:
            response = request.form.get(str(question.id))
            if question.required and (response == None or response.isspace() or response == ""):
                return render_template("survey.html", survey=survey, questions=questions, error=1)

        #submit responses
        for question in questions:
            response = request.form.get(str(question.id))

            if not response is None and not response.isspace() and response != "":
                if question.type == 1:
                    if not system.save_response(sid, session['user_id'], question.id, None, int(response)):
                        error = 1
                        break

                elif question.type == 2:
                    if not system.save_response(sid, session['user_id'], question.id, response, None):
                        error = 1
                        break

        if not error:
            return render_template("survey.html", survey=survey, questions=questions, success=1)
        else:
            return render_template("survey.html", survey=survey, questions=questions, error=2)

    else:
        return render_template("survey.html", survey=survey, questions=questions)

@app.route("/results/<sid>")
def results(sid):

    if not system.check_login(): return redirect(url_for('index'))

    # course_ids = [r[0] for r in Enrolment.query.filter_by(u_id=session['user_id']).with_entities(Enrolment.c_id).all()]

    survey = Survey.query.filter_by(id=sid).first()

    if not survey: return render_template("results.html", error=3)

    # if survey.c_id not in course_ids:
    #     if session['user_type'] != 3:
    #         return redirect(url_for('index'))


    questions = []
    for questionID in survey.questionsList():
        questions.append(system.find_question(questionID))

    responses = Response.query.filter_by(s_id=sid).all()

    return render_template("results.html", survey=survey, questions=questions, responses=responses)

def Audio_to_Transcript():
   subprocess.call(['ffmpeg', '-i', 'test.mp3', 'transcript.wav'])                               
   AUDIO_FILE = "transcript.wav"
   with contextlib.closing(wave.open(AUDIO_FILE,'r')) as f:
      frames = f.getnframes()
      rate = f.getframerate()
      duration = frames / float(rate)

   r = sr.Recognizer()
   f = open("transcription.txt", "w+")
   sound = AudioSegment.from_wav("transcript.wav")

   folder_name = "audio-chunks"
   if not os.path.isdir(folder_name):
      os.mkdir(folder_name)
   os.chdir(folder_name)

   chunk_length_ms = math.ceil(duration / 20) * 1000 
   chunks = make_chunks(sound , chunk_length_ms)
   for i, chunk in enumerate(chunks):
      chunk_silent = AudioSegment.silent(duration = 10)
      audio_chunk = chunk_silent + chunk + chunk_silent
      chunk_name = "{0}.wav".format(i) 
      print ("exporting", chunk_name) 
      audio_chunk.export(chunk_name, format="wav") 
   i = 0
   for chunk in chunks:
      filename = str(i)+'.wav'
      print("Processing chunk "+str(i))
      file = filename
      with sr.AudioFile(file) as source:
         r.adjust_for_ambient_noise(source)
         audio_listened = r.listen(source)
      try:
         rec = r.recognize_google(audio_listened)
         f.write(rec+". ")
      except sr.UnknownValueError:
         print("Could not understand audio")
      except sr.RequestError as e:
         print("Could not request results. check your internet connection")
      i += 1
   os.chdir('..')
   f.close()
   shutil.rmtree(os.getcwd() + "/" + folder_name)
   os.remove("test.mp3")
   os.remove("transcript.wav")

@app.route('/convert_tnx', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      # print(request.files['file'])
      f = request.files['file']
      codec = f.filename[-4:]
      f.filename = "test" + codec
      f.save(secure_filename(f.filename))
      Audio_to_Transcript()
      if os.path.exists("transcription.txt") == True:
        f = open("transcription.txt", "r")
        file_text = ""
        file_text += f.read()
        f.close()
        os.remove("transcription.txt")
        #  data = {
        #     200 : file_text
        #  }
        text_file = open("transcript.txt", "w")
        text_file.write(file_text)
        text_file.close()

        # return Response(returnfile, mimetype="text/plain", headers={"Content-disposition": "attachment; filename=output.txt"})
        #  return jsonify(data)
        return send_file("transcript.txt", as_attachment=True)
      else:
         data = {
            500 : "Audio could not be Transcribed. Faulty Audio. Please Try Again."
         }
         return jsonify(data)







if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
