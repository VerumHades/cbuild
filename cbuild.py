#!/usr/bin/python3

import os
import platform
import argparse
import shutil
import time
import subprocess
import sys
import json

from pathlib import Path
from lib.autopath import add_to_path
from lib.cmakebuilder import generate


parser = argparse.ArgumentParser()

parser.add_argument('-r', '--remake', action='store_true')
parser.add_argument(
    '-w', '--with-debuger',
    action='store_true',
    help="Runs gdb"
)
parser.add_argument(
    '-c', '--clear-build',
    action='store_true',
    help="Clears the build directory"
)

parser.add_argument(
    '-b', '--build-type',
    default="Release",
    help="Allows you to specify the build type.",
    choices=["Release", "Debug", "RelWithDebInfo", "MinSizeRel"]
)

parser.add_argument(
    '-a', '--autorun',
    help="Automatically runs the built executable"
)
parser.add_argument(
    '-p', '--package',
    action='store_true',
    help="Builds and creates an installer in the build directory"
)

parser.add_argument(
    '-m', '--build-makefile',
    action='store_true',
    help="Opens the CMakeLists.txt builder."
)
parser.add_argument(
    '--add-to-path',
    action='store_true',
    help="Adds scripts location to PATH."
)
parser.add_argument(
    '--run-args',
    nargs=argparse.REMAINDER,
    default=[],
    help="Arguments passed to the executable when autorunning."
)

script_directory = os.path.dirname(os.path.abspath(__file__))
root_directory = os.getcwd()

args = parser.parse_args()


# Load default executable when no arguments are supplied.
if len(sys.argv) == 1:
    config_path = os.path.join(root_directory, "cbuild.json")

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            loaded = json.load(f)

        if "executable" in loaded:
            args.build_type = "Release"
            args.autorun = loaded["executable"]


if args.add_to_path:
    add_to_path(script_directory)
    sys.exit(0)


if args.build_makefile:
    generate(root_directory)
    sys.exit(0)


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


def command(cmd):
    print(f"Running command: {cmd}")
    return os.system(cmd)


def os_command(linux, windows, prefix=""):
    if platform_is_windows:
        return command(prefix + windows)
    else:
        return command(prefix + linux)


suffixus = (
    '-DCMAKE_CXX_FLAGS="-DWINDOWS_PACKAGED_BUILD"'
    if args.package else ""
)


if not os.path.exists(os.path.join(root_directory, build_directory, "CMakeFiles")):
    print(os.path.join(build_directory, "CMakeFiles"))
    args.remake = True


if args.remake:
    print("Remaking...")

    os_command(
        f'cmake "{root_directory}" '
        f'-DCMAKE_BUILD_TYPE={build_type} '
        f'-DCMAKE_EXPORT_COMPILE_COMMANDS=ON {suffixus}',

        f'cmake "{root_directory}" '
        f'-DCMAKE_COLOR_MAKEFILE=ON '
        f'-G "Unix Makefiles" '
        f'-DCMAKE_BUILD_TYPE={build_type} '
        f'-DCMAKE_EXPORT_COMPILE_COMMANDS=ON {suffixus}'
    )


os.chdir(root_directory)

start_time = time.time()

build_exit_code = command(
    f'cmake --build "{build_directory}" -j 8'
)

if build_exit_code != 0:
    print("Build failed.")
    sys.exit(build_exit_code)


end_time = time.time()
elapsed_time = end_time - start_time

print(f"Time to build: {elapsed_time} seconds")


# Package the application.
if args.package:
    start_time = time.time()

    os.chdir(build_directory)

    file_path = "CPackConfig.cmake"

    with open(file_path, "r") as file:
        lines = file.readlines()

    with open(file_path, "w") as file:
        for line in lines:
            if line.startswith("set(CPACK_COMPONENTS_ALL"):
                line = line.replace("-", "_")

            file.write(line)

    package_exit_code = subprocess.call(
        ["cpack", "--config", file_path]
    )

    if package_exit_code != 0:
        print("Packaging failed.")
        sys.exit(package_exit_code)

    os.chdir(root_directory)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Time to package: {elapsed_time} seconds")


# Run the executable.
if args.autorun is not None:
    config_path = os.path.join(root_directory, "cbuild.json")

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"executable": args.autorun}, f, indent=4)

    executable = args.autorun

    if platform_is_windows:
        if not executable.lower().endswith(".exe"):
            executable += ".exe"

    executable_path = os.path.join(
        root_directory,
        build_directory,
        executable
    )

    if not os.path.isfile(executable_path):
        print(f"Executable not found: {executable_path}")
        sys.exit(1)

    run_command = [executable_path] + args.run_args

    if args.with_debuger:
        run_command = ["gdb", "-ex", "run", "--args"] + run_command

    print(f"Running executable: {run_command}")

    try:
        result = subprocess.run(
            run_command,
            cwd=root_directory
        )
        sys.exit(result.returncode)

    except FileNotFoundError as e:
        print(f"Failed to run executable: {e}")
        sys.exit(1)
