import os.path
import argparse
import re
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.highlight import SentenceFragmenter, Highlighter, ContextFragmenter
from custom_scorer import CustomTfIdf # 导入自定义评分器
import time

# --- 配置 ---
INDEX_DIR = "index_data"
DATA_ROOT_DIR = "TDT3_Data"
DEFAULT_HITS = 10  # 默认返回 Top 10

def read_document_content(doc_path):
    """
    从原始文件中读取文档内容
    :param doc_path: 文档的相对路径（从索引中获取）
    :return: 文档的文本内容
    """
    try:
        full_path = os.path.join(DATA_ROOT_DIR, doc_path)
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取 <TEXT> 标签中的内容
        text_match = re.search(r'<TEXT>\s*(.*?)\s*</TEXT>', content, re.DOTALL)
        if text_match:
            return text_match.group(1).strip()
        return ""
    except Exception as e:
        return ""

def extract_document_metadata(doc_path):
    """
    从原始文件中提取文档的元数据信息
    :param doc_path: 文档的相对路径（从索引中获取）
    :return: 包含 DOCTYPE 和 TXTTYPE 的字典
    """
    try:
        full_path = os.path.join(DATA_ROOT_DIR, doc_path)
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 提取 DOCTYPE
        doctype_match = re.search(r'<DOCTYPE>\s*(.*?)\s*</DOCTYPE>', content, re.DOTALL)
        doctype = doctype_match.group(1).strip() if doctype_match else "N/A"
        
        # 提取 TXTTYPE
        txttype_match = re.search(r'<TXTTYPE>\s*(.*?)\s*</TXTTYPE>', content, re.DOTALL)
        txttype = txttype_match.group(1).strip() if txttype_match else "N/A"
        
        return {
            'doctype': doctype,
            'txttype': txttype
        }
    except Exception as e:
        return {
            'doctype': 'N/A',
            'txttype': 'N/A'
        }

