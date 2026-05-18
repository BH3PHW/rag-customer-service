"""
Query Preprocessing Module - Spelling Correction

Features:
1. Spelling correction for user queries
2. Pinyin-based fuzzy matching
3. Common typo patterns
"""
from typing import List, Dict, Tuple, Optional
import re


class SpellingCorrector:
    """
    Spelling corrector for Chinese text
    
    Handles common typos:
    1. Pinyin similarity errors (拼音相似错误)
    2. Homophone errors (同音字错误)
    3. Keyboard adjacency errors (键盘相邻错误)
    4. Common typos (常见错别字)
    """
    
    # 常见拼音错误映射 (声母/韵母错误)
    PINYIN_ERRORS = {
        # n/l 混淆
        "蓝": "南", "啦": "哪", "里": "你", "了": "呢",
        "来": "奶", "老": "脑", "楼": "牛",
        # zh/z 混淆
        "知": "资", "这": "则", "中": "宗",
        # ch/c 混淆
        "吃": "次", "出": "粗",
        # sh/s 混淆
        "是": "四", "说": "所", "书": "苏",
        # b/p 混淆
        "不": "扑", "吧": "趴",
        # d/t 混淆
        "的": "特", "到": "套",
        # g/k 混淆
        "给": "可",
        # r/l 混淆
        "人": "邻",
    }
    
    # 常见错别字词组
    COMMON_TYPOS = {
        "蓝呀连接": "蓝牙连接",
        "蓝牙联接": "蓝牙连接",
        "蓝夜连接": "蓝牙连接",
        "兰牙连接": "蓝牙连接",
        "无线程": "无线连接",
        "无限连接": "无线连接",
        "联接": "连接",
        "网网": "网络",
        "互关网": "互联网",
        "互网": "互联网",
        "程序": "程序",
        "厨房": "厨房",
        "窗户": "窗户",
        "明年": "明年",
        "后年": "后年",
        "地址": "地址",
        "地主": "地主",
        "已经": "已经",
        "以经": "已经",
    }
    
    # 键盘相邻键映射 (用于检测键盘输入错误)
    KEYBOARD_ADJACENCY = {
        'q': 'wa', 'w': 'qeas', 'e': 'wrds', 'r': 'etdf', 't': 'ryfg',
        'y': 'tghu', 'u': 'yihj', 'i': 'ujko', 'o': 'iklp', 'p': 'ol',
        'a': 'qwsz', 's': 'qweazx', 'd': 'werfxc', 'f': 'ertgvc',
        'g': 'rtyhbv', 'h': 'tyujnb', 'j': 'yuikmn', 'k': 'uiolm',
        'l': 'iopk',
        'z': 'asx', 'x': 'sdcza', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn',
        'n': 'bhjm', 'm': 'njk'
    }
    
    def __init__(self):
        self.typo_patterns = self._compile_typo_patterns()
    
    def _compile_typo_patterns(self) -> re.Pattern:
        """编译错别字正则模式"""
        # 匹配重复字符 (如 "网网")
        return re.compile(r'(.)\1{1,}')
    
    def correct(self, text: str) -> Tuple[str, List[Dict]]:
        """
        纠正文本中的拼写错误
        
        Args:
            text: 输入文本
        
        Returns:
            Tuple of (corrected_text, list of corrections)
        """
        corrections = []
        corrected = text
        
        # 1. 词组级别纠正 (优先)
        for wrong, correct in self.COMMON_TYPOS.items():
            if wrong in corrected:
                corrections.append({
                    "type": "typo",
                    "original": wrong,
                    "corrected": correct,
                    "position": corrected.find(wrong)
                })
                corrected = corrected.replace(wrong, correct)
        
        # 2. 单字级别纠正 (基于拼音相似)
        for wrong, correct in self.PINYIN_ERRORS.items():
            if wrong in corrected:
                corrections.append({
                    "type": "pinyin",
                    "original": wrong,
                    "corrected": correct,
                    "position": corrected.find(wrong)
                })
                corrected = corrected.replace(wrong, correct, 1)
        
        # 3. 重复字符纠正
        matches = self.typo_patterns.findall(corrected)
        for match in matches:
            if len(match) >= 2:
                corrections.append({
                    "type": "repeat",
                    "original": match * 2 if len(match) == 1 else match[0] * 2,
                    "corrected": match,
                    "position": corrected.find(match * 2) if len(match) == 1 else -1
                })
        
        return corrected, corrections
    
    def suggest_corrections(self, text: str, max_suggestions: int = 3) -> List[str]:
        """
        生成纠正建议
        
        Args:
            text: 输入文本
            max_suggestions: 最大建议数量
        
        Returns:
            List of suggested corrections
        """
        suggestions = []
        
        corrected, corrections = self.correct(text)
        
        if corrections:
            suggestions.append(corrected)
        
        # 生成键盘相邻字符的替代建议
        for i, char in enumerate(text):
            if char.isalpha() and char.lower() in self.KEYBOARD_ADJACENCY:
                adjacent = self.KEYBOARD_ADJACENCY[char.lower()]
                for adj_char in adjacent[:2]:
                    suggestion = text[:i] + (adj_char if char.islower() else adj_char.upper()) + text[i+1:]
                    if suggestion != text:
                        suggestions.append(suggestion)
        
        return suggestions[:max_suggestions]
    
    def is_valid(self, text: str) -> bool:
        """
        检查文本是否需要纠正
        
        Args:
            text: 输入文本
        
        Returns:
            True if text is valid (no obvious errors)
        """
        # 检查是否包含任何已知错误模式
        for typo in self.COMMON_TYPOS.keys():
            if typo in text:
                return False
        
        # 检查重复字符
        if self.typo_patterns.search(text):
            return False
        
        return True


