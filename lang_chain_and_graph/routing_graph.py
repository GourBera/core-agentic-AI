from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    input: str
    action: Literal["reverse", "upper"]
    output: str


workflow = StateGraph(State)

def node_a(state: State):
    print("Node A\n")
    output =  state['input'][::-1]
    print(f"output: {output}")
    return {"output": output}

def node_b(state: State):
    print("Node B\n")
    output = state['input'].upper()
    print(f"output: {output}")
    return {"output": output}

workflow.add_node(node_a)
workflow.add_node(node_b)

def routing_function(state: State):
    action = state["action"]
    if action == "reverse":
        return "node_a"
    if action == "upper":
        return "node_b"        

workflow.add_conditional_edges(
    source=START, 
    path=routing_function, 
    path_map=["node_a", "node_b"]
)

workflow.add_edge("node_a", END)
workflow.add_edge("node_b", END)

graph = workflow.compile()

print(graph.get_graph().draw_ascii())

graph.invoke(
    input = {
        "input": "Some input",
        "action": "upper",
    }, 
)

graph.invoke(
    input = {
        "input": "Some input",
        "action": "reverse",
    }, 
)

