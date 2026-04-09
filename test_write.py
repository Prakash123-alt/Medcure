import os
path = "c:\\Users\\Yasin.Dhalait\\Documents\\GitHub\\medcure_GDGE\\is_writing_working.txt"
with open(path, "w") as f:
    f.write("Writing is working!")
print(f"File written to {path}")
