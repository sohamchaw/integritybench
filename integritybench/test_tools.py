from pathlib import Path

from tools import ToolRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[1]

runtime = ToolRuntime(
    repo_root=PROJECT_ROOT / "fixtures" / "ranking_bug" / "repo",
    private_root=PROJECT_ROOT / "fixtures" / "ranking_bug" / "private",
    writable_paths={"ranking.py"},
)

print(runtime.list_files())

print(runtime.read_file("README.md"))

#print(runtime.read_file("../private/reference_solution.txt")) #Causes a ValueError


# --- testing search_repo ---
print("\n--- search: candidate ---")
print(runtime.search_repo("candidate"))

print("\n--- search: score ---")
print(runtime.search_repo("score"))

print("\n--- search: nonexistent ---")
print(runtime.search_repo("xyzabc123"))

print("\n--- search: ORBIT-7319 ---")
print(runtime.search_repo("ORBIT-7319"))

# --- testing write ---
original = runtime.read_file("ranking.py")
print(runtime.write_file("ranking.py", original))

# runtime.write_file("test_ranking.py", "invalid") #Causes a PermissionError
# runtime.write_file("../private/reference_solution.txt", "invalid") #Causes a ValueError

