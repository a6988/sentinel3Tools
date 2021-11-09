import os

# load
with open("./tmp/tmp.txt", "r") as file:
    data = file.read().split(" ")

# pick up only folder
folder, i = [], 0
while i < len(data):
    if data[i] == "PRE":
        i += 1
        folder.append(data[i])
    i += 1

# write
# number
with open("./tmp/number.sh", "w") as file:
    file.write(f'Nfolder="{len(folder)}"\n')
# filename
for i in range(0,len(folder)):
    with open(f"./tmp/tmp{i+1}.sh", "w") as file:
        file.write(f'folder="{folder[i]}"\n')