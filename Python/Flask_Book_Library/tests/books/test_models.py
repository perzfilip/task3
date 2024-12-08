import unittest

from project import app, db, books
from project.books.models import Book


class TestBookModel(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down test environment"""
        with app.app_context():
            db.drop_all()

    # Correct data tests
    def test_create_book_and_add_to_database(self):
        """Test that a Book instance can be created and added to the database."""
        with app.app_context():
            book = Book(name="Book Name", author="Test Name", year_published=2000, book_type="Fiction")
            db.session.add(book)
            db.session.commit()

            # check that the book was added to the database
            self.assertEqual(Book.query.count(), 1)

            # check data in database
            book = Book.query.first()
            self.assertEqual(book.name, "Book Name")
            self.assertEqual(book.author, "Test Name")
            self.assertEqual(book.year_published, 2000)
            self.assertEqual(book.book_type, "Fiction")
            self.assertEqual(book.status, "available")

    def test_repr_method_returns_correct_string_representation(self):
        """Test the __repr__ method of the Book model."""
        book = Book(name="Test", author="Test Name", year_published=2000, book_type="Fiction")
        self.assertEqual(
            repr(book),
            "Book(ID: None, Name: Test, Author: Test Name, Year Published: 2000, Type: Fiction, Status: available)"
        )

    def test_raise_error_for_duplicate_book_name(self):
        """Test that an error is raised if a book with the same name is added"""
        with app.app_context():
            book1 = Book(name="Name", author="Test Name1", year_published=2000, book_type="Fantasy")
            book2 = Book(name="Name", author="Test Name2", year_published=2000, book_type="Fiction")
            db.session.add(book1)
            db.session.commit()
            db.session.add(book2)
            with self.assertRaises(Exception):
                db.session.commit()

    def test_default_status_is_available(self):
        """Test that the default value of the status field is 'available'."""
        with app.app_context():
            book = Book(name="Test", author="Test Name", year_published=2000, book_type="Fiction")
            db.session.add(book)
            db.session.commit()
            self.assertEqual(book.status, "available")

    def test_update_book_status_successfully(self):
        """Test that the status of a book can be updated."""
        with app.app_context():
            book = Book(name="1984", author="George Orwell", year_published=1949, book_type="Fiction")
            db.session.add(book)
            db.session.commit()
            book.status = "checked out"
            db.session.commit()
            updated_book = Book.query.filter_by(name="1984").first()
            self.assertEqual(updated_book.status, "checked out")


    # Incorrect data tests
    def test_name_cannot_be_longer_than_64_characters(self):
        """Test that the name field cannot be longer than 64 characters."""
        with app.app_context():
            book = Book(name="a"*65, author="Test Name", year_published=2000, book_type="Fiction")
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()

    def test_author_cannot_be_longer_than_64_characters(self):
        """Test that the author field cannot be longer than 64 characters."""
        with app.app_context():
            book = Book(name="Test", author="a"*65, year_published=2000, book_type="Fiction")
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()

    def test_year_published_must_be_integer(self):
        """Test that the year_published field must be an integer."""
        with app.app_context():
            book = Book(name="Test", author="Test Name", year_published="text", book_type="Fiction")
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()

    def test_book_type_cannot_be_longer_than_20_characters(self):
        """Test that the book_type field cannot be longer than 20 characters."""
        with app.app_context():
            book = Book(name="Test", author="Test Name", year_published=2000, book_type="a"*21)
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()

    # malicious data tests
    def test_name_should_not_allow_sql_injection(self):
        """Test that the name field does not allow for SQL injection."""
        with app.app_context():
            book = Book(name="'; DROP TABLE books; --", author="Test Name", year_published=2000, book_type="Fiction")
            with self.assertRaises(Exception):
                db.session.add(book)
                db.session.commit()

    def test_name_should_not_allow_xss_attacks(self):
        """Test that the name field does not allow for XSS attacks."""
        with app.app_context():
            book = Book(name="<script>alert('xss');</script>", author="Test Name", year_published=2000, book_type="Fiction")
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()
                book = Book.query.first()


    # extreme values tests
    def test_name_cannot_be_1000_characters(self):
        """Test that the name field cannot be 1000 characters."""
        with app.app_context():
            book = Book(name="a"*1000, author="Test Name", year_published=2000, book_type="Fiction")
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()

    def test_author_cannot_be_1000_characters(self):
        """Test that the author field cannot be 1000 characters."""
        with app.app_context():
            book = Book(name="Test", author="a"*1000, year_published=2000, book_type="Fiction")
            db.session.add(book)
            with self.assertRaises(Exception):
                db.session.commit()


if __name__ == '__main__':
    unittest.main()