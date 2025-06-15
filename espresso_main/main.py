# main.py
# 模块功能：Espresso 算法的主程序入口。
# - 负责读取输入文件，调用核心算法，并将结果写入输出文件。
# - 展示了算法的完整执行流程。

from expression_handler import parse_expression, format_expression
from espresso_core import expand, reduce, irredundant, complement, cost
import os


def espresso_algorithm(boolean_expression):
    """
    执行简化的 Espresso 算法来最小化一个布尔函数
    :param boolean_expression: 布尔表达式字符串
    :returns: 最小化后的布尔表达式。
    """
    print("--- 算法开始 ---")

    # 解析输入表达式，转换为内部立方体表示
    cover, var_map = parse_expression(boolean_expression)
    num_vars = len(var_map)

    if not cover:
        print("输入表达式为空")
        return "0"

    print(f"初始表达式: {format_expression(cover, var_map)}")
    print(f"变量映射: {var_map}")
    print(f"初始成本: {cost(cover, var_map)}")

    # 计算 OFF-set (所有不属于 ON-set 的最小项)
    off_set = complement(cover, num_vars)
    print(f"计算出的 OFF-set 包含 {len(off_set)} 个最小项。")

    # EXPAND -> IRREDUNDANT
    # 得到一个由素蕴含项组成的无冗余覆盖，这是第一个解
    F = expand(cover, off_set)
    print(f"\n首次 EXPAND 后: {format_expression(F, var_map)}")
    F = irredundant(F)
    print(f"首次 IRREDUNDANT 后: {format_expression(F, var_map)}")
    print(f"成本: {cost(F, var_map)}")

    # 通过反复的 REDUCE -> EXPAND -> IRREDUNDANT 寻找更优解
    last_cost = cost(F, var_map)
    for i in range(5):  # 设置最大迭代次数以防死循环
        print(f"\n--- 迭代优化 第 {i + 1} 轮 ---")

        F_reduced = reduce(F)
        print(f"REDUCE 后: {format_expression(F_reduced, var_map)}")

        F_expanded = expand(F_reduced, off_set)
        print(f"EXPAND 后: {format_expression(F_expanded, var_map)}")

        F_irredundant = irredundant(F_expanded)
        print(f"IRREDUNDANT 后: {format_expression(F_irredundant, var_map)}")

        current_cost = cost(F_irredundant, var_map)
        print(f"本轮成本: {current_cost}")

        # 如果成本不再降低，则迭代结束
        if current_cost >= last_cost:
            print("成本未降低，迭代结束。")
            F = F_irredundant
            break

        F = F_irredundant
        last_cost = current_cost

    print("\n--- 算法结束 ---")
    return format_expression(F, var_map)


# --- 主程序执行入口 ---
if __name__ == "__main__":
    input_filename = '../data/expressions.txt'
    output_filename = '../data/output.txt'

    # 从文件读取表达式,每行一个表达式）
    print(f"\n正在从 '{input_filename}' 读取表达式...")
    with open(input_filename, 'r', encoding='utf-8') as f:
        input_lines = f.readlines()
    minimized_results = []

    # 处理每一行表达式
    for i, line in enumerate(input_lines, 1):
        input_expression = line.strip()
        if not input_expression:  # 跳过空行
            continue

        print(f"\n========== 处理第 {i} 个表达式 ==========")
        print(f"原始表达式: {input_expression}")

        # 执行 Espresso 算法
        minimized_expression = espresso_algorithm(input_expression)
        minimized_results.append(minimized_expression)

        print(f"最小化结果: {minimized_expression}")

    # 将结果写入文件（每行一个结果）
    with open(output_filename, 'w', encoding='utf-8') as f:
        for result in minimized_results:
            f.write(result + '\n')

    print(f"\n处理 {len(minimized_results)} 个表达式，结果已写入 '{output_filename}'。")
