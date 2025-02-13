import asyncio
import time
from typing import List, Literal

from pydantic import BaseModel, Field
from torch.distributions.constraints import positive
import json
from openai import OpenAI
import time
import random

from metagpt.actions.action_node import ActionNode
from metagpt.ext.aflow.scripts.evaluator import DatasetType
from metagpt.ext.aflow.scripts.optimizer_utils.convergence_utils import ConvergenceUtils
from metagpt.ext.aflow.scripts.optimizer_utils.data_utils import DataUtils
from metagpt.ext.aflow.scripts.optimizer_utils.evaluation_utils import EvaluationUtils
from metagpt.ext.aflow.scripts.optimizer_utils.experience_utils import ExperienceUtils
from metagpt.ext.aflow.scripts.optimizer_utils.graph_utils import GraphUtils
from metagpt.logs import logger
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.ext.aflow.Debate.Debate_prompt import (
    optimizer_workflow_prompt,
    genera_output_prompt,
    neg_prompt,
    Debate_prompt,
    moderator_prompt_meta,
    moderator_prompt,
    final_judge,
    optimizer_logs_prompt,
    moderator_logs_meta,
)

key = "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"
QuestionType = Literal["math", "code", "qa"]
OptimizerType = Literal["Graph", "Test"]


class GraphOptimize(BaseModel):
    modification: str = Field(default="", description="modification")
    graph: str = Field(default="", description="graph")
    prompt: str = Field(default="", description="prompt")


class Debate:
    def __init__(self, prompt, mode, llm1, llm2, judge, optimizer, log_data, experience, score, operator_description, types, node_graph, node_prompt):
        self.prompt = prompt
        self.mode = mode
        self.llm1 = llm1
        self.llm2 = llm2
        self.judge = judge
        self.optimizer = optimizer
        self.log_data = log_data
        self.type = types
        self.affirm_memory_lst = []
        self.neg_memory_lst = []
        self.judge_memory_lst = []
        self.ini_prompt2 = optimizer_workflow_prompt.format(experience=experience,
                                                           score=score,
                                                           graph=node_graph,
                                                           prompt=node_prompt,
                                                           operator_description=operator_description,
                                                           log=self.log_data,
                                                           )
        self.ini_prompt = optimizer_logs_prompt.format(log=self.log_data)
        self.moderator_prompt_meta2 = moderator_prompt_meta.format(
                                                           graph=node_graph,
                                                           prompt=node_prompt,
                                                           )
        self.moderator_prompt_meta = moderator_logs_meta.format(log=self.log_data)
        self.mod_prompt = [{"role": "system", "content": f"{self.moderator_prompt_meta}"}]
        self.mod = {}

    async def query(self, context, llm, mode="xml_fill"):
        graph_optimize_node = await ActionNode.from_pydantic(GraphOptimize).fill(
            context=context, mode=mode, llm=llm
        )

        response = await self.optimizer.graph_utils.get_graph_optimize_response(graph_optimize_node)
        return response


    def judge_query(self,prompt):
        client = OpenAI(
            api_key=key,  # This is the default and can be omitted
        )

        chat_completion = client.chat.completions.create(
            messages=prompt,
            model="gpt-4o",
        )
        gen = chat_completion.choices[0].message.content
        return gen

    #init====
    #debate_topic=== father graph
    #positive ===prompt + neg_res
    #neg === prompt + positive
    #judge === positive + neg
    async def run(self):
        #init Debate
        positive = await self.query(self.prompt, self.llm1)
        self.affirm_memory_lst.append(positive)
        print("=====================================positive==========================")
        print(positive)
        neg_prompt_ = self.ini_prompt+neg_prompt.format(modification=positive["modification"],
                                        graph=positive["graph"],
                                        prompt=positive["prompt"],
                                        )+genera_output_prompt
        negative = await self.query(neg_prompt_, self.llm2)
        self.neg_memory_lst.append(negative)
        print('==============================================negative=================================')
        print(negative)
        mod_prompt_ = moderator_prompt.format(
            aff_modification=positive["modification"],
            aff_graph=positive["graph"],
            aff_prompt=positive["prompt"],
            neg_modification=negative["modification"],
            neg_graph=negative["graph"],
            neg_prompt=negative["prompt"],
            log=self.log_data,
        )
        self.mod_prompt.append({"role": "user", "content": mod_prompt_})
        self.mod =self.judge_query(self.mod_prompt)
        self.judge_memory_lst.append(self.mod)
        self.mod_prompt.pop()
        print('++++++++++++++++++++++++++++++++++++++++++++++++mod++++++++++++++++++++++++++++++++++++++')
        print(self.mod)

        for i in range(2):
            if self.mod != 'No':
                if self.mod == 'affirmative':
                    return self.affirm_memory_lst[-1]
                else:
                    return self.neg_memory_lst[-1]
            else:
                pos_prompt =self.ini_prompt+Debate_prompt.format(
                    modification = self.neg_memory_lst[-1]["modification"],
                    graph = self.neg_memory_lst[-1]["graph"],
                    prompt = self.neg_memory_lst[-1]["prompt"],
                )+genera_output_prompt
                positive = await self.query(pos_prompt, self.llm1)
                self.affirm_memory_lst.append(positive)
                print("=====================================positive==========================")
                print(positive)


                neg_prompt_ = self.ini_prompt +Debate_prompt.format(
                    modification = self.affirm_memory_lst[-1]["modification"],
                    graph = self.affirm_memory_lst[-1]["graph"],
                    prompt = self.affirm_memory_lst[-1]["prompt"],
                ) + genera_output_prompt
                negative = await self.query(neg_prompt_, self.llm2)
                self.neg_memory_lst.append(negative)
                print('==============================================negative=================================')
                print(negative)

                mod_prompt_ = moderator_prompt.format(
                    aff_modification=positive["modification"],
                    aff_graph=positive["graph"],
                    aff_prompt=positive["prompt"],
                    neg_modification=negative["modification"],
                    neg_graph=negative["graph"],
                    neg_prompt=negative["prompt"],
                    log=self.log_data
                )
                self.mod_prompt.append({"role": "user", "content": mod_prompt_})
                self.mod = self.judge_query(self.mod_prompt)
                self.judge_memory_lst.append(self.mod)
                self.mod_prompt.pop()
                print('++++++++++++++++++++++++++++++++++++++++++++++++mod++++++++++++++++++++++++++++++++++++++')
                print(self.mod)

        mod_prompt_ = final_judge.format(
            aff_modification=self.affirm_memory_lst[-1]["modification"],
            aff_graph=self.affirm_memory_lst[-1]["graph"],
            aff_prompt=self.affirm_memory_lst[-1]["prompt"],
            neg_modification=self.neg_memory_lst[-1]["modification"],
            neg_graph=self.neg_memory_lst[-1]["graph"],
            neg_prompt=self.neg_memory_lst[-1]["prompt"],
        )
        self.mod_prompt.append({"role": "user", "content": mod_prompt_})
        self.mod = self.judge_query(self.mod_prompt)
        self.judge_memory_lst.append(self.mod)
        self.mod_prompt.pop()
        print('++++++++++++++++++++++++++++++++++++++++++++++++mod++++++++++++++++++++++++++++++++++++++')
        print(self.mod)
        if self.mod == 'affirmative':
            return self.affirm_memory_lst[-1]
        else:
            return self.neg_memory_lst[-1]