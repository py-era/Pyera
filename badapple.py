# preprocess_bad_apple.py
import cv2
import json
import sys
from PIL import Image

# ========== 核心配置 ==========
VIDEO_PATH = "bad_apple.mp4"       # 你的视频文件路径
OUTPUT_FILE = "bad_apple_frames.py" # 输出的数据文件
FRAME_WIDTH = 100                   # 调整为适合Pera窗口的宽度 (建议 80-120)
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", " "]
# ==============================

def resize_image(image_frame, new_width=FRAME_WIDTH):
    """调整图片尺寸，保持宽高比"""
    width, height = image_frame.size
    # 修正宽高比，使其在终端/窗口中显示正常
    aspect_ratio = height / float(width * 2.2)  # 2.2是经验值，可根据效果调整
    new_height = int(aspect_ratio * new_width)
    return image_frame.resize((new_width, new_height))

def greyscale(image_frame):
    """转为灰度图"""
    return image_frame.convert("L")

def pixels_to_ascii(image_frame):
    """将像素转换为ASCII字符"""
    pixels = image_frame.getdata()
    # 根据灰度值选择字符
    characters = "".join([ASCII_CHARS[pixel // 25] for pixel in pixels])
    return characters

def extract_frames_from_video(video_path, max_frames=None):
    """
    从视频提取所有帧并转换为ASCII字符串列表
    """
    print(f"开始处理视频: {video_path}")
    print(f"输出宽度: {FRAME_WIDTH} 字符")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("错误：无法打开视频文件！")
        return None
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps
    
    print(f"视频信息: {total_frames}帧, {fps:.2f}FPS, 时长{duration:.2f}秒")
    
    if max_frames:
        total_frames = min(total_frames, max_frames)
        print(f"(测试模式：仅处理前{max_frames}帧)")
    
    frames = []
    frame_count = 0
    
    while frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 将OpenCV的BGR格式转为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # 处理图像：调整大小 -> 灰度化 -> 转换ASCII
        resized = resize_image(pil_image, FRAME_WIDTH)
        grey = greyscale(resized)
        ascii_chars = pixels_to_ascii(grey)
        
        # 将一维字符数组格式化为多行字符串
        pixel_count = len(ascii_chars)
        ascii_image = "\n".join(
            [ascii_chars[i:(i + FRAME_WIDTH)] for i in range(0, pixel_count, FRAME_WIDTH)]
        )
        
        frames.append(ascii_image)
        frame_count += 1
        
        # 显示进度
        if frame_count % 100 == 0 or frame_count == total_frames:
            progress = frame_count / total_frames * 100
            bar_length = 40
            filled = int(bar_length * frame_count // total_frames)
            bar = '█' * filled + '░' * (bar_length - filled)
            sys.stdout.write(f'\r进度: |{bar}| {progress:.1f}% ({frame_count}/{total_frames})')
            sys.stdout.flush()
    
    cap.release()
    print(f"\n处理完成！共提取 {len(frames)} 帧ASCII数据。")
    return frames, fps

def save_frames_to_python(frames, output_file, fps=30.0):
    """将帧数据保存为Python文件"""
    print(f"正在保存数据到 {output_file}...")
    
    # 使用json.dumps确保字符串转义正确
    frames_json = json.dumps(frames, ensure_ascii=False)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""# bad_apple_frames.py
# 此文件由 preprocess_bad_apple.py 自动生成
# 视频帧率: {fps:.2f} FPS
# 帧总数: {len(frames)}
# ASCII宽度: {FRAME_WIDTH} 字符

FRAMES = {frames_json}

# 方便导入的元数据
FRAME_RATE = {fps}
ASCII_WIDTH = {FRAME_WIDTH}
TOTAL_FRAMES = {len(frames)}
""")
    
    print(f"保存成功！文件大小: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
    print(f"平均每帧大小: {os.path.getsize(output_file) / len(frames):.0f} 字节")

if __name__ == "__main__":
    import os
    
    # 检查视频文件是否存在
    if not os.path.exists(VIDEO_PATH):
        print(f"错误：视频文件 '{VIDEO_PATH}' 不存在！")
        print("请将视频文件放在脚本同目录下，或修改 VIDEO_PATH 变量。")
        sys.exit(1)
    
    # 可选：测试模式（只处理前100帧）
    TEST_MODE = False
    max_frames = 100 if TEST_MODE else None
    
    # 提取帧数据
    result = extract_frames_from_video(VIDEO_PATH, max_frames)
    if result:
        frames, fps = result
        # 保存数据
        save_frames_to_python(frames, OUTPUT_FILE, fps)
        
        print("\n" + "="*50)
        print("下一步：")
        print(f"1. 将生成的 '{OUTPUT_FILE}' 移动到框架的 events/ 目录下")
        print("2. 确保事件文件 event_bad_apple.py 中正确导入")
        print(f"3. 将音频文件 'bad_apple.mp3' 放入 ./music/ 目录")
        print("="*50)