
try:
    import flask
    import flask_socketio
    import eventlet
    import ui_components
    import api_server
    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")
