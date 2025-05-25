"""
Gestionnaire GitHub - Test simple
"""

class GitHubManager:
    def __init__(self):
        self.test_value = "OK"
    
    def test(self):
        return "GitHub fonctionne"

# Test simple
if __name__ == "__main__":
    manager = GitHubManager()
    print(manager.test())