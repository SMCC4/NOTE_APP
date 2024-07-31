from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Comment
from . import db
import json

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)


@views.route("/notes", methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            # Providing the schema for the note
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)  # Adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("notes.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    # this function expects a JSON from the INDEX.js file
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()


@views.route('/comments', methods=['GET', 'POST'])
@login_required
def handle_comments():
    if request.method == 'POST':
        comment_data = request.form.get('comment')
        note_id = request.form.get('note_id')

        if len(comment_data) < 1:
            flash('Comment is too short!', category='error')
            return jsonify({'error': 'Comment is too short!'}), 400

        new_comment = Comment(
            data=comment_data, user_id=current_user.id, note_id=note_id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'id': new_comment.id, 'data': new_comment.data}), 201

    elif request.method == 'GET':
        note_id = request.args.get('note_id')
        comments = Comment.query.filter_by(note_id=note_id).all()
        comments_data = [{'id': comment.id, 'data': comment.data}
                         for comment in comments]
        return jsonify({'comments': comments_data}), 200


@views.route('/comments/<int:id>', methods=['DELETE'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    if comment.user_id != current_user.id:
        return jsonify({'error': 'You do not have permission to delete this comment'}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'}), 200


@views.route("/about")
def about():
    return render_template("about.html", user=current_user)


@views.route('/')
def index():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', notes=notes)


@views.route('/add-note', methods=['POST'])
@login_required
def add_note():
    note_data = request.form.get('note')
    if len(note_data) < 1:
        flash('Note is too short!', category='error')
        return jsonify({'error': 'Note is too short!'}), 400

    new_note = Note(data=note_data, user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'id': new_note.id, 'data': new_note.data}), 201
