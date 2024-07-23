from django.http import HttpResponse
from pathlib import Path

def dwim(request, path):
    # Get the project root directory (parent of kappa folder)
    project_root = Path(__file__).resolve().parent.parent
    
    # Construct the full path
    full_path = project_root / path
    
    # Get the parent directory and the file name (without extension)
    parent_dir = full_path.parent
    file_name_without_ext = full_path.stem
    
    # Find all files in the parent directory that start with the given name
    matching_files = list(parent_dir.glob(f"{file_name_without_ext}.*"))
    
    if matching_files:
        file_list = "\n".join([f.name for f in matching_files])
        return HttpResponse(f"Files matching {file_name_without_ext}.* in {parent_dir}:\n{file_list}")
    else:
        return HttpResponse(f"No files found matching {file_name_without_ext}.* in {parent_dir}")
