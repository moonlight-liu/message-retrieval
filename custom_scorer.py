from whoosh.scoring import Weighting, BaseScorer
import math

# --------------------------
# 1. 自定义 TF-IDF 评分器 (Scorer) 类
# --------------------------
class CustomTfIdfScorer(BaseScorer):
    """
    实现基于 Whoosh 的自定义 TF-IDF 评分函数。
    """
    
    def __init__(self, searcher, fieldname, text, qf=1):
        """
        初始化评分器。
        :param searcher: Whoosh Searcher 对象，用于获取全局统计信息（如 N 和 DF）。
        :param fieldname: 正在评分的字段名（例如 'content'）。
        :param text: 查询词文本
        :param qf: 查询频率 (query frequency)
        """
        self.searcher = searcher
        self.fieldname = fieldname
        self.text = text
        self.qf = qf
        
        # N: 文档总数 (Total number of documents)
        self.N = searcher.doc_count()

    def score(self, matcher):
        """
        计算当前文档的得分。
        这个方法在 Whoosh 匹配到文档时被调用。
        
        :param matcher: 一个 Matcher 对象，提供当前文档的信息。
        :return: 当前文档的相关性得分。
        """
        
        # 1. 提取词频信息 (Term Frequency, TF)
        # matcher.weight() 返回的是当前词 (Term) 在当前文档 (Doc) 中的权重。
        # 对于我们 'content' 字段的默认配置，它返回的是原始的词频 (TF)。
        tf = matcher.weight()
        
        # 2. 计算平滑 TF (Smooth TF)
        # 常见的平滑处理，防止文档过短导致 TF 权重过低。
        # 1 + log(tf) 是一个常用的平滑公式。
        if tf > 0:
            smoothed_tf = 1.0 + math.log(tf)
        else:
            smoothed_tf = 0.0

        # 3. 提取文档频率信息 (Document Frequency, DF)
        # 使用 searcher 和 fieldname 来获取 DF，因为不同版本的 Whoosh 可能有不同的 API
        try:
            # 尝试从 matcher 获取 DF
            if hasattr(matcher, 'doc_frequency'):
                df = matcher.doc_frequency()
            else:
                # 使用 searcher 获取该词的 DF
                df = self.searcher.doc_frequency(self.fieldname, self.text)
        except:
            # 如果获取失败，使用一个合理的默认值
            df = 1
        
        # 4. 计算 IDF (Inverse Document Frequency)
        # IDF = log(N / DF)
        # 为了避免 DF=0 导致的除零错误，虽然理论上不会发生，但加上 DF > 0 的检查是好习惯。
        if df > 0:
            idf = math.log(self.N / df)
        else:
            idf = 0.0
            
        # 5. 最终得分 = 平滑TF * IDF
        return smoothed_tf * idf
    
    def max_quality(self):
        """
        返回此评分器可能产生的最大分数。
        这对于某些搜索优化是必需的。
        """
        # 返回一个合理的最大值估计
        # 最大TF通常不会超过1000，最大IDF通常不会超过log(N)
        max_tf = 1.0 + math.log(1000)  # 假设最大TF为1000
        max_idf = math.log(self.N) if self.N > 1 else 1.0
        return max_tf * max_idf

# --------------------------
# 2. 自定义评分权重类 (Weighting)
# --------------------------
class CustomTfIdf(Weighting):
    """
    Whoosh 的评分权重类。它定义了如何创建 Scorer 实例。
    我们将它传递给搜索器 (Searcher)。
    """
    
    def scorer(self, searcher, fieldname, text, qf=1):
        """
        返回一个 CustomTfIdfScorer 实例。
        兼容新版本 Whoosh 的 scorer 方法签名
        """
        # 返回我们自定义的 Scorer 对象
        return CustomTfIdfScorer(searcher, fieldname, text, qf)