"""
Gestionnaire fichiers locaux - Test simple
"""

class LocalFilesManager:
    def __init__(self):
        self.test_value = "OK"
    
    def test(self):
        return "Local files fonctionne"

# Test simple
if __name__ == "__main__":
    manager = LocalFilesManager()
    print(manager.test())
    