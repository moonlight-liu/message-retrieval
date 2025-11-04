import os.path
import re
from search import search_index, INDEX_DIR

# --- 配置 ---
DEFAULT_HITS = 10

def parse_command(user_input):
    """
    解析用户输入的命令
    返回 (query_string, hits_limit) 或 None（如果是退出命令）
    """
    user_input = user_input.strip()
    
    # 检查退出命令
    if user_input.lower() in ['quit', 'exit', 'q']:
        return None
    
    # 检查是否包含 --hits 参数
    if '--hits' in user_input:
        parts = user_input.split('--hits')
        if len(parts) == 2:
            query_part = parts[0].strip()
            hits_part = parts[1].strip()
            
            # 提取hits数量（取第一个数字）
            hits_match = re.match(r'(\d+)', hits_part)
            if hits_match:
                hits_limit = int(hits_match.group(1))
                # 检查hits后面是否还有查询词
                remaining_query = hits_part[len(hits_match.group(1)):].strip()
                if remaining_query:
                    query_part = (query_part + " " + remaining_query).strip()
                return query_part, hits_limit
    
    # 没有 --hits 参数，使用默认值
    return user_input, DEFAULT_HITS

def print_welcome():
    """打印欢迎信息和使用说明"""
    print("=" * 80)
    print("🔍 信息检索系统 - 交互式搜索界面")
    print("=" * 80)
    print("📋 使用说明:")
    print("  • 输入查询词进行搜索，例如: hurricane")
    print("  • 使用 --hits N 指定返回结果数量，例如: --hits 5 hurricane")
    print("  • 支持短语搜索，例如: \"new york\"")
    print("  • 支持多词搜索，例如: hurricane disaster relief")
    print("  • 支持混合查询，例如: \"new york\" hurricane disaster")
    print("  • 输入 quit 或 exit 退出程序")
    print("-" * 80)
    print(f"📊 系统信息: 默认返回 Top {DEFAULT_HITS} 结果")
    print("=" * 80)
    print()

def main():
    """主函数 - 交互式搜索循环"""
    # 检查索引是否存在
    if not os.path.exists(INDEX_DIR):
        print(f"❌ 错误：找不到索引目录 '{INDEX_DIR}'。请先运行 indexer.py 建立索引。")
        return

    # 打印欢迎信息
    print_welcome()

    # 主搜索循环
    while True:
        try:
            # 获取用户输入
            user_input = input("🔍 请输入查询 (quit/exit 退出): ").strip()
            
            if not user_input:
                print("⚠️  请输入有效的查询内容。")
                continue
                
            # 解析命令
            result = parse_command(user_input)
            if result is None:
                print("👋 感谢使用信息检索系统，再见！")
                break
                
            query_string, hits_limit = result
            
            if not query_string:
                print("⚠️  请输入有效的查询内容。")
                continue
                
            # 执行搜索 - 使用 search.py 的函数
            print()  # 空行用于格式化
            search_index(query_string, hits_limit)
            print()  # 空行用于格式化
            
        except KeyboardInterrupt:
            print("\n👋 检测到 Ctrl+C，退出程序。再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            print("请重新尝试输入查询。")

if __name__ == '__main__':
    main()