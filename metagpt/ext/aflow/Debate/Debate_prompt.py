WORKFLOW_INPUT = """
Here is a graph and the corresponding prompt (prompt only related to the custom method) that performed excellently in a previous iteration (maximum score is 1). You must make further optimizations and improvements based on this graph. The modified graph must differ from the provided example, and the specific differences should be noted within the <modification>xxx</modification> section.\n
<sample>
    <experience>{experience}</experience>
    <modification>(such as:add a review step/delete a operator/modify a prompt)</modification>
    <score>{score}</score>
    <graph>{graph}</graph>
    <prompt>{prompt}</prompt>(only prompt_custom)
    <operator_description>{operator_description}</operator_description>
</sample>
Below are the logs of some results with the aforementioned Graph that performed well but encountered errors, which can be used as references for optimization:
{log}

First, provide optimization ideas. **Only one detail point can be modified at a time**, and no more than 5 lines of code may be changed per modification—extensive modifications are strictly prohibited to maintain project focus!
When introducing new functionalities in the graph, please make sure to import the necessary libraries or modules yourself, except for operator, prompt_custom, create_llm_instance, and CostManage, which have already been automatically imported.
**Under no circumstances should Graph output None for any field.**
Use custom methods to restrict your output format, rather than using code (outside of the code, the system will extract answers based on certain rules and score them).
It is very important to format the Graph output answers, you can refer to the standard answer format in the log.
"""


WORKFLOW_CUSTOM_USE = """\nHere's an example of using the `custom` method in graph:
```
# You can write your own prompt in <prompt>prompt_custom</prompt> and then use it in the Custom method in the graph
response = await self.custom(input=problem, instruction=prompt_custom.XXX_PROMPT)
# You can also concatenate previously generated string results in the input to provide more comprehensive contextual information.
# response = await self.custom(input=problem+f"xxx:{xxx}, xxx:{xxx}", instruction=prompt_custom.XXX_PROMPT)
# The output from the Custom method can be placed anywhere you need it, as shown in the example below
solution = await self.generate(problem=f"question:{problem}, xxx:{response['response']}")
```
Note: In custom, the input and instruction are directly concatenated(instruction+input), and placeholders are not supported. Please ensure to add comments and handle the concatenation externally.\n

**Introducing multiple operators at appropriate points can enhance performance. If you find that some provided operators are not yet used in the graph, try incorporating them.**
"""


WORKFLOW_OPTIMIZE_PROMPT = """You are building a Graph and corresponding Prompt to jointly solve {type} problems. 
Referring to the given graph and prompt, which forms a basic example of a {type} solution approach, 
please reconstruct and optimize them. You can add, modify, or delete nodes, parameters, or prompts. Include your 
single modification in XML tags in your reply. Ensure they are complete and correct to avoid runtime failures. When 
optimizing, you can incorporate critical thinking methods like review, revise, ensemble (generating multiple answers through different/similar prompts, then voting/integrating/checking the majority to obtain a final answer), selfAsk, etc. Consider 
Python's loops (for, while, list comprehensions), conditional statements (if-elif-else, ternary operators), 
or machine learning techniques (e.g., linear regression, decision trees, neural networks, clustering). The graph 
complexity should not exceed 10. Use logical and control flow (IF-ELSE, loops) for a more enhanced graphical 
representation.Ensure that all the prompts required by the current graph from prompt_custom are included.Exclude any other prompts.
Output the modified graph and all the necessary Prompts in prompt_custom (if needed).
The prompt you need to generate is only the one used in `prompt_custom.XXX` within Custom. Other methods already have built-in prompts and are prohibited from being generated. Only generate those needed for use in `prompt_custom`; please remove any unused prompts in prompt_custom.
the generated prompt must not contain any placeholders.
Considering information loss, complex graphs may yield better results, but insufficient information transmission can omit the solution. It's crucial to include necessary context during the process."""

