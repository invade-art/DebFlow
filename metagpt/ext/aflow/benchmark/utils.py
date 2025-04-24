#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/7/24 16:37
@Author  : didi
@File    : utils.py
"""

import json
import os

import numpy as np

from metagpt.utils.common import read_json_file, write_json_file
from openai import OpenAI

def generate_random_indices(n, n_samples, test=False):
    """
    Generate random indices
    """

    def _set_seed(seed=42):
        np.random.seed(seed)

    _set_seed()
    indices = np.arange(n)
    np.random.shuffle(indices)
    if test:
        return indices[n_samples:]
    else:
        return indices[:n_samples]


def split_data_set(file_path, samples, test=False):
    data = []

    with open(file_path, "r") as file:
        for line in file:
            data.append(json.loads(line))
    random_indices = generate_random_indices(len(data), samples, test)
    data = [data[i] for i in random_indices]
    return data


def log_mismatch(problem, expected_output, prediction, predicted_number, path):
    log_data = {
        "question": problem,
        "right_answer": expected_output,
        "model_output": prediction,
        "extracted_output": predicted_number,
    }

    log_file = os.path.join(path, "log.json")

    # Check if the log file already exists
    if os.path.exists(log_file):
        # If it exists, load the existing log data
        data = read_json_file(log_file)
    else:
        # If it does not exist, create a new log list
        data = []

    # Add the new log entry
    data.append(log_data)

    # Write the data back to log.json file
    write_json_file(log_file, data, encoding="utf-8", indent=4)


async def find_same(q):

        client = OpenAI()
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
            return True
        else:
            return False


async def main():
    t = await find_same({"right_answer": "Raffaella Reggi",
        "model_output": "To answer this question, I'll compare the birth dates of Lucie Hradecká and Raffaella Reggi:\n\n1. Lucie Hradecká was born on 21 May 1985.\n2. Raffaella Reggi was born on 27 November 1965.\n\nRaffaella Reggi was born first, as her birth year (1965) is earlier than Lucie Hradecká's birth year (1985).",
        })

    print(t)

#
# import asyncio  # 需要导入 asyncio
#
# asyncio.run(main())  # 正确运行 async 函数