def generate_snippet(content, query_terms, max_length=200):
    """
    生成包含查询词的摘要片段
    :param content: 文档内容
    :param query_terms: 查询词列表
    :param max_length: 摘要最大长度
    :return: 高亮的摘要片段
    """
    if not content:
        return "（文档内容为空）"
    
    # 清理内容，移除多余的空白字符
    content = ' '.join(content.split())
    
    # 将内容转换为小写以便匹配（不区分大小写）
    content_lower = content.lower()
    
    # 找到第一个查询词的位置
    first_pos = -1
    for term in query_terms:
        term_lower = term.lower()
        pos = content_lower.find(term_lower)
        if pos != -1 and (first_pos == -1 or pos < first_pos):
            first_pos = pos
    
    if first_pos == -1:
        # 如果没有找到查询词，返回文档开头
        snippet = content[:max_length]
        if len(content) > max_length:
            snippet += "..."
        # 高亮处理
        for term in query_terms:
            pattern = re.compile(r'\b' + re.escape(term) + r'\w*\b', re.IGNORECASE)
            snippet = pattern.sub(lambda m: f"【{m.group(0)}】", snippet)
        return snippet
    
    # 计算摘要的起始和结束位置（以查询词为中心）
    start = max(0, first_pos - max_length // 2)
    end = min(len(content), first_pos + max_length // 2)
    
    snippet = content[start:end]
    
    # 添加省略号
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    
    # 高亮所有查询词
    for term in query_terms:
        pattern = re.compile(r'\b' + re.escape(term) + r'\w*\b', re.IGNORECASE)
        snippet = pattern.sub(lambda m: f"【{m.group(0)}】", snippet)
    
    return snippet

def search_index(query_string, hits_limit):
    """执行搜索并打印结果。"""
    if not os.path.exists(INDEX_DIR):
        print(f"错误：找不到索引目录 '{INDEX_DIR}'。请先运行 indexer.py。")
        return

    # 1. 打开索引
    ix = open_dir(INDEX_DIR)
    
    # 2. 创建 QueryParser (查询解析器)
    # 我们将主要在 'content' 字段中搜索
    parser = QueryParser("content", ix.schema)
    
    # 解析查询字符串，使其支持 free text 和 "quoted phrases"
    # Whoosh 的 QueryParser 默认支持布尔运算符、字段限定和短语查询，与作业要求匹配。
    try:
        query = parser.parse(query_string)
    except Exception as e:
        print(f"查询解析错误: {e}")
        return

    start_time = time.time()
    
    # 3. 创建 Searcher 并使用自定义评分函数
    # 在 with 语句中打开 Searcher，并在 with 块结束后自动关闭。
    # 关键：weighting=CustomTfIdf() 使得搜索使用我们的自定义 TF-IDF 评分。
    with ix.searcher(weighting=CustomTfIdf()) as searcher:
        
        # 4. 执行搜索
        # limit=hits_limit 限制返回的结果数量（即作业中的 Top-N）
        results = searcher.search(query, limit=hits_limit)
        
        end_time = time.time()
        
        # 5. 打印搜索结果头
        print("-" * 60)
        print(f"查询 = {query_string} (耗时: {end_time - start_time:.3f} 秒)")
        print(f"总命中数: {len(results)}")
        print(f"返回 Top {hits_limit} 结果:")
        print("-" * 60)

        # 6. 结果格式化和展示 (Rank, Score, DocID, Summary)
        if not results:
            print("未找到任何匹配文档。")
            return

        # 提取查询词用于高亮（使用原始查询字符串，避免词干提取）
        # 这样可以确保高亮显示完整的单词，而不是词干
        query_terms = query_string.lower().split()

        for i, hit in enumerate(results):
            # Rank: 排名
            rank = i + 1
            # Score: 自定义评分函数返回的分数
            score = hit.score
            # DocID: 存储的文档编号
            doc_id = hit.get('docID', 'N/A')
            # doc_path: 文档路径
            doc_path = hit.get('doc_path', '')
            
            # 提取文档元数据
            metadata = extract_document_metadata(doc_path)
            doctype = metadata['doctype']
            txttype = metadata['txttype']
            
            # 从原始文件读取内容并生成摘要
            content = read_document_content(doc_path)
            # 调整 max_length 参数来控制摘要长度（单位：字符）
            # 建议值：150-500 之间
            snippet = generate_snippet(content, query_terms, max_length=250)
            
            # 美化的输出格式
            print(f"No: {rank:>2}    Score: {score:>8.4f}    DocNo: {doc_id:<20}    DocType: {doctype:<10}    TxtType: {txttype}")
            print("-" * 100)
            # 打印摘要，并去除多余的换行符和首尾空格，合并多余空格
            clean_snippet = ' '.join(snippet.replace('\n', ' ').split())
            print(clean_snippet)
            print("=" * 100)
            print()
            
    print("-" * 60)


def main():
    """主函数，负责命令行参数解析。"""
    parser = argparse.ArgumentParser(description="自定义信息检索命令行搜索工具")
    
    # 命令行格式要求：# search --hits XX new york san francisco
    # 所以第一个参数是查询字符串列表
    parser.add_argument('query_parts', 
                        nargs=argparse.REMAINDER, 
                        help='查询词或短语 (例如: "new york city" apple cider)')
                        
    # --hits XX 可配置返回结果数
    parser.add_argument('--hits', 
                        type=int, 
                        default=DEFAULT_HITS, 
                        help=f'返回 Top-N 结果的数量 (默认: {DEFAULT_HITS})')

    args = parser.parse_args()
    
    # 检查是否有 --hits 参数后还有查询词
    if not args.query_parts:
        print("用法错误: 请提供查询词。示例: search.py --hits 10 hurricane")
        return

    # 将所有剩余的查询部分重新组合成一个字符串
    query_string = " ".join(args.query_parts)
    
    # 检查用户是否错误地输入了'search'作为第一个词，如果是，则去掉。
    if query_string.lower().startswith('# search'):
         query_string = query_string[len('# search'):].strip()

    if not query_string:
        print("请输入有效的查询内容。")
        return
        
    search_index(query_string, args.hits)

if __name__ == '__main__':
    main()