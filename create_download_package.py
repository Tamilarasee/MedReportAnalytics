#!/usr/bin/env python
"""
Script to generate a ZIP file containing the Medical Report Analyzer project.
Run this script to create a ZIP file that can be downloaded.
"""

import os
import zipfile
import datetime
import time

# Only include these essential directories and files
INCLUDE_PATHS = [
    'app.py',
    'main.py',
    'run.py',
    'README.md',
    'package_list.txt',
    '.env.example',
    'routes/',
    'templates/',
    'static/',
    'utils/',
]

def should_include(path):
    """Check if a path should be included in the ZIP file."""
    # Skip the script itself
    if path == './create_download_package.py' or path.endswith('.zip'):
        return False
        
    # Include only selected paths
    for include_path in INCLUDE_PATHS:
        if path == './' + include_path or path.startswith('./' + include_path + '/'):
            # But skip any __pycache__ directories
            if '__pycache__' in path:
                return False
            return True
    
    return False

def create_zip_file():
    """Create a ZIP file of the project."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    zip_filename = f'medical_report_analyzer_{timestamp}.zip'
    
    print(f"Creating ZIP file: {zip_filename}")
    
    # Use current time for all files (to avoid timestamp issues)
    zinfo_time = time.localtime(time.time())[:6]
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all directories and files
        for root, dirs, files in os.walk('.'):
            # Filter directories
            dirs[:] = [d for d in dirs if should_include(os.path.join(root, d))]
            
            # Add files to ZIP
            for file in files:
                filepath = os.path.join(root, file)
                if should_include(filepath):
                    arcname = filepath[2:]  # Remove './' from the beginning
                    print(f"Adding {arcname}")
                    
                    # Create ZipInfo object with current time
                    zinfo = zipfile.ZipInfo(arcname, zinfo_time)
                    zinfo.compress_type = zipfile.ZIP_DEFLATED
                    
                    # Read file content and add to ZIP
                    with open(filepath, 'rb') as f:
                        zipf.writestr(zinfo, f.read())
    
    print(f"\nZIP file created successfully: {zip_filename}")
    print(f"Size: {os.path.getsize(zip_filename) / (1024 * 1024):.2f} MB")

if __name__ == '__main__':
    create_zip_file()