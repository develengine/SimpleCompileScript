import sys
import os
import json

operating_system = os.name

compiler = "clang++"
program_name = "program.exe"
src_file_extensions    = [ "cpp" ]
header_file_extensions = [ "hpp", "h" ]
object_directory = "obj"

source_directories  = [ "src" ]
include_directories = [ "src/include" ]
library_directories = [ ]
additional_objects  = [ ]

libraries = [ ]
defines   = [ ]
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

def comm_get(args):
    """ Simple command for displaying information """
    for arg in args:
        if arg == "--os":
            print(operating_system)

def comm_compile(args):
    """ Command for compiling programs. """

    def load_modification_info():
        """ Loads info about src file modification times """
        try:
            with open("modinfo.json", 'r') as file:
                data = json.load(file)
                return data
        except Exception:
            print("Created 'modinfo.json'")
            with open("modinfo.json", 'w') as file:
                json.dump({ }, file, sort_keys = True, indent = 4)
                return { }

    mod_info = load_modification_info()

    # Get all source files
    src_files = [ ]
    for src_dir in source_directories:
        for item in os.listdir(src_dir):
            full_path = os.path.join(src_dir, item)
            if endswith_lst(str(item), src_file_extensions):
                src_files.append(str(full_path))

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
    for i in defines:
        defines_command.append("-D" + i)
    for i in library_directories:
        library_directories_command.append("-L" + i)
    for i in libraries:
        library_command.append("-l" + i)

    # Compile modified source files
    for src_file in src_files:
        mod_time = os.path.getmtime(src_file)
        if src_file not in mod_info or mod_info[src_file]["mt"] != mod_time:
            sys_call (
                compiler,
                "-o", object_directory + '/' + src_file.replace('/', '_') + ".o",
                "-c", src_file,
                ' '.join(flags),
                ' '.join(include_directories_command),
                ' '.join(defines_command)
            )
            # TODO: Parse file for include files
            mod_info[src_file] = { }
            mod_info[src_file]["mt"]  = mod_time
            mod_info[src_file]["ifl"] = [ ]
        # TODO: 'elif' for included file changes 

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

def caller(args):
    """ Calls functions """
    command = args[0]
    if command == "g" or command == "get":
        comm_get(args[1:])
    elif command == "c" or command == "compile":
        comm_compile(args[1:])
    elif command == "r" or command == "run":
        print("Not implemented yet")

input_arguments = sys.argv[1:]

caller(input_arguments)
