# espresso_core.py
# 模块功能：实现 Espresso 算法的核心操作。
# 这是算法的大脑，包含 expand, reduce, 和 irredundant 三个关键步骤。

from itertools import product


# --- 辅助函数 ---
def cube_contains(c1: str, c2: str) -> bool:
    """
    检查 c1 是否为 c2 的超集
        :rtype: bool
        :return: 如果 c1 包含 c2，返回 True，否则返回 False。
    """
    for i in range(0, len(c1), 2):
        p1 = c1[i:i + 2];
        p2 = c2[i:i + 2];
        # c1 的某一位是确定值('01'或'10')，而 c2 的对应位不是相同的值，则 c1 不包含 c2。
        if (p1 == '01' and p2 != '01') or \
                (p1 == '10' and p2 != '10'):
            return False
    return True


def get_minterms(cube: str) -> set[str]:
    """
    生成一个立方体所包含的所有 minterms。
    最小项是立方体最具体的表现形式，不包含任何 '11'

    :param cube:一个立方体字符串。
    :return:  一个包含该立方体所有最小项字符串的集合。
    """

    num_vars = len(cube) // 2
    # 'parts' 列表的每个元素都是一个列表，代表一个变量位所有可能的最小项形式。
    parts = []
    for i in range(num_vars):
        part = cube[i * 2:i * 2 + 2]
        if part == '01':
            parts.append(['01'])
        elif part == '10':
            parts.append(['10'])
        else:  # "11" don't care, 意味着两种可能性都存在
            parts.append(['01', '10'])

    # 使用 itertools.product 计算所有部分的笛卡尔积，生成所有最小项。
    minterms_tuples = product(*parts)
    minterms = ["".join(p) for p in minterms_tuples]
    return set(minterms)


def is_covered(minterm, cover):
    """检查一个最小项是否被一个cover所包含。"""
    for cube in cover:
        if cube_contains(cube, minterm):
            return True
    return False


def complement(cover, num_vars):
    """计算一个覆盖的补集 (OFF-set)，即所有不在该覆盖中的最小项。"""
    all_minterms = ["".join(p) for p in product(['01', '10'], repeat=num_vars)]
    on_set_minterms = set()
    for cube in cover:
        on_set_minterms.update(get_minterms(cube))
    off_set = [m for m in all_minterms if m not in on_set_minterms]
    return off_set


def cube_intersection(c1, c2):
    """
        :return cube: 两个立方体的交集。如果无交集则返回 None
    """
    result = []
    for i in range(0, len(c1), 2):
        p1, p2 = c1[i:i + 2], c2[i:i + 2]
        # '01'&'10' -> '00' (空)，'01'&'01' -> '01'，'11'&'01' -> '01'
        intersect = "".join([str(int(b1) & int(b2)) for b1, b2 in zip(p1, p2)])
        if intersect == '00': return None
        result.append(intersect)
    return "".join(result)


def supercube(minterm_set):
    """计算一个最小项集合的立方体"""
    if not minterm_set: return None
    num_vars = len(next(iter(minterm_set))) // 2
    super_cube_parts = []
    for i in range(num_vars):
        # 获取所有最小项在当前变量位的形式
        parts_at_i = {m[i * 2:i * 2 + 2] for m in minterm_set}
        # 如果所有形式都一样，则超立方体在该位也一样；否则，为 '11' (don't care)。
        super_cube_parts.append(parts_at_i.pop() if len(parts_at_i) == 1 else '11')
    return "".join(super_cube_parts)


def cost(cover, var_map):
    """计算一个覆盖的成本（SOP成本：乘积项数 + 文字数）。"""
    if not cover: return 0
    num_literals = sum(1 for cube in cover for i in range(0, len(cube), 2) if cube[i:i + 2] != '11')
    return len(cover) * 10 + num_literals


# ==== Espresso 三个操作 ====

def expand(cover, off_set):
    # EXPAND: 将每个立方体扩展为素蕴含项，使其尽可能大而不与OFF-set冲突
    # 主要逻辑是：优先扩展包含文字最多的立方体
    expanded_cover = []

    sorted_cover = sorted(cover, key=lambda c: c.count('11'))
    for cube in sorted_cover:
        if any(cube_contains(ec, cube) for ec in expanded_cover): continue
        temp_cube = cube
        can_expand = True
        while can_expand:
            can_expand = False
            for i in range(0, len(temp_cube), 2):
                if temp_cube[i:i + 2] != '11':  # 尝试移除一个literal
                    expanded_once = list(temp_cube);
                    expanded_once[i:i + 2] = '11'
                    expanded_once = "".join(expanded_once)
                    # 如果expand后不与OFF-set相交，则是有效
                    if not any(cube_intersection(expanded_once, off) for off in off_set):
                        temp_cube = expanded_once;
                        can_expand = True;
                        break
        expanded_cover.append(temp_cube)
    return expanded_cover


def irredundant(cover):
    # IRREDUNDANT: 移除覆盖中的冗余项，得到一个无冗余的覆盖。
    final_cover = list(cover)
    for i in range(len(final_cover) - 1, -1, -1):
        cube_to_check = final_cover[i]
        other_cubes = final_cover[:i] + final_cover[i + 1:]
        if not other_cubes: continue
        # 如果一个立方体的所有最小项都被其他立方体覆盖，则它是冗余的
        if all(is_covered(m, other_cubes) for m in get_minterms(cube_to_check)):
            final_cover.pop(i)
    return final_cover


def reduce(cover):
    # REDUCE: 在保持功能不变的前提下，尽可能地缩小每个立方体。
    final_cover = []
    for i, cube_to_reduce in enumerate(cover):
        context_cover = cover[:i] + cover[i + 1:]
        context_minterms = set().union(*(get_minterms(c) for c in context_cover))
        # 识别当前立方体的"本质"最小项
        essential_minterms = get_minterms(cube_to_reduce) - context_minterms
        print(type(essential_minterms));
        # 是否有本质最小项
        if not essential_minterms:
            # 如果没有本质最小项，说明此立方体可能冗余，暂时保留
            final_cover.append(cube_to_reduce)
        else:
            # 否则，将立方体缩减为其本质最小项的超立方体
            reduced_cube = supercube(essential_minterms)
            final_cover.append(reduced_cube)
    return final_cover
