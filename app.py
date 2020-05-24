from flask import Flask, request, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"

debug = DebugToolbarExtension(app)

responses = []
@app.route('/')
def show_select_survey():
    """shows selection of surveys for user to choose from"""
    survey_titles = surveys.keys()

    return render_template('select.html', titles=survey_titles)

@app.route('/begin_survey')
def show_begin_survey():
    """shows the title and instructions and a button to begin survey"""
    survey_key = request.args['survey_title']
    survey = surveys.get(survey_key)
    title = survey.title
    instructions = survey.instructions
    
    return render_template('begin.html', survey=survey_key, title=title, instructions=instructions)

@app.route('/<survey_key>/question/<int:qid>')
def show_question(survey_key, qid):
    """shows a question from the survey"""
    survey = surveys.get(survey_key)

    correct_qid = len(responses)
    if correct_qid == len(survey.questions):
        # all responses are already submitted
        flash('You have finished the survery and cannot access questions')
        return redirect(f'{survey_key}/thankyou')
    if not qid == correct_qid:
        # trying to go to question out of order
        flash('Please stop tinkering. You need to answer the questions in order.')
        return redirect(f'/{survey_key}/question/{correct_qid}')

    question_obj = survey.questions[qid]
    question = question_obj.question
    choices = question_obj.choices
    allow_text = question_obj.allow_text


    return render_template('question.html', survey=survey_key, id=qid, question=question, choices=choices, allow_text=allow_text)

@app.route('/<survey_key>/answer/<int:qid>', methods=["POST"])
def get_answer(survey_key, qid):
    """retrieves answer and puts it in db"""

    survey = surveys.get(survey_key)
    answer = request.form["choice"]
    comment = request.form.get('comment')
    responses.append((answer, comment))
    next_qid = qid + 1

    if (next_qid >= len(survey.questions)):
        return redirect(f'/{survey_key}/thankyou')

    return redirect(f'/{survey_key}/question/{qid + 1}')

@app.route('/<survey_key>/thankyou')
def show_thankyou(survey_key):
    """shows a thank you message to the user"""
    survey = surveys.get(survey_key)
    questions = [q.question for q in survey.questions]
    zipped = zip(questions, responses)
    return render_template('thankyou.html', zipped=zipped)