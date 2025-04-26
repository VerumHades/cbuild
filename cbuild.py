#! /usr/bin/python3

import os, platform, argparse, shutil, time, subprocess
from lib.autopath import add_to_path
from lib.cmakebuilder import generate

parser = argparse.ArgumentParser()

parser.add_argument('-r', '--remake', action='store_true')
parser.add_argument('-w', '--with-debuger', action='store_true', help="Runs gdb")
parser.add_argument('-c', '--clear-build', action='store_true', help="Clears the build directory")

parser.add_argument(
    '-b', '--build-type',
    default="Release",
    help="Allows you to specify the build type.",
    choices = ["Release","Debug","RelWithDebInfo","MinSizeRel"]
)

parser.add_argument('-a', '--autorun', help="Automatically runs the built executable")
parser.add_argument('-p', '--package', action='store_true', help="Builds and creates and installer in build directory")

parser.add_argument('-m', '--build-makefile', action='store_true', help="Opens the CMakeLists.txt builder.")
parser.add_argument('--add-to-path', action='store_true', help="Adds scripts location to path.")

script_directory = os.path.dirname(os.path.abspath(__file__))  # Directory where the script is located

args = parser.parse_args()
root_directory = os.getcwd()

if args.add_to_path:
    add_to_path(script_directory)
    exit()

if args.build_makefile:
    generate(root_directory)
    exit()


build_type = args.build_type
build_directory = os.path.join("build", build_type)

print(f"Selected build type: {build_type}")
print(f"Selected build directory: {build_directory}")

os.makedirs(build_directory, exist_ok=True)

if args.clear_build:
    shutil.rmtree(build_directory)
    os.makedirs(build_directory, exist_ok=True)

os.chdir(build_directory)
print("Verified build directory")

platform_is_windows = platform.system().lower() == "windows"

print(f"Platform is: {platform.system().lower()}")

def command(command):
    print(f"Running command: {command}")
    return os.system(command)

def os_command(linux,windows, prefix = ""):
    if platform_is_windows:
        return command(prefix + windows)
    else:
        return command(prefix + linux)


suffixus = "-DCMAKE_CXX_FLAGS=\"-DWINDOWS_PACKAGED_BUILD\"" if args.package else ""

if args.remake:
    print("Remaking...")
    os_command(
        f"cmake {root_directory} -DCMAKE_BUILD_TYPE={build_type} -DCMAKE_EXPORT_COMPILE_COMMANDS=ON {suffixus}",
        f"cmake {root_directory} -DCMAKE_COLOR_MAKEFILE=ON -G \"Unix Makefiles\" -DCMAKE_BUILD_TYPE={build_type} {suffixus}"
    )

os.chdir(root_directory)

prefix = "gdb -ex run " if args.with_debuger else ""
#prefix =  ""

start_time = time.time()

build_exit_code = command(f"cmake --build {build_directory} -j 8")
if build_exit_code != 0:
    print("Build failed.")
    exit()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Time to build: {elapsed_time} seconds")

if args.package:
    start_time = time.time()

    os.chdir(build_directory)

    file_path = 'CPackConfig.cmake'

    with open(file_path, 'r') as file:
            lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith("set(CPACK_COMPONENTS_ALL"):
                line = line.replace("-","_")
            file.write(line)

    os.system(f"cpack --config {file_path}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time to package: {elapsed_time} seconds")

if args.autorun is not None:
    os_command(
        f"./{build_directory}/{args.autorun}",
        f"{build_directory}\\{args.autorun}.exe",
        prefix = prefix
    )
