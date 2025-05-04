import questionary
import json, os, shutil

from os.path import join

script_directory = join(os.path.dirname(os.path.abspath(__file__)),"..")  # Directory where the script is located

library_templates = json.loads(open(join(script_directory,"lib_templates.json")).read());
library_template_path = join(script_directory,"lib_templates")

def setup_library(name, path = os.getcwd()):
    if not name in library_templates:
        print(f"Library setup not found: {name}")
        return

    lib_path = join(library_template_path, name)
    if not os.path.exists(lib_path):
        print(f"Library setup not found: {name}")
        return

    template = library_templates[name]

    make_string = ""
    link_name = ""
    if "link" in template:
        link_name = template["link"]

    make_config_path = join(lib_path, "make.txt")
    if os.path.exists(make_config_path):
        make_string = open(make_config_path).read()

    src_path = join(lib_path,"src")
    if os.path.exists(src_path):
        shutil.copytree(src_path, join(path, "external", "src"), dirs_exist_ok=True)

    include_path = join(lib_path,"include")
    if os.path.exists(include_path):
        shutil.copytree(include_path, join(path, "external", "include"), dirs_exist_ok=True)
    
    main_templates = join(lib_path,"main_templates")
    if(os.path.exists(main_templates)):
        selection = ["None"]
        
        for entry in os.listdir(main_templates):
            full_path = os.path.join(main_templates, entry)
            if os.path.isfile(full_path):
                selection.append(entry)

        selected = questionary.select(
            "This library provides templates for main.cpp (Choose None to not apply any template): ",
            choices=selection,
            default="None"
        ).ask()
        
        if(selected != "None"):
            shutil.copy2(join(main_templates, selected), join(path, "src" ,"main.cpp"))

    print(f"Setup library: {name}")
    return (make_string, link_name)

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

def generate(path = os.getcwd()):
    project_name = questionary.text("Enter your Project Name:").ask()
    executable_name = questionary.text("Enter your Executable Name (default 'main'): ", default="main").ask()
    version_major = questionary.text("Enter Major Version (default 1):", default="1").ask()
    version_minor = questionary.text("Enter Minor Version (default 0):", default="0").ask()
    options = []

    for key, template in library_templates.items():
        options.append(key)

    selected = questionary.checkbox(
        "Select libraries to include: ",
        choices=options
    ).ask()

    os.makedirs(join(path, "src"), exist_ok=True)
    os.makedirs(join(path, "include"), exist_ok=True)
    os.makedirs(join(path, "external/src"), exist_ok=True)
    os.makedirs(join(path, "external/include"), exist_ok=True)

    shutil.copytree(join(script_directory, "template", "src"), join(path, "src"), dirs_exist_ok=True)

    libraries = ""
    library_links = ""

    for name in selected:
        (make_string, link_name) = setup_library(name, path)
        libraries += f"# {'=' * 30} {name} {'=' * 30} \n\r" + make_string + f"# {'=' * 30}{'=' * 30} \n\r"
        library_links += " " +  link_name

    pairs = [
        ("project_name", project_name),
        ("version_major", version_major),
        ("version_minor", version_minor),
        ("executable_name", executable_name),
    ]
    for (key, value) in pairs:
        libraries = libraries.replace(key, value);

    cmake_template = open(join(script_directory,"cmake_template.txt")).read()
    cmake_filled = cmake_template.format(
        project_name=project_name,
        version_major=version_major,
        version_minor=version_minor,
        executable_name=executable_name,
        libraries=libraries,
        library_links=f"target_link_libraries({executable_name} PRIVATE {library_links})"
    )
    
    open(join(path,"cbuild.json"), "w").write(json.dumps({"executable": executable_name}))

    output_path = os.path.join(path, "CMakeLists.txt")
    with open(output_path, "w") as f:
        f.write(cmake_filled)
