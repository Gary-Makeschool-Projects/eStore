from unittest import TestCase, main as unittest_main, mock
from app import app
import os


class MinimalTets(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True
        app.secret_key = os.urandom(24)

    def test_index(self):
        """Test the Home page homepage."""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')

    def test_register(self):
        """Test the register page."""
        result = self.client.get('/register')
        self.assertEqual(result.status, '200 OK')

    def test_login(self):
        """Test the login page."""
        result = self.client.get('/login')
        self.assertEqual(result.status, '200 OK')

    def test_cart(self):
        """Test the cart page."""
        result = self.client.get('/cart')
        self.assertIn(result.status, '302 FOUND')

    def test_add(self):
        """Test the add  page."""
        result = self.client.get('/add')
        self.assertIn(result.status, '405 METHOD NOT ALLOWED')

    def test_delete(self):
        """Test the delete page."""
        result = self.client.get('/delete')
        self.assertIn(result.status, '405 METHOD NOT ALLOWED')


if __name__ == '__main__':
    unittest_main()