optimizer_workflow_prompt = """You are a debater. Hello and welcome to the debate. It's not necessary to fully agree with each other's perspectives, as our objective is to find the correct answer.
The debate topic is how to optimize the Graph and corresponding Prompt. The initial graph and corresponding prompt as follow:
<initial>
    <experience>{experience}</experience>
    <modification>(such as:add a review step/delete a operator/modify a prompt)</modification>
    <score>{score}</score>
    <graph>{graph}</graph>
    <prompt>{prompt}</prompt>(only prompt_custom)
    <operator_description>{operator_description}</operator_description>
</initial>

Below are the logs of some results with the aforementioned Graph that performed well but encountered errors, which can be used as references for optimization:
{log}

It is very important to format the Graph output answers, you can refer to the standard answer format in the log.
"""

optimizer_logs_prompt = """You are a debater. Hello and welcome to the debate. It's not necessary to fully agree with each other's perspectives, as our objective is to find the correct answer.
The debate topic is how to optimize the Graph and corresponding Prompt. You should analyze log data and come up with an optimization plan.

Below are the logs of some results with the aforementioned Graph that performed well but encountered errors, which can be used as references for optimization:
{log}

It is very important to format the Graph output answers, you can refer to the standard answer format in the log.
"""


genera_output_prompt = """
First, provide optimization ideas. **Only one detail point can be modified at a time**, and no more than 5 lines of code may be changed per modification—extensive modifications are strictly prohibited to maintain project focus!
When introducing new functionalities in the graph, please make sure to import the necessary libraries or modules yourself, except for operator, prompt_custom, create_llm_instance, and CostManage, which have already been automatically imported.
**Under no circumstances should Graph output None for any field.**
Use custom methods to restrict your output format, rather than using code (outside of the code, the system will extract answers based on certain rules and score them).
It is very important to format the Graph output answers, you can refer to the standard answer format in the log.

Here's an example of using the `custom` method in graph:
```
# You can write your own prompt in <prompt>prompt_custom</prompt> and then use it in the Custom method in the graph
response = await self.custom(input=problem, instruction=prompt_custom.XXX_PROMPT)
# You can also concatenate previously generated string results in the input to provide more comprehensive contextual information.
# response = await self.custom(input=problem+f"xxx:{xxx}, xxx:{xxx}", instruction=prompt_custom.XXX_PROMPT)
# The output from the Custom method can be placed anywhere you need it, as shown in the example below
solution = await self.generate(problem=f"question:{problem}, xxx:{response['response']}")
```
Note: In custom, the input and instruction are directly concatenated(instruction+input), and placeholders are not supported. Please ensure to add comments and handle the concatenation externally.\n

**Introducing multiple operators at appropriate points can enhance performance. If you find that some provided operators are not yet used in the graph, try incorporating them. Be careful not to import operators that are not included in the operator, otherwise the program will fail.**

please reconstruct and optimize them. You can add, modify, or delete nodes, parameters, or prompts. Include your single modification in XML tags in your reply. Ensure they are complete and correct to avoid runtime failures.
When optimizing, you can incorporate critical thinking methods like review, revise, ensemble (generating multiple answers through different/similar prompts, then voting/integrating/checking the majority to obtain a final answer), selfAsk, etc. Consider 
Python's loops (for, while, list comprehensions), conditional statements (if-elif-else, ternary operators), 
or machine learning techniques (e.g., linear regression, decision trees, neural networks, clustering). The graph 
complexity should not exceed 10. Use logical and control flow (IF-ELSE, loops) for a more enhanced graphical 
representation.Ensure that all the prompts required by the current graph from prompt_custom are included.Exclude any other prompts.
Output the modified graph and all the necessary Prompts in prompt_custom (if needed).
The prompt you need to generate is only the one used in `prompt_custom.XXX` within Custom. Other methods already have built-in prompts and are prohibited from being generated. Only generate those needed for use in `prompt_custom`; please remove any unused prompts in prompt_custom.
the generated prompt must not contain any placeholders.
Considering information loss, complex graphs may yield better results, but insufficient information transmission can omit the solution. It's crucial to include necessary context during the process.
"""

