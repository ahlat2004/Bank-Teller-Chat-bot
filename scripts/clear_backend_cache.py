"""Clear backend caches without touching DB or trained models.

Safe actions performed:
- Remove `__pycache__` directories under `backend/` (recursive), excluding any path that contains `models` or `data`.
- Remove `.pyc` files under `backend/` excluding paths that contain `models` or `data`.
- Attempt to call `session_manager.clear_all_sessions()` if the backend package imports correctly.

Run from project root: `python scripts\clear_backend_cache.py`
"""
import os
import sys
import shutil

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(project_root, 'backend')

if not os.path.isdir(backend_dir):
    print(f"Backend directory not found at: {backend_dir}")
    sys.exit(1)

removed_count = 0
removed_items = []

for dirpath, dirnames, filenames in os.walk(backend_dir):
    # Skip any path that includes 'models' or 'data' to avoid touching trained models or DB files
    parts = dirpath.split(os.sep)
    if 'models' in parts or 'data' in parts:
        continue

    # Remove __pycache__ directories
    if '__pycache__' in dirnames:
        cache_path = os.path.join(dirpath, '__pycache__')
        try:
            shutil.rmtree(cache_path)
            removed_count += 1
            removed_items.append(cache_path)
            print(f"Removed: {cache_path}")
        except Exception as e:
            print(f"Failed to remove {cache_path}: {e}")

    # Remove .pyc files
    for fname in filenames:
        if fname.endswith('.pyc'):
            fpath = os.path.join(dirpath, fname)
            try:
                os.remove(fpath)
                removed_count += 1
                removed_items.append(fpath)
                print(f"Removed: {fpath}")
            except Exception as e:
                print(f"Failed to remove {fpath}: {e}")

print('\nSummary:')
print(f'  Removed {removed_count} items (pyc/__pycache__) under backend/')

# Try to call session_manager.clear_all_sessions() if available
try:
    sys.path.insert(0, project_root)
    from backend.app.utils.session_manager import session_manager
    try:
        cleared = session_manager.clear_all_sessions()
        print(f"Called session_manager.clear_all_sessions(): cleared {cleared} sessions")
    except Exception as e:
        print(f"Imported session_manager but clear_all_sessions() failed: {e}")
except Exception as e:
    print(f"Could not import session_manager (backend not installed or missing deps): {e}")

print("Done. To ensure a fully fresh run, restart the backend with FORCE_FRESH_SESSIONS=1.")
