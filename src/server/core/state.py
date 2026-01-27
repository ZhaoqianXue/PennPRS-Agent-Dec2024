"""
Shared state management for the application.
"""

# Global Progress Store (InMemory)
# {request_id: {"status": "running"|"completed", "total": 0, "fetched": 0, "current_action": ""}}
search_progress = {}
