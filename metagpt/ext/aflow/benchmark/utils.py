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


def find_same(q):

    client = OpenAI(api_key="sk-509d832659e64e73bcb61fc420bf4910", base_url="https://api.deepseek.com")
    prompt = """Compare the final answers in right_answer and model_output. Determine if they are consistent. Return only True if the answers match exactly, otherwise return False. Do not provide any explanation.
                {q}
              """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt.format(q=q)},
        ],
        stream=False
    )

    if response.choices[0].message.content == 'True':
        return True
    else:
        return False

# find_same({
#     "right_answer": "If its initial value was $x$, after Monday, its value is $.9x$, and after a further $20\\%$ loss, its value becomes $.8\\cdot .9x = .72x$, making for a total loss of $\\boxed{28\\%}$.",
#     "model_output": "Let the initial value of the stock at the beginning of Monday be \\( V \\).\n\nOn Monday, the stock loses \\( 10\\% \\) of its value. The amount lost on Monday is:\n\n\\[\n0.10 \\times V = 0.1V\n\\]\n\nThus, the value of the stock at the end of Monday is:\n\n\\[\nV - 0.1V = 0.9V\n\\]\n\nOn Tuesday, the stock loses \\( 20\\% \\) of its value at the end of Monday. The value at the end of Monday is \\( 0.9V \\), so the amount lost on Tuesday is:\n\n\\[\n0.20 \\times 0.9V = 0.18V\n\\]\n\nTherefore, the value of the stock at the end of Tuesday is:\n\n\\[\n0.9V - 0.18V = 0.72V\n\\]\n\nNow, we need to find the overall percent loss from the initial value \\( V \\) to the final value \\( 0.72V \\).\n\nThe overall loss in value is:\n\n\\[\nV - 0.72V = 0.28V\n\\]\n\nTo find the percent loss, we calculate:\n\n\\[\n\\text{Percent loss} = \\left( \\frac{\\text{Loss}}{\\text{Initial value}} \\right) \\times 100\\% = \\left( \\frac{0.28V}{V} \\right) \\times 100\\% = 28\\%\n\\]\n\nThus, the overall percent loss in value from the beginning of Monday to the end of Tuesday is:\n\n\\[\n\\boxed{28}\n\\]",
#
# })