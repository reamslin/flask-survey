from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"

debug = DebugToolbarExtension(app)

@app.route('/')
def show_select_survey():
    """shows selection of surveys for user to choose from"""
    survey_titles = surveys.keys()

    return render_template('select.html', titles=survey_titles)

@app.route('/begin_survey', methods=['POST'])
def show_begin_survey():
    """shows the title and instructions and a button to begin survey"""

    survey_key = request.form['survey_title']
    session['survey_key'] = survey_key
    session['responses'] = []

    survey = surveys.get(survey_key)
    title = survey.title
    instructions = survey.instructions
    
    return render_template('begin.html', title=title, instructions=instructions)

@app.route('/question/<int:qid>')
def show_question(qid):
    """shows a question from the survey"""
    survey_key = session['survey_key']
    survey = surveys.get(survey_key)
    responses = session['responses']
    correct_qid = len(responses)
    if correct_qid == len(survey.questions):
        # all responses are already submitted
        flash('You have finished the survery and cannot access questions')
        return redirect('/thankyou')
    if not qid == correct_qid:
        # trying to go to question out of order
        flash('Please stop tinkering. You need to answer the questions in order.')
        return redirect(f'/question/{correct_qid}')

    question_obj = survey.questions[qid]
    question = question_obj.question
    choices = question_obj.choices
    allow_text = question_obj.allow_text


    return render_template('question.html', id=qid, question=question, choices=choices, allow_text=allow_text)

@app.route('/answer', methods=["POST"])
def get_answer():
    """retrieves answer and puts it in db"""

    survey_key = session['survey_key']
    survey = surveys.get(survey_key)
    responses = session['responses']
    answer = request.form["choice"]
    comment = request.form.get('comment')
    responses.append((answer, comment))
    session['responses'] = responses
    next_qid = len(responses)

    if (next_qid >= len(survey.questions)):
        return redirect('/thankyou')

    return redirect(f'/question/{next_qid}')

@app.route('/thankyou')
def show_thankyou():
    """shows a thank you message to the user"""
    survey_key = session['survey_key']
    survey = surveys.get(survey_key)
    responses = session['responses']
    questions = [q.question for q in survey.questions]
    zipped = zip(questions, responses)
    return render_template('thankyou.html', zipped=zipped)