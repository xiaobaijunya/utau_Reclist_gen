

#录音表长度
length = 8
pitch = 60


words = []
with open("Reclist.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = line.split("_")
        line = [line for line in line if line != ""]
        words.append(line)
n = 0

# 给长度不足 length 的 words 行添加 R 补足为 length 个
for i in range(len(words)):
    while len(words[i]) < length:
        words[i].append('R')
    if len(words[i]) > length:
        print('录音表过长')

with open("record.ust", "w") as ust:
    ust.write("""[#VERSION]
UST Version1.2
[#SETTING]
Tempo=120
Tracks=1
VoiceDir=""")
    ust.write(f"\n[#{n}]\nLyric=R\nNoteNum={pitch}\nLength=1920")
    n+=1
    for i in range(len(words)):
        for j in range(length):
            ust.write(f"\n[#{n}]\nLyric={words[i][j]}\nNoteNum={pitch}\nLength=480")
            n+=1
        ust.write(f"\n[#{n}]\nLyric=R\nNoteNum={pitch}\nLength=1920")
        n+=1

