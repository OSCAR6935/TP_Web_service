# routes/students.py
from flask import Blueprint, request, jsonify
from models import db, Student, Book, StudentBook
from datetime import datetime


students_bp = Blueprint('students', __name__)

# Récupérer tous les étudiants
@students_bp.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([
        {'id': s.id, 'email': s.email, 'first_name': s.first_name, 'last_name': s.last_name, 'birth_date': s.birth_date.strftime('%Y-%m-%d') if s.birth_date else None}
        for s in students
    ])

# Récupérer un étudiant par ID
@students_bp.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({
        'id': student.id,
        'email': student.email,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'birth_date': student.birth_date.strftime('%Y-%m-%d') if student.birth_date else None
    })

# Ajouter un étudiant
@students_bp.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data or 'email' not in data or 'first_name' not in data or 'last_name' not in data:
        return jsonify({'error': 'Invalid data, email, first_name, and last_name are required'}), 400

    student = Student(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d') if 'birth_date' in data else None
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully', 'id': student.id}), 201

# Mettre à jour un étudiant
@students_bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'email' in data:
        student.email = data['email']
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'birth_date' in data:
        student.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')

    db.session.commit()
    return jsonify({'message': 'Student updated successfully'})

# Supprimer un étudiant
@students_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})

# Emprunter un livre
@students_bp.route('/students/<int:student_id>/borrow/<int:book_id>', methods=['POST'])
def borrow_book(student_id, book_id):
    student = Student.query.get(student_id)
    book = Book.query.get(book_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Vérifier si le livre est déjà emprunté
    if StudentBook.query.filter_by(student_id=student_id, book_id=book_id, return_date=None).first():
        return jsonify({'error': 'This book is already borrowed by the student'}), 400

    # Ajouter l'emprunt
    student_book = StudentBook(student_id=student_id, book_id=book_id, borrow_date=datetime.now())
    db.session.add(student_book)
    db.session.commit()
    return jsonify({'message': 'Book borrowed successfully'}), 200

# Rendre un livre
@students_bp.route('/students/<int:student_id>/return/<int:book_id>', methods=['POST'])
def return_book(student_id, book_id):
    student = Student.query.get(student_id)
    book = Book.query.get(book_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    student_book = StudentBook.query.filter_by(student_id=student_id, book_id=book_id, return_date=None).first()
    if not student_book:
        return jsonify({'error': 'This book was not borrowed by the student'}), 400

    # Mettre à jour la date de retour
    student_book.return_date = datetime.now()
    db.session.commit()
    return jsonify({'message': 'Book returned successfully'}), 200
