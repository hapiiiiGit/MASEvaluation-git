import os
import glob
import shutil

def restructure_log_files(dir_path: str):
    # 匹配所有 instruction* 子目录
    pattern = os.path.join(dir_path, "instruction*")
    instruction_dirs = glob.glob(pattern)

    if not instruction_dirs:
        print(f"未找到任何 instruction 文件夹，请检查路径: {dir_path}")
        return

    success_count = 0
    skip_count = 0

    for folder in sorted(instruction_dirs):
        if not os.path.isdir(folder):
            continue

        logs_dir = os.path.join(folder, "logs")
        target_file = os.path.join(folder, "log.txt")

        # 检查 logs 子文件夹是否存在
        if not os.path.isdir(logs_dir):
            print(f"[跳过] {folder} 下未找到 logs 文件夹")
            skip_count += 1
            continue

        # 找到 logs 文件夹下的 txt 文件
        txt_files = glob.glob(os.path.join(logs_dir, "*.txt"))

        if not txt_files:
            print(f"[跳过] {logs_dir} 下未找到任何 .txt 文件")
            skip_count += 1
            continue

        if len(txt_files) > 1:
            print(f"[警告] {logs_dir} 下有多个 .txt 文件，将使用第一个: {txt_files[0]}")

        src_file = txt_files[0]

        # 移动并重命名
        shutil.move(src_file, target_file)
        print(f"[已处理] {src_file} -> {target_file}")

        # 删除空的 logs 文件夹
        if not os.listdir(logs_dir):
            os.rmdir(logs_dir)
            print(f"[已删除空文件夹] {logs_dir}")
        else:
            print(f"[提示] {logs_dir} 非空，未删除")

        success_count += 1

    print(f"\n完成！共扫描 {len(instruction_dirs)} 个文件夹，成功处理 {success_count} 个，跳过 {skip_count} 个。")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python restructure.py <dir_path>")
        print("示例: python restructure.py /path/to/your/dir")
        sys.exit(1)

    dir_path = sys.argv[1]
    if not os.path.isdir(dir_path):
        print(f"错误：路径不存在或不是目录: {dir_path}")
        sys.exit(1)

    restructure_log_files(dir_path)