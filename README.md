# 信息检索系统使用说明

## ✅ 修复内容（2025-11-03）

### 已修复的问题

1. ✅ **高亮显示完整** - 现在会高亮完整的单词（如 "【hurricane】" 而不是 "【hurrican】e"）
2. ✅ **消除重复输出** - 优化了输出逻辑，移除多余空格和换行
3. ✅ **默认Top 10** - 不指定`--hits`参数时默认返回前10个结果
4. ✅ **修复短语搜索** - 添加了 `max_quality()` 方法支持复杂查询

## 🚀 使用方法

### 基本搜索（返回Top 10）

```bash
python search.py hurricane
```

### 指定返回结果数量

```bash
python search.py --hits 5 hurricane
python search.py --hits 20 hurricane
```

### 短语搜索

```bash
python search.py "new york"
```

### 多词搜索

```bash
python search.py hurricane disaster relief
```

## 📊 输出格式

```text
01 [17.2345] APW19981027.0512
...文档摘要，查询词会被【高亮】显示...
```

- `01` - 排名（第1名）
- `[17.2345]` - TF-IDF 相关性评分（越高越相关）
- `APW19981027.0512` - 文档ID
- 摘要 - 包含查询词的文档片段，查询词用【】标记

## 🔧 配置选项

### 调整摘要长度

编辑 `search.py` 第 159 行：

```python
snippet = generate_snippet(content, query_terms, max_length=350)
```

修改 `max_length` 值（推荐范围：150-500）

### 修改默认返回数量

编辑 `search.py` 第 13 行：

```python
DEFAULT_HITS = 10  # 改为你想要的默认值
```

## 📁 项目结构

```text
├── indexer.py          # 索引构建器
├── search.py           # 搜索引擎
├── custom_scorer.py    # 自定义TF-IDF评分函数
├── TDT3_Data/          # 原始文档数据
└── index_data/         # 生成的索引文件（自动生成，不提交到Git）
```

## 🔄 重建索引

如果需要重建索引：

```bash
# 删除旧索引
Remove-Item -Recurse -Force index_data

# 重新构建
python indexer.py
```

## 📈 系统信息

- 索引文档数：37,526篇
- 评分方法：自定义TF-IDF
- 索引构建时间：约3-4分钟
- 平均搜索时间：< 0.1秒
