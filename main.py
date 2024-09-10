from flask import Flask, redirect, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

# Instantiate App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy(app)

# Declare Models
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    courses = db.relationship('Course', secondary='enrollments', backref='students')

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()
    if not db.session.query(Course).count():
        courses = [
            Course(course_code="CSE01", course_name="MAD I", course_description="Modern Application Development - I"),
            Course(course_code="CSE02", course_name="DBMS", course_description="Database Management Systems"),
            Course(course_code="CSE03", course_name="PDSA", course_description="Programming, Data Structures and Algorithms using Python"),
            Course(course_code="BST13", course_name="BDM", course_description="Business Data Management")
        ]
        db.session.bulk_save_objects(courses)
        db.session.commit()

# Declare Flask Routes
@app.route('/', methods=['GET'])
def index():
    students = db.session.query(Student).all()
    return render_template('index.html', students=students)

@app.route('/student/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        courses = db.session.query(Course).all()
        return render_template('add.html', courses=courses)
    elif request.method == 'POST':
        rollno = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        courses_selected = request.form.getlist('courses')

        exist_check = db.session.query(Student).filter_by(roll_number=rollno).first()
        if exist_check:
            return render_template('exist.html')
        else:
            new_student = Student(roll_number=rollno, first_name=first_name, last_name=last_name)
            for course_code in courses_selected:
                course = db.session.query(Course).filter_by(course_code=course_code).first()
                if course:
                    new_student.courses.append(course)
            db.session.add(new_student)
            db.session.commit()
            return redirect(url_for('index'))

@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete(student_id):
    delete_student = db.session.query(Student).filter_by(student_id=student_id).first()
    if delete_student:
        db.session.delete(delete_student)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/student/<int:student_id>/', methods=['GET'])
def view(student_id):
    details_student = db.session.query(Student).filter_by(student_id=student_id).first()
    if details_student:
        return render_template('view.html', student=details_student)
    else:
        return redirect(url_for('index'))  # or render a 404 page

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update(student_id):
    if request.method == 'GET':
        student_details = db.session.query(Student).filter_by(student_id=student_id).first()
        if student_details:
            courses = db.session.query(Course).all()
            return render_template('update.html', student=student_details, courses=courses, student_id=student_id)
        else:
            return redirect(url_for('index'))
    elif request.method == 'POST':
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        courses_selected = request.form.getlist('courses')

        update_student = db.session.query(Student).filter_by(student_id=student_id).first()
        if update_student:
            update_student.first_name = first_name
            update_student.last_name = last_name
            update_student.courses.clear()

            for course_code in courses_selected:
                course = db.session.query(Course).filter_by(course_code=course_code).first()
                if course:
                    update_student.courses.append(course)

            db.session.commit()
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
