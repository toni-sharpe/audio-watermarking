import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def test_index_page(self, client):
        """Test that the index page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Audio Watermarking Tool' in response.data
    
    def test_artists_page(self, client):
        """Test that the artists page loads"""
        response = client.get('/artists')
        assert response.status_code == 200
        assert b'Artists Database' in response.data
    
    def test_api_nodes_endpoint(self, client):
        """Test the /api/nodes endpoint"""
        response = client.get('/api/nodes')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        # Parse JSON response
        data = response.get_json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) == 19, f"Should have 19 nodes, got {len(data)}"
        
        # Check structure of first node
        if len(data) > 0:
            node = data[0]
            assert 'id' in node, "Node should have 'id' field"
            assert 'name' in node, "Node should have 'name' field"
            assert isinstance(node['id'], int), "ID should be an integer"
            assert isinstance(node['name'], str), "Name should be a string"
    
    def test_api_nodes_data_integrity(self, client):
        """Test that API returns valid data"""
        response = client.get('/api/nodes')
        data = response.get_json()
        
        # Check that all nodes have valid data
        for node in data:
            assert node['id'] > 0, "ID should be positive"
            assert len(node['name']) > 0, "Name should not be empty"
            assert len(node['name']) <= 240, "Name should not exceed 240 characters"
        
        # Check that IDs are sequential starting from 1
        ids = [node['id'] for node in data]
        assert ids == list(range(1, 20)), "IDs should be sequential from 1 to 19"
    
    def test_api_nodes_includes_diverse_names(self, client):
        """Test that API returns diverse names"""
        response = client.get('/api/nodes')
        data = response.get_json()
        
        names = [node['name'] for node in data]
        
        # Check for some expected names
        assert 'Amara Okafor' in names
        assert 'Chen Wei' in names
        assert 'Priya Sharma' in names
        assert 'Yuki Tanaka' in names
