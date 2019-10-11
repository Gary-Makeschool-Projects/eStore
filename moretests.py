from unittest import TestCase, main as unittest_main, mock
from app import app


class MinimalTets(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test the Home page homepage."""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')

    def test_register(self):
        """Test the cart page."""
        result = self.client.get('/register')
        self.assertEqual(result.status, '200 OK')

    def test_login(self):
        """Test the cart page."""
        result = self.client.get('/login')
        self.assertEqual(result.status, '200 OK')

    def test_cart(self):
        """Test the cart page."""
        result = self.client.get('/cart')
        self.assertIn(result.status, '302')

    def test_add():
        """Test the cart page."""
        result = self.client.get('/add')
        self.assertIn(result.status, '302')


if __name__ == '__main__':
    unittest_main()
