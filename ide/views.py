import subprocess
from django.shortcuts import render
from django.http import HttpResponse
from vt_site.models import Terms_pages, site_detail
import requests
from django.http import JsonResponse


PISTON_API_URL = "http://127.0.0.1:2000/api/v2/execute"

LANGUAGE_VERSIONS = {
    "python": "3.12.0",
    "c": "10.2.0",
    "cpp": "10.2.0",
    "java": "15.0.2",
    "javascript": "20.11.1",
    "go": "1.16.2",
    "swift": "5.3.3"
}

def get_extension(language):
    return {
        "python": "py",
        "c": "c",
        "cpp": "cpp",
        "java": "java",
        "javascript": "js",
        "go": "go",
        "swift": "swift"
    }.get(language, "txt")


def get_base_code(language):
    base_code = {
        "python": 'print("Hello, World!")',
        "c": '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!");\n    return 0;\n}',
        "cpp": '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!";\n    return 0;\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
        "javascript": 'console.log("Hello, World!");',
        "go": 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}',
        "swift": 'import Foundation\n\nprint("Hello, World!")',
    }
    return base_code.get(language, "// Base code not available for this language")

    
def editor_view(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    
    output = ''
    code = ''
    input_data = ''
    language = 'python'
    version = LANGUAGE_VERSIONS.get(language)

    if request.method == 'POST':    
        try:
            code = request.POST.get('code', '')
            input_data = request.POST.get('input_data', '')
            language = request.POST.get('language', 'python')
            version = LANGUAGE_VERSIONS.get(language)
            
            if not code:
                code = get_base_code(language)
                
            response = requests.post(PISTON_API_URL, json={
                "language": language,
                "version": version,
                "files": [{"name": f"main.{get_extension(language)}", "content": code}],
                "stdin": input_data
            }, timeout=10)

            if response.ok:
                result = response.json()
                run_output = result.get('run', {})
                output = (run_output.get('stdout') or '') + (run_output.get('stderr') or '')
            else:
                output = f"Error: Unable to compile. Status code {response.status_code}"
        except Exception as e:
            output = f"Error: {str(e)}"
        
        return JsonResponse({'output': output})

    base_code = get_base_code(language)
    context = {
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
        'output': output,
        'code': code,
        'input_data': input_data,
        'language': language,
        'version': version,
        'base_code': base_code
    }

    return render(request, 'ide/editor.html', context)
