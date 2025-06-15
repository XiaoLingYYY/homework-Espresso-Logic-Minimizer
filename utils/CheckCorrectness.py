# CheckCorrectness.py
# 模块功能：利用wolfram mathematics 的功能判断
# - 负责读取espresso的输入输出文件，判断正确率。

WolframKernel_path = r"C:\Program Files\Wolfram Research\Mathematica\14.0\WolframKernel.exe"
origin_file = "../data/expressions.txt"
out_file = "../data/output.txt"

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr

if __name__ == '__main__':

    # 读取文件,全部转成 wlexpr
    with open(origin_file, 'r') as f:
        expr_set1 = [wlexpr(line) for line in f]

    with open(out_file, 'r') as f:
        expr_set2 = [wlexpr(line) for line in f]
    print(f"read file {origin_file}  <=>  {out_file}")

    # 启动wolfram
    wf = WolframLanguageSession(WolframKernel_path)

    total_cases = len(expr_set1)
    correct_cases = 0

    # 逐个判断是否等价
    for i, (e1, e2) in enumerate(zip(expr_set1, expr_set2), 1):
        correct = wf.evaluate(
            wl.TautologyQ(wl.Equivalent(e1, e2))
        )
        if correct:
            correct_cases += 1
        else:
            print(f"Wrong case detected at index: {i} \n " + wf.evaluate(wl.ToString(e1)) + "\n<=/+=>\n" + wf.evaluate(
                wl.ToString(e2)))

    print(f"正确率：{correct_cases}/{total_cases}")
    wf.terminate()
