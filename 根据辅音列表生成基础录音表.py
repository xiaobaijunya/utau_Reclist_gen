import re


# 读取辅音列表并生成录音表的函数
def generate_base_reclist(ini_file_path, output_file_path, line_length=8):
    consonants_data = {}
    all_phonemes = []

    # 读取ini文件
    with open(ini_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        # 提取[CONSONANT]部分
        consonant_section = re.search(r'\[CONSONANT\](.*?)\[', content, re.DOTALL)
        if consonant_section:
            consonants_text = consonant_section.group(1).strip()

            # 解析每一行辅音数据
            for line in consonants_text.split('\n'):
                if line.strip():
                    # 分割辅音和音素列表（使用=作为分隔符）
                    parts = line.split('=')
                    if len(parts) >= 3:
                        consonant = parts[0].strip()
                        # 提取==中间的音素列表
                        phonemes_str = '='.join(parts[1:-1]).strip()
                        # 以逗号分割音素
                        phonemes = [ph.strip() for ph in phonemes_str.split(',') if ph.strip()]

                        consonants_data[consonant] = phonemes
                        all_phonemes.extend(phonemes)

    # 生成录音表
    with open(output_file_path, 'w', encoding='utf-8') as file:
        current_line = []

        for phoneme in all_phonemes:
            current_line.append(phoneme)

            # 当达到设定的行长度时，写入一行并重置当前行
            if len(current_line) >= line_length:
                file.write('_' + '_'.join(current_line) + '\n')
                current_line = []

        # 写入最后一行（如果有剩余的音素）
        if current_line:
            file.write('_' + '_'.join(current_line) + '\n')

    print(f"录音表已生成到 {output_file_path}")
    print(f"总音素数量: {len(all_phonemes)}")


if __name__ == "__main__":
    # 配置文件路径和参数
    ini_file = 'risku优化版presamp.ini'
    output_file = 'base_reclist.txt'  # 生成的基础录音表文件名
    line_length = 4  # 每行的音素数量

    # 生成录音表
    generate_base_reclist(ini_file, output_file, line_length)

    # 可选：如果需要直接覆盖record.txt文件，可以取消下面这行的注释
    # generate_base_reclist(ini_file, 'record.txt', line_length)
