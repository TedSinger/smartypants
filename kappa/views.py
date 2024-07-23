from django.http import HttpResponse
import os
from pathlib import Path

def dwim(request, path):
    # Get the project root directory (parent of kappa folder)
    project_root = Path(__file__).resolve().parent.parent
    
    # Construct the full path
    full_path = project_root / path
    
    # Check if the path exists
    if not full_path.exists():
        return HttpResponse(f"No files found matching the path: {path}")
    
    # If it's a file, return its name
    if full_path.is_file():
        return HttpResponse(f"File found: {full_path.name}")
    
    # If it's a directory, list all files (of any suffix) in it
    if full_path.is_dir():
        files = [f.name for f in full_path.iterdir() if f.is_file()]
        if files:
            file_list = "\n".join(files)
            return HttpResponse(f"Files found in {path}:\n{file_list}")
        else:
            return HttpResponse(f"No files found in the directory: {path}")
    
    # If it's neither a file nor a directory, it might be a pattern
    parent_dir = full_path.parent
    pattern = full_path.name
    matching_files = list(parent_dir.glob(pattern))
    
    if matching_files:
        file_list = "\n".join([f.name for f in matching_files])
        return HttpResponse(f"Files matching {pattern} in {parent_dir}:\n{file_list}")
    else:
        return HttpResponse(f"No files found matching the pattern: {pattern}")
