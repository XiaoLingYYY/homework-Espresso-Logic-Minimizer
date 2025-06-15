import random


# 表达式生成
def generate_literal(variable):
    return variable if random.random() < 0.5 else f"!{variable}"

def generate_and_term(variables, max_len):
    selected = sorted(random.sample(variables, random.randint(1, max_len)))
    return ' && '.join([generate_literal(v) for v in selected])

def generate_expression_format(num_literals, num_vars):
    variables = sorted([chr(97+i) for i in range(num_vars)])
    expression = []
    literal_count = 0
    used_terms = set()

    while literal_count < num_literals:
        term = generate_and_term(variables, num_vars)
        term_literals = [lit.strip() for lit in term.split('&&')]
        lit_num = len(term_literals)
        if term not in used_terms and literal_count + lit_num <= num_literals:
            used_terms.add(term)
            expression.append(term)
            literal_count += lit_num

    return ') || ('.join(expression), variables


# 主函数
if __name__ == "__main__":
    scales = {
        'small': (24, 5),
        'medium': (24, 5),
        'large': (24, 5)
    }

    with open("../data/expressions.txt", "w") as f:
        for label, (num_lits, num_vars) in scales.items():
            for i in range(3000):
                expr, vars_list = generate_expression_format(num_lits, num_vars)
                f.write(f"({expr})\n")
