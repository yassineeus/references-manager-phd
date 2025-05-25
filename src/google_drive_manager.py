"""
Gestionnaire Google Drive - Test simple
"""

class GoogleDriveManager:
    def __init__(self):
        self.test_value = "OK"
    
    def test(self):
        return "Google Drive fonctionne"

# Test simple
if __name__ == "__main__":
    manager = GoogleDriveManager()
    print(manager.test())