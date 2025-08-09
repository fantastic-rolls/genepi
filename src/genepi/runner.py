import os
import subprocess
from importlib.resources import files
from tempfile import NamedTemporaryFile

import genepi.data


def run_script(ae_script: str) -> None:
    return
    wrapper = f"""
tell application "Adobe After Effects 2025"
    activate
    DoScriptFile "{ae_script}"
end tell"""

    p = subprocess.Popen(
        "osascript",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf8",
        text=True,
    )
    print("Running script in After effects...")
    _ = p.communicate(wrapper)[0].split("\n")


def run_premiere_script(ae_script: str) -> None:
    wrapper = f"""
tell application "Adobe Premiere Pro 2025"
    activate
    ProcessFile "{ae_script}"
end tell"""

    p = subprocess.Popen(
        "osascript",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf8",
        text=True,
    )
    print("Running script in After effects...")
    _ = p.communicate(wrapper)[0].split("\n")


def _run_script(ae_script: str) -> None:
    p = subprocess.Popen(
        [
            "osascript",
            "-e",
            'tell application "Adobe After Effects 2025" to activate',
            "-e",
            f'tell application "Adobe After Effects 2025" to DoScriptFile "{ae_script}"',
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf8",
        text=True,
    )
    print(f"Running script in After effects {ae_script}...")
    stdout, stderr = p.communicate()


def generate_ae_script(config_file: str, script_dir: str | None = None) -> str:
    my_module_root = files(genepi.data)
    templates_root = my_module_root.joinpath("ae_scripts")
    if script_dir:
        script_file = os.path.join(script_dir, "genepi.js")
    else:
        script_file = NamedTemporaryFile(
            prefix="genpan-", suffix="-script-gen-panels.js", delete=False
        ).name
    with templates_root.joinpath("genepi.js").open("r") as src_fp:
        with open(script_file, "w", encoding="utf8") as fp:
            for line in src_fp.readlines():
                if "___TMPLT_CONFIG_FILE___" in line:
                    line = line.replace("___TMPLT_CONFIG_FILE___", config_file)
                fp.write(line)

    return script_file
