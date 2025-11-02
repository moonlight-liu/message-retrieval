import os.path
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.analysis import StemmingAnalyzer # 预处理选项之一
