from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
import importlib
import sys

@csrf_exempt
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
    
    if len(matching_files) == 1 and matching_files[0].suffix == '.py':
        # If there's exactly one matching file and it's a .py file
        module_path = str(matching_files[0].relative_to(project_root).with_suffix(''))
        module_name = module_path.replace('/', '.')
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Call the handle_request function
            if hasattr(module, 'handle_request'):
                return module.handle_request(request)
            else:
                return HttpResponse(f"The module {module_name} does not have a handle_request function.")
        except ImportError:
            return HttpResponse(f"Failed to import module {module_name}")
    elif matching_files:
        file_list = "\n".join([f.name for f in matching_files])
        return HttpResponse(f"Files matching {file_name_without_ext}.* in {parent_dir}:\n{file_list}")
    else:
        return HttpResponse(f"No files found matching {file_name_without_ext}.* in {parent_dir}")
