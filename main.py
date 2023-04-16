from flask import Flask, render_template, redirect, request, abort

from data import db_session
from data.group_class import Group, GroupForm
from data.question_class import Question, QuestionForm
from data.student_class import Student, StudentForm
from data.quiz_class import Quiz, QuizForm
from data.test_class import Test
from data.register_form import RegisterForm
from data.login_form import LoginForm
from generate_quiz import generate_quiz, generate_full

db_session.global_init("db/digital_footprint.db")

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    app.run(host='127.0.0.1', port=8080, debug=True, use_reloader=False)


@app.route("/questions", methods=['GET', 'POST'])
def questions():
    query_questions = db_sess.query(Question).all()
    query_groups = db_sess.query(Group)
    return render_template('questions.html', query_questions=query_questions, query_groups=query_groups,
                           title="Вопросы")


@app.route('/questions/add/<int:id>', methods=['GET', 'POST'])
def add_questions(id):
    query_questions = db_sess.query(Question).all()
    query_groups = db_sess.query(Group)
    form = QuestionForm()
    theme = query_groups.filter_by(id_group=id).first().label
    if form.validate_on_submit():
        question = Question()
        question.texts = form.content.data
        question.id_group = id
        db_sess.add(question)
        db_sess.commit()
        return redirect('/questions')
    return render_template('questions_add.html', query_questions=query_questions, query_groups=query_groups,
                           title="Вопросы", form=form, theme=theme)


@app.route('/questions/<int:id>', methods=['GET', 'POST'])
def edit_questions(id):
    form = QuestionForm()
    theme = 0
    if request.method == "GET":
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id_question == id).first()
        group = db_sess.query(Group)
        theme = group.filter_by(id_group=question.id_group).first().label
        if question:
            form.content.data = question.texts
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = db_sess.query(Question).filter(Question.id_question == id).first()
        group = db_sess.query(Group)
        if question:
            question.texts = form.content.data
            db_sess.commit()
            return redirect('/questions')
        else:
            abort(404)

    return render_template('questions_edit.html', title="ниЧиво?", form=form, id=id, theme=theme)


@app.route('/questions_delete/<int:id>', methods=['GET', 'POST'])
def questions_delete(id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id_question == id).first()
    if question:
        db_sess.delete(question)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/questions')


@app.route("/students", methods=['GET', 'POST'])
def students():
    query_students = db_sess.query(Student).all()
    form = StudentForm()
    if form.validate_on_submit():
        student = Student()
        student.name = form.name.data
        student.birthday = form.date.data
        student.id_stepik = form.id_stepik.data
        db_sess.add(student)
        db_sess.commit()

        return redirect('/students')
    return render_template('students.html', query_students=query_students,
                           title="Студенты", form=form)


@app.route('/students/<int:id>', methods=['GET', 'POST'])
def students_edit(id):
    form = StudentForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        student = db_sess.query(Student).filter(Student.id_student == id).first()
        if student:
            form.name.data = student.name
            form.date.data = student.birthday
            form.id_stepik.data = student.id_stepik
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        student = db_sess.query(Student).filter(Student.id_student == id).first()
        if student:
            student.name = form.name.data
            student.birthday = form.date.data
            student.id_stepik = form.id_stepik.data
            db_sess.commit()
            return redirect('/students')
        else:
            abort(404)
    return render_template('students_edit.html', title="ниЧиво?", form=form, id=student.id_student)


@app.route('/students_delete/<int:id>', methods=['GET', 'POST'])
def students_delete(id):
    db_sess = db_session.create_session()
    student = db_sess.query(Student).filter(Student.id_student == id).first()
    if student:
        db_sess.delete(student)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/students')


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    query_groups = db_sess.query(Group).all()
    form = GroupForm()
    if form.validate_on_submit():
        group = Group()
        group.label = form.label.data
        db_sess.add(group)
        db_sess.commit()
        return redirect('/groups')
    return render_template('groups.html', query_groups=query_groups,
                           title="Группы", form=form)


@app.route('/groups/<int:id>', methods=['GET', 'POST'])
def edit_groups(id):
    form = GroupForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id_group == id).first()
        if group:
            form.label.data = group.label
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        group = db_sess.query(Group).filter(Group.id_group == id).first()
        if group:
            group.label = form.label.data
            db_sess.commit()
            return redirect('/groups')
        else:
            abort(404)
    return render_template('groups_edit.html', title="ниЧиво?", form=form, id=group.id_group)


@app.route('/groups_delete/<int:id>', methods=['GET', 'POST'])
def groups_delete(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id_group == id).first()
    if group:
        db_sess.delete(group)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/groups')


@app.route('/quiz/<int:id>', methods=['GET', 'POST'])
def quiz(id):
    db_sess = db_session.create_session()
    query_quiz = db_sess.query(Quiz).filter(Quiz.id_quiz == id)
    tests = db_sess.query(Test).filter(Test.id_quiz == id).all()
    quests = []
    for i in tests:
        quests.append(db_sess.query(Question).filter(Question.id_question == i.id_question).first())
    form = QuizForm()
    if form.validate_on_submit():
        for i in range(5):
            tests[i].stud_answers = form.answers.data[i]
        db_sess.commit()
        return redirect("/")

    db_sess.commit()

    return render_template('quiz_page.html', id=id, questions_num=5,
                           query_questions=quests, title="Тестирование", form=form, timer=10)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        student = Student(
            name=form.name.data,
            birthday=form.birthday.data,
            id_stepik=form.stepik_id.data
        )
        db_sess.add(student)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    db_sess = db_session.create_session()
    # generate_full([1, 2], groups=[1])
    main()
