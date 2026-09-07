import math

import torch
import torch.nn.functional as F

torch.set_printoptions(precision=4, sci_mode=False)


def layer_norm(x: torch.Tensor) -> torch.Tensor:
    return F.layer_norm(x, normalized_shape=(x.shape[-1],))


def print_attention_table(tokens: list[str], weights: torch.Tensor) -> None:
    print("\nWho attends to whom?")
    for i, token in enumerate(tokens):
        print(f"\n{token}:")
        for j, other_token in enumerate(tokens):
            print(f"  {other_token}: {weights[i, j].item():.4f}")


text = "I love cats"
tokens = text.split()

print("We will build one small Transformer encoder block for:")
print(tokens)


# 1. Token embeddings + positional embeddings
#    In a real model, these are learned. Here we keep them fixed so the math is easy to follow.
token_embeddings = torch.tensor(
    [
        [1.0, 0.0, 1.0, 0.0],  # I
        [0.0, 2.0, 0.0, 1.0],  # love
        [1.0, 1.0, 1.0, 1.0],  # cats
    ],
    dtype=torch.float32,
)

position_embeddings = torch.tensor(
    [
        [0.1, 0.0, 0.0, 0.0],
        [0.0, 0.1, 0.0, 0.0],
        [0.0, 0.0, 0.1, 0.0],
    ],
    dtype=torch.float32,
)

x = token_embeddings + position_embeddings

print("\n1) Token embeddings:")
print(token_embeddings)
print("\n2) Positional embeddings:")
print(position_embeddings)
print("\n3) Transformer input = token embeddings + positional embeddings:")
print(x)


# 2. Self-attention projections
#    Q, K, and V are learned linear projections in a real transformer.
d_model = x.shape[-1]
W_Q = torch.eye(d_model)
W_K = torch.eye(d_model)
W_V = torch.tensor(
    [
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.0],
    ],
    dtype=torch.float32,
)
W_O = torch.eye(d_model)

q = x @ W_Q
k = x @ W_K
v = x @ W_V

scores = (q @ k.T) / math.sqrt(d_model)
attention_weights = F.softmax(scores, dim=-1)
attention_context = attention_weights @ v
attention_output = attention_context @ W_O

print("\n4) Q, K, and V:")
print("Q:")
print(q)
print("\nK:")
print(k)
print("\nV:")
print(v)

print("\n5) Attention scores:")
print(scores)
print("\n6) Attention weights:")
print(attention_weights)
print("\nRow sums:")
print(attention_weights.sum(dim=-1))
print("\n7) Attention output:")
print(attention_output)

print_attention_table(tokens, attention_weights)


# 3. Residual connection + layer norm
residual_1 = x + attention_output
norm_1 = layer_norm(residual_1)

print("\n8) Residual connection after attention:")
print(residual_1)
print("\n9) Layer norm after attention:")
print(norm_1)


# 4. Feed-forward network
#    This is the second major sublayer in a transformer block.
W_1 = torch.tensor(
    [
        [1.0, 0.0, 0.5, 0.0, 0.0, 0.5, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.5, 1.0, 0.0, 0.0, 0.5],
        [0.5, 1.0, 0.0, 0.0, 0.5, 0.0, 1.0, 0.0],
        [0.0, 0.5, 1.0, 1.0, 0.0, 0.5, 0.0, 1.0],
    ],
    dtype=torch.float32,
)

W_2 = torch.tensor(
    [
        [1.0, 0.0, 0.5, 0.0],
        [0.0, 1.0, 0.0, 0.5],
        [0.5, 0.0, 1.0, 0.0],
        [0.0, 0.5, 0.0, 1.0],
        [0.5, 0.5, 0.0, 0.0],
        [0.0, 0.0, 0.5, 0.5],
        [1.0, 0.0, 0.0, 1.0],
        [0.0, 1.0, 1.0, 0.0],
    ],
    dtype=torch.float32,
)

b_1 = torch.zeros(8)
b_2 = torch.zeros(d_model)

ff_hidden = F.relu(norm_1 @ W_1 + b_1)
ff_output = ff_hidden @ W_2 + b_2

print("\n10) Feed-forward hidden layer:")
print(ff_hidden)
print("\n11) Feed-forward output:")
print(ff_output)


# 5. Final residual + layer norm
residual_2 = norm_1 + ff_output
final_output = layer_norm(residual_2)

print("\n12) Residual connection after feed-forward:")
print(residual_2)
print("\n13) Final transformer block output:")
print(final_output)

print("\nInterview summary:")
print("A transformer block = embeddings + positional information -> self-attention -> residual + layer norm -> feed-forward -> residual + layer norm.")
print("The attention weights decide which tokens talk to which other tokens.")