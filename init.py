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
        
        # 1. 仅负责读取和初步解析
        self.readglobal_csv()
        self.readcharact_csv()
        self.initglobalkey()
        self.initcharates()

    def readcharact_csv(self):
        charact_csv_div=self.csv_dir+'characters/'
        if not self.os.path.exists(charact_csv_div):
             self.os.makedirs(charact_csv_div)
        for root, dirs, files in self.os.walk(charact_csv_div):
            dirs.sort(key=lambda x: int(x) if x.isdigit() else 0)
            for file in files:
                current_file_data = []
                if file.endswith('.csv'):
                    file_path = self.os.path.join(root, file)
                    with open(file_path, mode='r', encoding='utf-8-sig') as f:
                        reader = self.csv.reader(f)
                        for row in reader:
                            if not row: continue
                            if row[0].strip().startswith(';'): continue
                            
                            # [安全修复] 使用 enumerate 防止重复值的索引错误
                            clean_row = []
                            for i, cell in enumerate(row):
                                if ';' in cell:
                                    cell = cell.split(';')[0]
                                clean_row.append(cell.strip())
                            
                            current_file_data.append(clean_row)
                    self.charaseting.append(current_file_data)
        return self.charaseting

    def readglobal_csv(self):
        global_csv_path=self.csv_dir+'global/'
        if not self.os.path.exists(global_csv_path):
             self.os.makedirs(global_csv_path)
             
        for root, dirs, files in self.os.walk(global_csv_path):
            globalnumtmp=0
            for file in files:
                current_file_data = []
                if file.endswith('.csv'):
                    gloablkey=file.split('.')[0]
                    file_path = self.os.path.join(root, file)
                    with open(file_path, mode='r', encoding='utf-8-sig') as f:
                        reader = self.csv.reader(f)
                        for row in reader:
                            if not row: continue
                            if row[0].strip().startswith(';'): continue
                            
                            clean_row = []
                            for i, cell in enumerate(row):
                                if ';' in cell:
                                    cell = cell.split(';')[0]
                                clean_row.append(cell.strip())
                            
                            if not any(clean_row): continue
                            current_file_data.append(clean_row)
                            
                    self.global_settings.append(current_file_data)
                    self.global_settings[globalnumtmp].insert(0,['gloabkey',gloablkey])
                    globalnumtmp+=1

    def initglobalkey(self):
        for glb in self.global_settings:
            global_key_tmp={}
            if glb and len(glb) > 0 and len(glb[0]) > 1:
                global_key_name = glb[0][1]
                self.globalid.append(global_key_name)
                
                for row in glb:
                    if len(row) > 0 :
                        key = row[0]
                        if key == 'gloabkey' or not key:
                            continue
                        
                        # [通用逻辑] 不再对 Item 做特殊处理
                        # 只负责把 CSV 行转为 String(单列) 或 List(多列)
                        values = row[1:]
                        
                        # 清理末尾空值
                        while values and (values[-1] is None or values[-1] == ""):
                            values.pop()
                        
                        if len(values) == 1:
                            global_key_tmp[key] = values[0]
                        elif len(values) > 1:
                            global_key_tmp[key] = values
                        else:
                            global_key_tmp[key] = ""

            self.global_key[global_key_name]=global_key_tmp
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
        print(f"Loaded Characters IDs: {self.chara_ids}")