neg_prompt = """
Below is my answer based on the initial graph and prompt, You disagree with my answer. You have to consider whether my answer can solve the problems in the logs
You must make further optimizations and improvements based on this graph. The modified graph must differ from the provided example, and the specific differences should be noted within the <modification>xxx</modification> section.
<sample>
    <modification>{modification}</modification>
    <graph>{graph}</graph>
    <prompt>{prompt}</prompt>(only prompt_custom)
</sample>
"""

Debate_prompt ="""
Below is my answer based on the initial graph and prompt. Do you agree with my perspective? You have to consider whether my answer can solve the problems in the logs.
You must make further optimizations and improvements based on this graph. The modified graph must differ from the provided example, and the specific differences should be noted within the <modification>xxx</modification> section.
<sample>
    <modification>{modification}</modification>
    <graph>{graph}</graph>
    <prompt>{prompt}</prompt>(only prompt_custom)
</sample>
"""

moderator_prompt_meta = """
You are a moderator. There will be two debaters involved in a debate. 
They will present their answers and discuss their perspectives on the following topic: 
The debate topic is how to optimize the Graph and corresponding Prompt.
<initial>
    <graph>{graph}</graph>
    <prompt>{prompt}</prompt>
</initial>

At the end of each round, you will evaluate answers and decide which is correct.
"""

moderator_logs_meta = """
You are a moderator. There will be two debaters involved in a debate. 
They will present their answers and discuss their perspectives on the following topic: 
The debate topic is how to optimize the Graph and corresponding Prompt.

Below are the logs of some results with the aforementioned Graph that performed well but encountered errors, which can be used as references for optimization:
{log}

At the end of each round, you will evaluate answers and decide which is correct.
"""

moderator_prompt = """
Now the round of debate for both sides has ended.
You have to consider which side of the workflow will not have problems in the logs after execution.

Affirmative side arguing:
<aff_ans>
    <modification>{aff_modification}</modification>
    <graph>{aff_graph}</graph>
    <prompt>{aff_prompt}</prompt>
</aff_ans>

Negative side arguing: 
<neg_ans>
    <modification>{neg_modification}</modification>
    <graph>{neg_graph}</graph>
    <prompt>{neg_prompt}</prompt>
</neg_ans>

You, as the moderator, will evaluate both sides' answers and determine if there is a clear preference for an answer candidate. If so, please output your supporting 'affirmative' or 'negative' side and give the final answer that you think is correct, and the debate will conclude. If not, just output 'No', the debate will continue to the next round.
for examples: 'affirmative' , 'negative', 'No'
"""

x = 'Now please output your answer in json format, with the format as follows:  {\"preference\": \"Yes or No\", \"Supported Side\": \"Affirmative or Negative\", \"Reason\": \"\"}. Please strictly output in JSON format, do not output irrelevant content.Please strictly output your answer in JSON format with no additional text.'

final_judge = """
Now the round of debate for both sides has ended.
You have to consider which side of the workflow will not have problems in the logs after execution.
Affirmative side arguing:
<aff_ans>
    <modification>{aff_modification}</modification>
    <graph>{aff_graph}</graph>
    <prompt>{aff_prompt}</prompt>
</aff_ans>

Negative side arguing: 
<neg_ans>
    <modification>{neg_modification}</modification>
    <graph>{neg_graph}</graph>
    <prompt>{neg_prompt}</prompt>
</neg_ans>

As a judge, the current round has ended. You must choose one of the affirmative and negative as your final choice. Please base your judgment on the original graph and the revisions of both affirmative and negative.
If you choose affirmative, please output 'affirmative'. If you choose negative, please output 'negative'.
for examples: 'affirmative' , 'negative'

Please strictly output format, do not output irrelevant content.
"""