class QueryPreprocessor:
    """
    Query preprocessing pipeline
    
    Combines multiple preprocessing steps:
    1. Spelling correction
    2. Whitespace normalization
    3. Punctuation normalization
    4. Query expansion (optional)
    """
    
    def __init__(self, enable_correction: bool = True):
        self.spell_corrector = SpellingCorrector()
        self.enable_correction = enable_correction
        
        # 标点符号规范化映射
        self.punctuation_map = {
            '，': ',',
            '。': '.',
            '！': '!',
            '？': '?',
            '；': ';',
            '：': ':',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
            '《': '<',
            '》': '>',
        }
    
    def preprocess(self, query: str) -> Dict[str, any]:
        """
        预处理查询文本
        
        Args:
            query: 原始查询
        
        Returns:
            Dict containing:
            - original: 原始查询
            - corrected: 纠正后的查询
            - corrections: 纠正详情列表
            - normalized: 规范化后的查询
            - warnings: 警告信息
        """
        result = {
            "original": query,
            "corrected": query,
            "corrections": [],
            "normalized": query,
            "warnings": []
        }
        
        # 1. 去除首尾空白
        processed = query.strip()
        
        # 2. 标点符号规范化
        for old, new in self.punctuation_map.items():
            if old in processed:
                processed = processed.replace(old, new)
        
        # 3. 多余空格处理
        processed = re.sub(r'\s+', ' ', processed)
        
        # 4. 拼写纠错
        if self.enable_correction:
            corrected, corrections = self.spell_corrector.correct(processed)
            result["corrected"] = corrected
            result["corrections"] = corrections
            
            if corrections:
                processed = corrected
                result["warnings"].append(f"已自动纠正 {len(corrections)} 处拼写错误")
        
        # 5. 去除控制字符
        processed = ''.join(char for char in processed if ord(char) >= 32 or char in '\n\t')
        
        result["normalized"] = processed
        
        return result
    
    def preprocess_for_retrieval(self, query: str) -> str:
        """
        预处理查询用于向量检索
        
        Args:
            query: 原始查询
        
        Returns:
            处理后的查询文本
        """
        result = self.preprocess(query)
        return result["normalized"]


# Singleton instance
_query_preprocessor: Optional[QueryPreprocessor] = None


def get_query_preprocessor() -> QueryPreprocessor:
    """Get singleton instance of QueryPreprocessor"""
    global _query_preprocessor
    if _query_preprocessor is None:
        _query_preprocessor = QueryPreprocessor()
    return _query_preprocessor
