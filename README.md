# 信息检索系统使用说明

## ✅ 修复内容（2025-11-04）

### 最新更新

1. ✅ **交互式搜索界面** - 新增 `cmd.py` 支持多次查询，输入 quit/exit 退出
2. ✅ **文档摘要显示** - 替换高亮片段为文档摘要（默认100字符）
3. ✅ **删除高亮功能** - 简化输出，专注于文档内容摘要
4. ✅ **优化用户体验** - 交互式界面提供更好的使用体验

### 已修复的历史问题

1. ✅ **高亮显示完整** - 现在输出文档摘要而非高亮片段
2. ✅ **消除重复输出** - 优化了输出逻辑，移除多余空格和换行
3. ✅ **默认Top 10** - 不指定`--hits`参数时默认返回前10个结果
4. ✅ **修复短语搜索** - 添加了 `max_quality()` 方法支持复杂查询

## 🚀 使用方法

### 交互式搜索（推荐）

启动交互式搜索界面：

```bash
python cmd.py
```

在交互界面中：

- 输入查询词: `hurricane`
- 指定结果数量: `--hits 5 hurricane`
- 短语搜索: `"new york"`
- 多词搜索: `hurricane disaster relief`
- 退出程序: `quit` 或 `exit`

### 单次搜索命令

#### 基本搜索（返回Top 10）

```bash
python search.py hurricane
```

#### 指定返回结果数量

```bash
python search.py --hits 5 hurricane
python search.py --hits 20 hurricane
```

#### 短语搜索

```bash
python search.py "new york"
```

#### 多词搜索

```bash
python search.py hurricane disaster relief
```

## 📊 输出格式

```text
No:  1    Score:  17.2345    DocNo: APW19981027.0512      DocType: NEWS       TxtType: NEWSWIRE
----------------------------------------------------------------------------------------------------
In the days before Hurricane Georges struck the Gulf Coast last week, storm forecasters faced...
====================================================================================================
```

- `No: 1` - 排名（第1名）
- `Score: 17.2345` - TF-IDF 相关性评分（越高越相关）
- `DocNo: APW19981027.0512` - 文档ID
- `DocType/TxtType` - 文档类型和文本类型
- 摘要 - 文档开头的内容摘要（默认100字符）

## 🔧 配置选项

### 调整摘要长度

编辑 `search.py` 或 `cmd.py` 中的 `generate_summary()` 调用：

```python
summary = generate_summary(content, max_length=150)  # 修改为你想要的长度
```

推荐摘要长度范围：50-200字符

### 修改默认返回数量

编辑文件顶部的 `DEFAULT_HITS` 常量：

```python
DEFAULT_HITS = 10  # 改为你想要的默认值
```

## 📁 项目结构

```text
├── cmd.py              # 🆕 交互式搜索界面
├── search.py           # 单次搜索命令
├── indexer.py          # 索引构建器
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

## 🎯 快速开始

1. **建立索引**（首次使用）：

   ```bash
   python indexer.py
   ```

2. **开始搜索**：

   ```bash
   python cmd.py
   ```

3. **进行查询**：
   - 输入: `hurricane`
   - 输入: `--hits 5 "new york"`
   - 输入: `quit` （退出）

## 📈 系统信息

- 索引文档数：37,526篇
- 评分方法：自定义TF-IDF
- 摘要长度：默认100字符
- 索引构建时间：约3-4分钟
- 平均搜索时间：< 0.1秒
- 支持功能：短语查询、多词查询、交互式搜索

## 🔍 使用示例

### 交互式搜索示例

```text
🔍 请输入查询 (quit/exit 退出): hurricane
------------------------------------------------------------
查询 = hurricane (耗时: 0.045 秒)
总命中数: 10
返回 Top 10 结果:
------------------------------------------------------------
No:  1    Score:  17.2345    DocNo: NYT19981003.0052      DocType: NEWS       TxtType: NEWSWIRE
----------------------------------------------------------------------------------------------------
In the days before Hurricane Georges struck the Gulf Coast last week, storm forecasters faced...
====================================================================================================

🔍 请输入查询 (quit/exit 退出): --hits 3 "new york"
...

🔍 请输入查询 (quit/exit 退出): quit
👋 感谢使用信息检索系统，再见！
```
