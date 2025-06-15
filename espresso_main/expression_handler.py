# expression_handler.py
# 模块功能：处理布尔表达式的解析和格式化。
# - parse_expression: 将人类可读的表达式字符串转换为内部使用的“位置立方体”表示法。
# - format_expression: 将内部表示的立方体覆盖转换回人类可读的表达式字符串。
# - get_vars: 从表达式中提取所有变量名。

import re


def get_vars(expr_str):
    """
    从布尔表达式字符串中提取所有唯一的、按字母顺序排序的变量名。
    :param expr_str:  输入的布尔表达式字符串。
    :return: 一个包含所有单字符变量名的有序list。
    """
    # 使用正则表达式找到所有字母，它们代表变量名。
    # 使用 set 去重，然后 sorted 排序，确保变量顺序始终一致。
    vars_found = sorted(list(set(re.findall(r'[a-zA-Z]', expr_str))))
    return vars_found


def parse_expression(expr_str):
    """
    将布尔表达式字符串解析为“位置立方体表示法”(Positional-Cube Notation) 的覆盖(cover)。
    新格式示例: (a && !d) || (b && c)

    内部表示法回顾:
    对于一个变量，例如 'a':
    - 'a' (正向)  -> '01'
    - '!a' (反向) -> '10'
    - 无关 (don't care) -> '11'
    一个包含 a,b,c 三个变量的项 "a && !c" 会被转换为 "011110"。

    :param
        expr_str:  输入的布尔表达式字符串。

    :returns:
        tuple: 包含两个元素的元组
            - cover (list): 一个由立方体字符串组成的列表。
            - var_map (dict): 一个将变量名映射到其在立方体中起始索引的字典。
    """
    # 如果输入为空，直接返回空结果
    if not expr_str or not expr_str.strip():
        return [], {}

    # 识别所有变量并建立映射关系
    variables = get_vars(expr_str)
    var_map = {var: i * 2 for i, var in enumerate(variables)}
    num_vars = len(variables)

    # 按 "||" 分割表达式，得到各个乘积项
    terms_str = expr_str.split('||')

    cover = []
    for term_s in terms_str:
        # 3. 为每个乘积项创建一个立方体
        # 初始化为全 "11" (don't care)
        cube = ['11'] * num_vars

        # 去除项两端的空格和括号
        term_s = term_s.strip()
        if term_s.startswith('(') and term_s.endswith(')'):
            term_s = term_s[1:-1]

        # 4. 按 "&&" 分割乘积项，得到各个变量
        literals_str = term_s.split('&&')

        # 检查项内一致性标志
        valid_term = True
        seen_vars = {}

        for literal_s in literals_str:
            literal_s = literal_s.strip()
            if not literal_s:
                continue

            # 5. 解析每个文字，判断是否为“非”
            is_negated = literal_s.startswith('!')
            var_name = literal_s.lstrip('!').strip()

            if var_name in var_map:
                var_idx = var_map[var_name] // 2

                # 检查变量是否已经出现过（防止 a && !a的情况）
                if var_name in seen_vars:
                    # 检查是否冲突 (a && !a)
                    if seen_vars[var_name] != is_negated:
                        valid_term = False  # 发现冲突
                        break
                else:
                    # 首次出现，记录值
                    seen_vars[var_name] = is_negated
                    cube[var_idx] = '10' if is_negated else '01'

        # 如果项有效且不为空,加入进去形成cover
        if valid_term and seen_vars:
            cover.append("".join(cube))

    return cover, var_map


def format_expression(cover, var_map):
    """
    将一个用位置立方体表示的覆盖转换回人类可读的布尔表达式字符串。
    新格式示例: (a && !d) || (b && c)

    :param cover: (list) 一个由立方体字符串组成的列表。
    :param var_map: (dict) 变量名到索引的映射字典。

    :return:
        格式化后的布尔表达式字符串。
    """

    # 什么都没有是 False
    if not cover:
        return "False"

    # 创建一个反向的 var_map ,用于从索引查找变量名
    rev_var_map = {v: k for k, v in var_map.items()}

    all_terms = []
    for cube in cover:
        term_parts = []
        is_tautology = True  # 标记立方体是否为全 "11"

        # 1. 遍历立方体中的每个变量部分
        for i in range(0, len(cube), 2):
            part = cube[i:i + 2]
            if part != '11':
                is_tautology = False
                var_name = rev_var_map.get(i)
                if var_name:
                    # 根据 '01' 或 '10' 格式化为 "!a" 或 "a"
                    formatted_literal = f"!{var_name}" if part == '10' else var_name
                    term_parts.append(formatted_literal)

        # 2. 如果立方体是全 "11", 它代表True
        if is_tautology and var_map:
            return "True"

        # 3. 将单个项的Product用 "&&" 连接，加上括号
        if term_parts:
            # 对文字按变量名排序以保持输出一致性
            all_terms.append(f'({" && ".join(sorted(term_parts))})')

    # 4. 将所有项用 "||" 连接
    return " || ".join(sorted(all_terms))
