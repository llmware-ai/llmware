def qdrant_installed():
    try:
        import qdrant_client
        return True
    except ImportError:
        return False