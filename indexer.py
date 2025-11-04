import os.path
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.analysis import StemmingAnalyzer # 预处理选项之一
import re
import time

# 1.定义索引存储路径
INDEX_DIR = "index_data"

DATA_ROOT_DIR = "TDT3_Data"

# 2.定义索引的Schema
# docID: 存储且不可分词，用于唯一标识文档
# title: 存储且可分词（用于摘要和显示）
# content: 可分词（用于搜索），但不需要存储（节省空间，但摘要可能麻烦，
#          不过Whoosh有内置的摘要功能）
# **注意**：如果需要自定义预处理（如忽略大小写），需要调整TEXT字段的Analyzer。
#          默认TEXT字段会做词干提取、小写转换和停用词移除。
my_schema = Schema(
    docID=ID(stored=True, unique=True), # 存储DocID,且必须唯一
    doc_path=ID(stored=True),#存储文件路径，方便读取原始文件获取摘要
    content=TEXT(stored=False, analyzer=StemmingAnalyzer()) # 主要文本内容，不存储以节省空间
)
# content 使用 TEXT 类型，这意味着里面的文本会被 Whoosh 默认处理（分词、小写、停用词过滤等）
# 并且我们明确指定使用 StemmingAnalyzer 进行词干提取。

def create_or_open_index():
  """检查索引是否存在，如果不存在则创建新的索引，否则打开已有索引。"""
  if not os.path.exists(INDEX_DIR):
      os.mkdir(INDEX_DIR)
      print("Created index directory:", INDEX_DIR)
  
  if not exists_in(INDEX_DIR):
      # 创建新的索引
      print("索引不存在，开始创建新的索引")
      return create_in(INDEX_DIR, my_schema)
  else:
      # 打开已有索引
      print("索引已存在，开始打开索引")
      return open_dir(INDEX_DIR)

def extract_doc_info(file_path):
    """
    从TDT3文件内容中提取DOCNO作为docID，并提取TEXT内容作为content。
    我们使用正则表达式来处理这种结构化的文本。
    """
    try:
        # 使用'ignore'跳过无法解码的字符，确保程序不会崩溃
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 匹配 <DOCNO> 和 </DOCNO> 之间的内容，并去除首尾空格
        docno_match = re.search(r'<DOCNO>\s*(.*?)\s*</DOCNO>', content, re.DOTALL)
        # 匹配 <TEXT> 和 </TEXT> 之间的内容，re.DOTALL让.匹配换行符
        text_match = re.search(r'<TEXT>\s*(.*?)\s*</TEXT>', content, re.DOTALL)
        
        docID = docno_match.group(1).strip() if docno_match else None
        text_content = text_match.group(1).strip() if text_match else None
        
        if docID and text_content:
            return {'docID': docID, 'content': text_content}
        
    except Exception as e:
        print(f"读取或解析文件失败 {file_path}: {e}")
        
    return None
  
def index_documents(ix):
    """
    遍历数据目录，读取文件，并将其添加到Whoosh索引中。
    :param ix: Whoosh Index 对象
    """
    if not os.path.exists(DATA_ROOT_DIR):
        print(f"错误：找不到数据目录 '{DATA_ROOT_DIR}'。请确保该目录位于脚本旁边。")
        return
    writer = ix.writer()
    indexed_count = 0
    start_time = time.time()
    print(f"开始遍历 '{DATA_ROOT_DIR}' 目录并添加文档...")
    # os.walk 会遍历目录下的所有子目录和文件
    for root, _, files in os.walk(DATA_ROOT_DIR):
        for filename in files:
            # 仅处理.txt文件
            if filename.endswith('.txt'):
                file_path = os.path.join(root, filename)
                
                # 提取文档信息
                doc_info = extract_doc_info(file_path)
                
                if doc_info:
                    # 获取相对于 DATA_ROOT_DIR 的文件路径作为 doc_path
                    relative_path = os.path.relpath(file_path, DATA_ROOT_DIR)
                    
                    writer.add_document(
                        docID=doc_info['docID'],
                        doc_path=relative_path, # 存储相对路径
                        content=doc_info['content']
                    )
                    indexed_count += 1
                    
                    # 每索引1000篇文档，打印一次进度
                    if indexed_count % 1000 == 0:
                        print(f"已索引 {indexed_count} 篇文档...")

    # 提交所有更改到索引
    writer.commit()
    end_time = time.time()
    
    print("-" * 30)
    print(f"索引构建完成！")
    print(f"总计索引文档数: {indexed_count} 篇")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print("-" * 30)

if __name__ == '__main__':
    # 1. 创建或打开索引
    my_index = create_or_open_index()
    
    # 2. 索引文档（仅在索引为空时执行）
    if my_index.doc_count() == 0:
        index_documents(my_index)
    else:
        print(f"索引中已包含 {my_index.doc_count()} 篇文档，跳过索引步骤。")