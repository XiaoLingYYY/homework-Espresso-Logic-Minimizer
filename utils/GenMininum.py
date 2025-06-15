# GenMininum.py
# 模块功能：利用wolfram mathematics 的功能得到最简析取式
# - 读取输入表达式文件，输出最简SOP。

WolframKernel_path = r"C:\Program Files\Wolfram Research\Mathematica\14.0\WolframKernel.exe"

origin_file = "../data/output.txt"
mini_file = "../data/minifile.txt"

from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr

if __name__ == '__main__':
    #读取文件
    print("read from " + origin_file)
    with open(origin_file, 'r') as f:
        expr_set1 = [line for line in f]
    minifile = open(mini_file,"w")
    #启动
    wf = WolframLanguageSession(WolframKernel_path)
    
    #逐个生成最短SOP 
    for i , exp in enumerate( expr_set1 , 1):
        min_result = wf.evaluate(wlexpr("ToString[BooleanMinimize[" + exp + "]]"))
        minifile.write(min_result)
        minifile.write('\n')

    minifile.close()
    wf.terminate()