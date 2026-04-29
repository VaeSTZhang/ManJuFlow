import re
from typing import Any


_CJK = r"\u4e00-\u9fff"
_CJK_PUNCT = r"，。！？；：、“”‘’（）《》【】—…"
_ASCII_WORD = r"A-Za-z"


_self_test_cases = [
    ("二线城 市", "二线城市"),
    ("U盘 准备离开", "U盘准备离开"),
    (" 当晚十点", "当晚十点"),
    ("他 插上电脑", "他插上电脑"),
    ("不对 ，这些数字", "不对，这些数字"),
    ("大 楼玻璃幕墙", "大楼玻璃幕墙"),
    ("还有什 么好怕的？", "还有什么好怕的？"),
    ("科 技公司", "科技公司"),
    ("公 司会议室", "公司会议室"),
    ("反 转", "反转"),
]


def _clean_string(value: str) -> str:
    # Remove abnormal spaces inside Chinese text while keeping English and number spacing intact.
    value = value.strip()
    value = re.sub(rf"([{_CJK}])\s+([{_CJK_PUNCT}])", r"\1\2", value)
    value = re.sub(rf"([{_CJK_PUNCT}])\s+([{_CJK}])", r"\1\2", value)
    value = re.sub(rf"([{_CJK}])\s+([{_CJK}])", r"\1\2", value)
    value = re.sub(rf"([{_ASCII_WORD}]+[{_CJK}]+)\s+([{_CJK}])", r"\1\2", value)
    value = re.sub(rf"([{_CJK}])\s+([{_ASCII_WORD}]+[{_CJK}]+)", r"\1\2", value)
    return value


def clean_chinese_spacing(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: clean_chinese_spacing(item) for key, item in value.items()}

    if isinstance(value, list):
        return [clean_chinese_spacing(item) for item in value]

    if isinstance(value, str):
        return _clean_string(value)

    return value
