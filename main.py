# import sqlite3
#
# db = sqlite3.connect("books-collection.db")
# cursor = db.cursor()
#
# cursor.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title varchar(250) NOT NULL UNIQUE,"
#                "author varchar(250) NOT NULL, rating FLOAT NOT NULL)")
#
# cursor.execute("INSERT INTO books VALUES(1, 'Harry Potter', 'J. K. Rowling', '9.3')")
# db.commit()

from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float


# create the app
app = Flask(__name__)

# Create Database
class Base(DeclarativeBase):
  pass

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

# Create the extension
db = SQLAlchemy(model_class=Base)

# initialize the app with the extension
db.init_app(app)


# Create Table
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

# with app.app_context():
#     new_book = Book(id=1, title="Harry Potter", author="J. K. Rowling", rating=9.3)
#     db.session.add(new_book)
#     db.session.commit()

all_books = None


@app.route("/", methods=["GET", "POST"])
def home():
    global all_books
    if request.method == "POST":
        new_rating = request.form["rating"]
        book_index = request.form["id"]
        with app.app_context():
            book_to_update = db.session.execute(db.select(Book).where(Book.id == book_index)).scalar()
            book_to_update.rating = new_rating
            db.session.commit()

    books = db.session.execute(db.select(Book).order_by(Book.title)).scalars().all()
    all_books = books
    return render_template("home.html", books=books)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        new_book_dict = Book(
            title = request.form["title"],
            author = request.form["author"],
            rating = request.form["rating"]
        )
        print("new book dict: ", new_book_dict)
        db.session.add(new_book_dict)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_book.html")


@app.route("/edit/<int:index>")
def edit_book(index):
    print("test1: ", all_books)
    for book in all_books:
        if book.id == index:
            return render_template("edit_book.html", book=book)


@app.route("/delete")
def delete_book():
    book_id = request.args.get("index")
    book_to_delete = db.get_or_404(Book, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)