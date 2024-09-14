from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizzes.db'
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    options = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.String(500), nullable=False)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
            login_user(user)
            return render_template("index.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/')
def home():
    return render_template('lr.html')


@app.route('/create_quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        data = request.get_json()
        new_quiz = Quiz(name=data['quiz_name'])
        db.session.add(new_quiz)
        db.session.commit()

        for question in data['questions']:
            new_question = Question(
                quiz_id=new_quiz.id,
                name=question['name'],
                options=question['options'],
                correct_option=question['correct_option'],
                explanation=question['explanation']
            )
            db.session.add(new_question)
        db.session.commit()

        return jsonify({'message': 'Quiz created successfully'}), 201

    return render_template('create_quiz.html')


@app.route('/quizzes')
def get_quizzes():
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)


@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def participate_quiz(quiz_id):
    if request.method == 'POST':
        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        score = 0
        total_questions = len(questions)
        user_answers = request.form.to_dict()

        for question in questions:
            if user_answers.get(f'question_{question.id}') == question.correct_option:
                score += 1
        

        # return render_template('results.html', quiz=quiz, questions=questions, user_answers=user_answers, score=score, total_questions=total_questions)
        return render_template('results.html', quiz=quiz, questions=questions, user_answers=user_answers, score=score, total_questions=total_questions, enumerate=enumerate)

    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('participate_quiz.html', quiz=quiz, questions=questions)



if __name__ == '__main__':
    app.run(debug=True)