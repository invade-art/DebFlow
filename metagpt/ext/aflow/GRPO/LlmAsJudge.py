import asyncio
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Tuple

import aiofiles
import pandas as pd
from tqdm.asyncio import tqdm_asyncio
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from openai import OpenAI


# 异步获得output
@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
async def generate_output_with_retry(graph, input_text):
    return await graph(input_text)

# 用workflow获得输出
async def evaluate_problem(problem, graph):
    input_text = problem["problem"]
    expected_output = problem["solution"]

    output = await generate_output_with_retry(graph, input_text)

    return input_text, output, expected_output

# 评估每一个问题
async def evaluate_all_problems(data, graph):
    semaphore = asyncio.Semaphore(50)

    async def sem_evaluate(problem):
        async with semaphore:
            return await evaluate_problem(problem, graph)

    tasks = [sem_evaluate(problem) for problem in data]
    return await tqdm_asyncio.gather(*tasks, desc=f"Evaluating problems", total=len(data))

# 获得workflow的执行结果
async def graph_evaluate(datasets, graph, params):
    """
    datasets:str
    graph: class
    params:dict
    """

    # 实例化workflow
    dataset_config = params.get("dataset", {})
    llm_config = params.get("llm_config", {})
    workflow =  graph(name=datasets, llm_config=llm_config, dataset=dataset_config)

    # list[tuple, tuple]
    results = await evaluate_all_problems(datasets, workflow)
    columns = ['input_text', 'output', 'expected_output']
    # 将结果保存一下
    df = pd.DataFrame(results, columns=columns)
    filename = f"workflow_results.csv"
    output_file = os.path.join('./workflow_results', filename)
    df.to_csv(output_file, index=False)

    return results

async def judge(results):
    rewards = [0] * len(results)

    async def find_same(q):

        client = OpenAI(
            api_key="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",
            base_url="https://api.openai.com/v1")
        prompt = """Compare the final answers in right_answer and model_output. Ignore any additional explanations or reasoning in model_output. 
                    If the final answer in model_output is logically consistent with right_answer, return only True. Otherwise, return False. 
                    Do not provide any explanation.
                    {q}
                  """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt.format(q=q)},
            ],
            stream=False
        )

        if response.choices[0].message.content == 'True':
            return 1
        else:
            return 0
    # tuple
    for quest, output, expecte in results:
        q = {
            "right_answer": expecte,
            "model_output": output
        }
        rewards.append(await find_same(q))

    return rewards

# rewards function
# 要求输出[int, int, int, int],n*m == n是样本数，m是rewards值
async def LlmAaJudge(prompt, completions, **kwargs):
    # 每种数据类不一样的好像不能进行统一的rewards

    # list[tuple, tuple]
    results = await graph_evaluate(prompt, completions)

    rewards = await judge(results)

    return rewards