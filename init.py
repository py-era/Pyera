class initall:
    import csv
    import os
    import time
    def __init__(self,csv_dir):
        self.csv_dir = csv_dir
        self.charaseting = []
        self.chara_ids = []
        self.charaters_key={}
        self.keywords = ["基础", "素质", "能力", "CFLAG", "相性", "CSTR"]
        self.global_settings=[]
        self.globalid=[]
        self.global_key={}
        self.readglobal_csv()
        self.readcharact_csv()
        self.initglobalkey()
        self.initcharates()

    def readcharact_csv(self):
        charact_csv_div=self.csv_dir+'characters/'
        for root, dirs, files in self.os.walk(charact_csv_div):
            dirs.sort(key=lambda x: int(x))
            for file in files:
                current_file_data = []
                if file.endswith('.csv'):
                    file_path = self.os.path.join(root, file)
                    with open(file_path, mode='r', encoding='utf-8-sig') as f:
                        reader = self.csv.reader(f)
                        for row in reader:
                            if not row:
                                continue
                            if ';' in row[0]:
                                continue
                            else:
                                split_row=[]
                                for i in row:
                                    if ';' in i:
                                        split_row=i.split(';')[0]
                                        row[row.index(i)]=split_row
                            current_file_data.append(row)
                    self.charaseting.append(current_file_data)
        return self.charaseting

    def readglobal_csv(self):
        global_csv_path=self.csv_dir+'global/'
        for root, dirs, files in self.os.walk(global_csv_path):
            globalnumtmp=0
            for file in files:
                 #全局文件计数器,,,用在后面的
                current_file_data = []
                if file.endswith('.csv'):
                    gloablkey=file.split('.')[0]
                    file_path = self.os.path.join(root, file)
                    with open(file_path, mode='r', encoding='utf-8-sig') as f:
                        reader = self.csv.reader(f)
                        for row in reader:
                            if not row:
                                continue
                            if ';' in row[0]:
                                continue
                            else:
                                split_row=[]
                                for i in row:
                                    if ';' in i:
                                        split_row=i.split(';')[0]
                                        row[row.index(i)]=split_row
                            current_file_data.append(row)
                    self.global_settings.append(current_file_data)
                    self.global_settings[globalnumtmp].insert(0,['gloabkey',gloablkey]) #在每个全局设置的开头插入一个标识符，用于区分不同的全局设置
                    globalnumtmp+=1

    def initglobalkey(self):
        for glb in self.global_settings:
            global_key_tmp={}
            if glb and len(glb) > 0 and len(glb[0]) > 1:
                global_key= glb[0][1]
                self.globalid.append(global_key)
                for row in glb:
                    if len(row) > 0 :
                        key=row[0]
                        if key=='gloabkey':
                            continue
                        
                        # Item 的特殊逻辑保持不变
                        if glb[0][1]=='Item':
                            item_key_id=['name','price','idn','ex']
                            global_key_tmp[key]={}
                            # 防止 row 长度不足导致索引越界，加个简单的切片保护或者逻辑判断
                            process_len = min(len(row), len(item_key_id) + 2)
                            for i in range(2, process_len):
                                global_key_tmp[key][item_key_id[i-2]]=row[i-1]
                        
                        # 修改后的通用逻辑
                        else:
                            # 1. 先获取所有值
                            values = row[1:]
                            
                            # 2. 循环检查：只要列表不为空，且最后一个元素是空的，就把它扔掉
                            # .strip() == "" 用于判定是否为空或全是空格
                            while len(values) > 0 and (values[-1] is None or values[-1].strip() == ""):
                                values.pop() # 移除最后一个
                            
                            # 3. 根据清理后的长度决定存储类型
                            if len(values) > 1:
                                # 列表 (例如: ['A', '', 'C'] -> 中间的空位被保留了)
                                value = values
                            elif len(values) == 1:
                                # 单个字符串
                                value = values[0]
                            else:
                                # 空
                                value = ""
                                
                            global_key_tmp[key] = value

            self.global_key[global_key]=global_key_tmp
        self.global_settings.clear()

    def initcharates(self):
        for chara in self.charaseting:
            charaters_key_tmp={}
            if chara and len(chara) > 0 and len(chara[0]) > 1:
                chara_id = chara[0][1]
                self.chara_ids.append(chara_id)
                for category in self.keywords:
                    charaters_key_tmp[category] = {}
                for row in chara:
                    if len(row) > 0:
                        key = row[0]
                        if key in self.keywords:
                            sub_key = row[1]
                            value = row[2] if len(row) > 2 else ""
                            charaters_key_tmp[key][sub_key] = value
                        else:
                            value = row[1] if len(row) > 1 else ""
                            charaters_key_tmp[key] = value
            self.charaters_key[chara_id] = charaters_key_tmp
        self.charaseting.clear()
a=initall("./csv/")
""" 
这是一个制作过程中用来搬运的东西）
import re
import os
for root, dirs, files in os.walk("./characters/csvfile/"):
    for file in files:
         match = re.search(r'(1[0-5][0-9]|16[0-1]|[1-9][0-9]?)', file)
         if match:
            folder_num = match.group(1)
            target_folder = f"./characters/{folder_num}/"
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            src_path = os.path.join(root, file)
            dst_path = os.path.join(target_folder, file)
            os.rename(src_path, dst_path) 
"""