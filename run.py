#!/usr/bin/env python3
"""
Smart Filling Frontend - Flask Application Entry Point
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )