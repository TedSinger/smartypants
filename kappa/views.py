from django.http import HttpResponse
from django.template import Context
from pathlib import Path
import importlib
import sys
from jinja2 import Environment, FileSystemLoader
import pugsql


def dwim(request, path):
    # Database connection
    db = pugsql.module()
    db.connect('sqlite:///tmp/foo.db')
    project_root = Path(__file__).resolve().parent.parent
    
    # Construct the full path
    full_path = project_root / path
    
    # Get the parent directory and the file name (without extension)
    parent_dir = full_path.parent
    file_name_without_ext = full_path.stem
    
    # Find all files in the parent directory that start with the given name
    matching_files = list(parent_dir.glob(f"{file_name_without_ext}.*"))
    
    if len(matching_files) == 1:
        matching_file = matching_files[0]
        if matching_file.suffix == '.py':
            # If there's exactly one matching file and it's a .py file
            module_path = str(matching_file.relative_to(project_root).with_suffix(''))
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
        elif matching_file.suffix == '.jinja':
            # If there's exactly one matching file and it's a .jinja file
            env = Environment(loader=FileSystemLoader(parent_dir))
            template = env.get_template(matching_file.name)
            
            # Create a context for the template
            context = {
                'request': request,
                # Add any other context variables you want to pass to the template
            }
            
            # Render the template
            rendered_content = template.render(context)
            return HttpResponse(rendered_content)
    # Check for .sql files in parent directories
    for parent in full_path.parents:
        sql_files = list(parent.glob("*.sql"))
        if sql_files:
            sql_file = sql_files[0]
            db.load_sql(sql_file)
            query_name = full_path.relative_to(parent).with_suffix('').as_posix().replace('/', '_')
            if query_name in db.queries:
                query_params = request.GET.dict()
                if request.body:
                    import json
                    try:
                        body_data = json.loads(request.body)
                        if isinstance(body_data, list) and all(isinstance(item, dict) for item in body_data):
                            result = db.queries[query_name](body_data)
                        else:
                            return HttpResponse("Request body must be a list of dictionaries.", status=400)
                    except json.JSONDecodeError:
                        return HttpResponse("Invalid JSON in request body.", status=400)
                else:
                    result = db.queries[query_name](**query_params)
                return HttpResponse(str(result))
            else:
                return HttpResponse(f"No query named {query_name} found in {sql_file}")
        file_list = "\n".join([f.name for f in matching_files])
        return HttpResponse(f"Files matching {file_name_without_ext}.* in {parent_dir}:\n{file_list}")
    else:
        return HttpResponse(f"No files found matching {file_name_without_ext}.* in {parent_dir}")
