import pytest
from src.library_manager import Book, LibraryManager


@pytest.fixture
def empty_library():
    """Fixture returning an empty library."""
    return LibraryManager()


@pytest.fixture
def sample_books():
    """Fixture returning a list of sample books."""
    return [
        Book(1, "The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy"),
        Book(2, "Pride and Prejudice", "Jane Austen", 1813, "Romance"),
        Book(3, "1984", "George Orwell", 1949, "Dystopian"),
        Book(4, "To Kill a Mockingbird", "Harper Lee", 1960, "Fiction"),
        Book(5, "The Great Gatsby", "F. Scott Fitzgerald", 1925, "Fiction")
    ]


@pytest.fixture
def library_with_books(empty_library, sample_books):
    """Fixture returning a library with sample books already added."""
    library = empty_library
    for book in sample_books:
        library.add_book(book)
    return library


class TestBookAddition:
    def test_add_book(self, empty_library, sample_books):
        """Test adding a book to the library."""
        result = empty_library.add_book(sample_books[0])

        assert result is True
        assert len(empty_library.books) == 1
        assert empty_library.get_book(1) == sample_books[0]

    def test_add_duplicate_book(self, library_with_books, sample_books):
        """Test adding a book with existing ID."""
        result = library_with_books.add_book(sample_books[0])

        assert result is False
        assert len(library_with_books.books) == 5  # Count remains the same

    def test_add_invalid_book(self, empty_library):
        """Test adding an invalid object as a book."""
        with pytest.raises(TypeError, match="Object must be of type Book"):
            empty_library.add_book("Not a book")


class TestBookRetrieval:
    def test_get_existing_book(self, library_with_books, sample_books):
        """Test retrieving an existing book."""
        book = library_with_books.get_book(1)

        assert book == sample_books[0]

    def test_get_nonexistent_book(self, library_with_books):
        """Test retrieving a book that doesn't exist."""
        book = library_with_books.get_book(999)

        assert book is None


class TestBookRemoval:
    def test_remove_book(self, library_with_books):
        """Test removing a book from the library."""
        result = library_with_books.remove_book(1)

        assert result is True
        assert len(library_with_books.books) == 4
        assert library_with_books.get_book(1) is None

    def test_remove_nonexistent_book(self, library_with_books):
        """Test removing a book that doesn't exist."""
        result = library_with_books.remove_book(999)

        assert result is False
        assert len(library_with_books.books) == 5  # Count remains the same

    def test_remove_borrowed_book(self, library_with_books):
        """Test removing a borrowed book."""
        library_with_books.borrow_book(1, "user1")

        with pytest.raises(ValueError, match="Cannot remove a borrowed book"):
            library_with_books.remove_book(1)


class TestBookBorrowing:
    def test_borrow_book(self, library_with_books):
        """Test borrowing a book."""
        result = library_with_books.borrow_book(1, "user1")

        assert result is True
        assert library_with_books.books[1].is_borrowed is True
        assert library_with_books.books[1].borrow_count == 1
        assert "user1" in library_with_books.borrowed_books
        assert 1 in library_with_books.borrowed_books["user1"]

    def test_borrow_already_borrowed_book(self, library_with_books):
        """Test borrowing a book that's already borrowed."""
        library_with_books.borrow_book(1, "user1")
        result = library_with_books.borrow_book(1, "user2")

        assert result is False
        assert "user2" not in library_with_books.borrowed_books

    def test_borrow_nonexistent_book(self, library_with_books):
        """Test borrowing a book that doesn't exist."""
        with pytest.raises(ValueError, match="Book not found in library"):
            library_with_books.borrow_book(999, "user1")


class TestBookReturning:
    def test_return_book(self, library_with_books):
        """Test returning a borrowed book."""
        library_with_books.borrow_book(1, "user1")
        result = library_with_books.return_book(1, "user1")

        assert result is True
        assert library_with_books.books[1].is_borrowed is False
        assert "user1" not in library_with_books.borrowed_books  # User entry should be cleaned up

    def test_return_not_borrowed_book(self, library_with_books):
        """Test returning a book that's not borrowed."""
        result = library_with_books.return_book(1, "user1")

        assert result is False

    def test_return_book_wrong_borrower(self, library_with_books):
        """Test returning a book with wrong borrower."""
        library_with_books.borrow_book(1, "user1")

        with pytest.raises(ValueError,
                           match="Book was not borrowed by this borrower"):
            library_with_books.return_book(1, "user2")

    def test_return_nonexistent_book(self, library_with_books):
        """Test returning a book that doesn't exist."""
        with pytest.raises(ValueError, match="Book not found in library"):
            library_with_books.return_book(999, "user1")


class TestBookSearch:
    @pytest.mark.parametrize("criteria, expected_count", [
        ({"title": "The"}, 2),  # "The Hobbit" and "The Great Gatsby"
        ({"author": "J.R.R. Tolkien"}, 1),
        ({"year_from": 1930, "year_to": 1960}, 3),
        # Books from 1937, 1949, and 1960
        ({"genre": "Fiction"}, 2),
        ({"title": "The", "genre": "Fantasy"}, 1),  # Only "The Hobbit"
        ({"available_only": True}, 5),  # All books are available initially
    ])
    def test_search_books(self, library_with_books, criteria, expected_count):
        """Test searching books with various criteria."""
        results = library_with_books.search_books(criteria)

        assert len(results) == expected_count

    def test_search_with_borrowed_books(self, library_with_books):
        """Test searching for available books when some are borrowed."""
        library_with_books.borrow_book(1, "user1")

        results = library_with_books.search_books({"available_only": True})
        assert len(results) == 4

        for book in results:
            assert book.is_borrowed is False


class TestLibraryStatistics:
    def test_statistics_empty_library(self, empty_library):
        """Test statistics for an empty library."""
        stats = empty_library.get_statistics()

        assert stats["total_books"] == 0
        assert stats["available_books"] == 0
        assert stats["borrowed_books"] == 0
        assert stats["borrowers_count"] == 0
        assert stats["genres"] == {}
        assert stats["popular_books"] == []

    def test_statistics_with_books(self, library_with_books):
        """Test statistics for a library with books."""
        stats = library_with_books.get_statistics()

        assert stats["total_books"] == 5
        assert stats["available_books"] == 5
        assert stats["borrowed_books"] == 0
        assert stats["borrowers_count"] == 0
        assert len(
            stats["genres"]) == 4  # Fantasy, Romance, Dystopian, Fiction
        assert stats["genres"]["Fiction"] == 2
        assert len(stats["popular_books"]) == 5

    def test_statistics_with_borrowed_books(self, library_with_books):
        """Test statistics when some books are borrowed."""
        # Borrow some books
        library_with_books.borrow_book(1, "user1")
        library_with_books.borrow_book(2, "user1")
        library_with_books.borrow_book(3, "user2")

        # Borrow and return to increase borrow count
        library_with_books.borrow_book(4, "user3")
        library_with_books.return_book(4, "user3")
        library_with_books.borrow_book(4, "user3")
        library_with_books.return_book(4, "user3")

        stats = library_with_books.get_statistics()

        assert stats["total_books"] == 5
        assert stats["available_books"] == 2
        assert stats["borrowed_books"] == 3
        assert stats["borrowers_count"] == 3

        # Book 4 should be most popular with borrow_count=2
        assert stats["popular_books"][0].book_id == 4
        assert stats["popular_books"][0].borrow_count == 2