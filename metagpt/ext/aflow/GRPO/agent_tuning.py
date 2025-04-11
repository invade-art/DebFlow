import torch
import torch.nn as nn


# 假设 x 是一个可学习的 embedding 向量，y 是固定文本
class LearnablePrompt(nn.Module):
    def __init__(self, x_init_text, y_fixed_text, embedding_dim=768):
        super().__init__()
        self.y_fixed = y_fixed_text  # 固定部分（字符串）

        # 将可学习的 x 初始化为 embedding 向量
        self.x_embedding = nn.Parameter(torch.randn(1, embedding_dim))  # [1, dim]

        # 可选：用预训练模型（如 GPT2）的 tokenizer 和 embedding 层
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.embedding_layer = nn.Embedding.from_pretrained("gpt2").embeddings

    def forward(self):
        # 将 x_embedding 转换为文本（通过最近邻搜索）
        x_text = self.embedding_to_text(self.x_embedding)  # 自定义函数（见下文）
        return x_text + self.y_fixed  # 拼接成完整 prompt

    def embedding_to_text(self, embedding):
        # 找到预训练 embedding 层中最接近 x_embedding 的 token
        distances = torch.norm(self.embedding_layer.weight - embedding, dim=1)
        closest_token_id = torch.argmin(distances)
        return self.tokenizer.decode(closest_token_id)


def update_prompt_x(learnable_prompt, advantages, optimizer, clip_ratio=0.2):
    """
    learnable_prompt: LearnablePrompt 实例
    advantages: 优势值 Tensor [a1, a2, a3], shape [n_workflows]
    """
    # 1. 获取当前 x 的 embedding 和生成的所有 workflows 的对数概率
    #    假设模型 M 返回 (workflows, log_probs)
    workflows, log_probs = model_M.generate(learnable_prompt())  # log_probs shape [n_workflows]

    # 2. 计算策略梯度损失（类似 PPO）
    ratios = torch.exp(log_probs - log_probs.detach())  # 概率比
    clipped_ratios = torch.clamp(ratios, 1 - clip_ratio, 1 + clip_ratio)
    loss = -torch.min(ratios * advantages, clipped_ratios * advantages).mean()

    # 3. 反向传播更新 x_embedding
    optimizer.zero_grad()
    loss.backward()
    optimizer.step() 

    # 4. （可选）约束 x_embedding 在合理范围内
    learnable_prompt.x_embedding.data = torch.clamp(learnable_prompt.x_embedding, -2, 2)



# 初始化
learnable_prompt = LearnablePrompt(
    x_init_text="Generate a workflow",  # 初始文本（仅用于初始化 embedding）
    y_fixed_text=" that must pass all tests."  # 固定部分
)
optimizer = torch.optim.Adam([learnable_prompt.x_embedding], lr=1e-3)

for epoch in range(100):
    # 生成 workflows 并测试
    prompt = learnable_prompt()  # 获取当前 prompt（x + y）
    workflows, log_probs = model_M.generate(prompt, num_workflows=3)
    test_results = [env.test(w) for w in workflows]  # 测试通过率 [0.9, 0.5, 0.7]

    # 计算优势（这里简化为通过率作为优势）
    advantages = torch.tensor(test_results, dtype=torch.float32)  # [a1, a2, a3]

    # 更新 prompt 的 x 部分
    update_prompt_x(learnable_prompt, advantages, optimizer)

    print(f"Epoch {epoch}, Prompt: {prompt}, Avg Advantage: {advantages.mean():.2f}")