import os
import json
import asyncio
import importlib.util
from metagpt.configs.models_config import ModelsConfig

# 动态加载模块
def load_class_from_file(file_path, class_name):
    spec = importlib.util.spec_from_file_location("dynamic_module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 从模块中获取类
    cls = getattr(module, class_name)
    return cls

#找到最佳workflow
def find_workflow(dirs):
    max_after_value = float('-inf')
    graph = ''
    rou = ''
    for sub in os.listdir(dirs):
        round_x = os.path.join(dirs, sub)
        if os.path.isdir(round_x):
            experience = os.path.join(round_x, "experience.json")

            if os.path.isfile(experience):
                try:
                    with open(experience, "r") as f:
                        data = json.load(f)
                    after_value = data.get("after")
                    if after_value is not None and isinstance(after_value, (int, float)):
                        if after_value > max_after_value:
                            max_after_value = after_value
                            graph_path = os.path.join(round_x, 'graph.py')
                            graph = load_class_from_file(graph_path, 'Workflow')
                            rou = round_x
                except (json.JSONDecodeError, IOError) as e:
                    print(e)
    print(f'===============================================================================best_round is {rou}====================================')
    return graph, max_after_value


#选择类型以及读取workflow
def find_best_workflow(types):
    graph = ''
    score = ''
    if types=='math':
        dirs = "metagpt/ext/aflow/scripts/optimized/MATH/workflows"
        graph, score = find_workflow(dirs)
    elif types=='code':
        dirs = "metagpt/ext/aflow/scripts/optimized/MBPP/workflows"
        graph, score = find_workflow(dirs)
    else:
        dirs = "metagpt/ext/aflow/scripts/optimized/HotpotQA/workflows"
        graph, score = find_workflow(dirs)
    models_config = ModelsConfig.default()
    opt_llm_config1 = models_config.get("gpt-4o-mini")
    return graph(name='workflow', llm_config=opt_llm_config1, dataset = types), score


async def Debate_aflow(query, relevant, types):
    #选择最佳的workflow
    graph, score = find_best_workflow(types)
    inputs = query
    if relevant is not None:
        inputs = f"Context: {relevant}\n\nQuestion: {query}\n\nAnswer:"
    outputs = await graph(inputs)

    return outputs


# if __name__ == '__main__':
#     ans = asyncio.run(Debate_aflow('2024年春节期间去哪里旅游性价比最高', None, 'qa'))
#     #math,qa code。