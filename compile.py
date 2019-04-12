import sys
import os
import json

operating_system = os.name

compiler = "clang++"
program_name = "program.exe"
src_file_extensions = [ "cpp" ]
inc_file_extensions = [ "hpp", "h" ]
object_directory = "obj"

source_directories  = [ "src" ]
include_directories = [ "src/include" ]
library_directories = [ ]
additional_sources  = [ ]
additional_objects  = [ ]

libraries = [ ]
defines   = [ "ENG_DEBUG" ]
flags     = [ "-Wall" ]


def endswith_lst(input_str, ends):
    """ 'endswith' but compares with list of arguments """
    for end in ends:
        if input_str.endswith(end):
            return True
    return False


def sys_call(command, *args):
    """ System call helper function """
    call = command + ' ' + ' '.join(args)
    os.system(call)

def comm_print(args):
    """ Simple command for displaying information """
    for arg in args:
        if arg == "--os":
            print(operating_system)

def comm_compile(args):
    """ Command for compiling the program. """

    def load_modification_info():
        """ Loads info about src file modification times """
        try:
            with open("modinfo.json", 'r') as file:
                data = json.load(file)
                return data
        except Exception:
            print("Created 'modinfo.json'")
            with open("modinfo.json", 'w') as file:
                json.dump({"src":{},"inc":{}}, file, sort_keys = True, indent = 4)
                return {"src":{},"inc":{}}

    def parse_file_for_includes(path):
        """ Goes through file and returns local ' "" ' includes """
        includes = [ ]
        with open(path) as file:
            for line in file:
                if line.startswith("#") and "include" in line and '"' in line:
                    includes.append(line[line.find('"') + 1:line.rfind('"')])
        return includes

    def check_from_end_inclusion(partial, full):
        """ Checks if an element (string) from 'partial'
         is at the end of any element from 'full' """
        for part in partial:
            for i in full:
                if i.endswith(part):
                    return True
        return False

    # Load modinfo
    mod_info = {"src":{},"inc":{}}
    if not "-a" in args:
        mod_info = load_modification_info()

    # Get all source files
    src_files = [ ]
    for src_dir in source_directories:
        for item in os.listdir(src_dir):
            full_path = os.path.join(src_dir, item)
            if endswith_lst(str(item), src_file_extensions):
                src_files.append(str(full_path))
    src_files.extend(additional_sources)

    # Get all modified and unmodified include files
    modified_includes   = [ ]
    unmodified_includes = [ ]
    for inc_dir in include_directories:
        for item in os.listdir(inc_dir):
            full_path = str(os.path.join(inc_dir, item))
            if endswith_lst(str(item), inc_file_extensions):
                mod_time = os.path.getmtime(full_path)
                if (full_path not in mod_info["inc"]
                or mod_info["inc"][full_path]["mt"] != mod_time):
                    mod_info["inc"][full_path] = { }
                    mod_info["inc"][full_path]["mt"]  = mod_time
                    mod_info["inc"][full_path]["ifl"] = parse_file_for_includes(full_path)
                    modified_includes.append(full_path)
                else:
                    unmodified_includes.append(full_path)

    # Search for recurrent inclusion within include files themself
    to_search_modified = modified_includes.copy()
    new_to_search_modified = [ ]
    while to_search_modified != [ ]:
        for i in range(len(unmodified_includes)):
            key = unmodified_includes[i]
            if check_from_end_inclusion(mod_info["inc"][key]["ifl"], to_search_modified):
                modified_includes.append(key)
                new_to_search_modified.append(key)
        for i in new_to_search_modified:
            unmodified_includes.remove(i)
        to_search_modified = new_to_search_modified.copy()
        new_to_search_modified = [ ]

    # Check if obj directory exists
    if not os.path.exists(object_directory):
        print("Object path wasn't found. Creating one.")
        os.makedirs(object_directory)

    # Create some parts of compile commands
    include_directories_command = [ ]
    library_directories_command = [ ]
    defines_command = [ ]
    library_command = [ ]
    for i in include_directories:
        include_directories_command.append("-I" + i)
    for i in library_directories:
        library_directories_command.append("-L" + i)
    for i in defines:
        defines_command.append("-D" + i)
    for i in libraries:
        library_command.append("-l" + i)

    # Compile modified source files
    for src_file in src_files:
        mod_time = os.path.getmtime(src_file)
        if (src_file not in mod_info["src"]
        or mod_info["src"][src_file]["mt"] != mod_time
        or check_from_end_inclusion(mod_info["src"][src_file]["ifl"], modified_includes)):
            sys_call (
                compiler,
                "-o", object_directory + '/' + src_file.replace('/', '_') + ".o",
                "-c", src_file,
                ' '.join(flags),
                ' '.join(include_directories_command),
                ' '.join(defines_command)
            )
            print(src_file, "compiled")
            mod_info["src"][src_file] = { }
            mod_info["src"][src_file]["mt"]  = mod_time
            mod_info["src"][src_file]["ifl"] = parse_file_for_includes(src_file)

    # Save mod_info
    with open("modinfo.json", 'w') as file:
        json.dump(mod_info, file, sort_keys = True, indent = 4)

    # Create executable binary
    sys_call (
        compiler,
        "-o", program_name,
        object_directory + "/*.o",
        ' '.join(additional_objects),
        ' '.join(library_directories_command),
        ' '.join(library_command)
    )

def comm_run(args):
    """ Command for running compiled programs """
    return_value = -666
    if operating_system == "posix":
        return sys_call("./" + program_name, ' '.join(args))
    else:
        print("Current platform needs to be configured!")
        return sys_call(program_name, ' '.join(args))

def caller(args):
    """ Calls command functions """
    command = args[0]
    if command == "p" or command == "print":
        comm_print(args[1:])
    elif command == "c" or command == "compile":
        comm_compile(args[1:])
    elif command == "r" or command == "run":
        comm_run(args[1:])

input_arguments = sys.argv[1:]

caller(input_arguments)
