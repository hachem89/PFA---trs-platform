import os
import sys

# Add the root directory to sys.path so we can import 'shared.models' in Phase 2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Running on port 5001 so it doesn't conflict with ingestion-service on 5000
    app.run(debug=True, host='0.0.0.0', port=5001)
