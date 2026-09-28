import difflib
import os

def generate_colored_diff():
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_v1 = os.path.join(dir_path, "main-v1.py")
    file_main = os.path.join(dir_path, "main.py")

    if not os.path.exists(file_v1) or not os.path.exists(file_main):
        print("Error: Make sure both main-v1.py and main.py exist in the directory.")
        return

    with open(file_v1, "r", encoding="utf-8") as f1, open(file_main, "r", encoding="utf-8") as f2:
        lines_v1 = f1.readlines()
        lines_main = f2.readlines()

    diff = difflib.unified_diff(
        lines_v1, lines_main, 
        fromfile="main-v1.py", tofile="main.py"
    )

    # ANSI escape sequences for terminal coloring
    GREEN = "\033[32m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            print(GREEN + line.rstrip() + RESET)
        elif line.startswith("-") and not line.startswith("---"):
            print(RED + line.rstrip() + RESET)
        elif line.startswith("@@"):
            print(CYAN + line.rstrip() + RESET)
        else:
            print(line.rstrip())

if __name__ == "__main__":
    generate_colored_diff()