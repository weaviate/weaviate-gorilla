# Agentic Retrieval: A Comparison with Compound AI Systems

This study explores how well LLM systems can utilize retrieval functions through the lens of two emerging LLM system designs: Agents and Compound AI Systems.

Agents refer to a more open-ended process where an LLM is embedded in a function calling loop. At each step, the LLM is given a prompt, a list of available functions, including their respective arguments and their descriptions, as well as a working memory of information acquired thus far from the function calling loop. At each iteration the Agent decides to either call a function or complete the response.

Contrastingly, Compound AI Systems follow a pre-determined pipeline of computation to generate a response to a prompt. For example, rather than tasking the LLM with deciding whether to select a function or not in an open-ended loop, a Tool Selector System will first classify which tool is needed or output "NO TOOL NEEDED" if no tool is needed, and then will call the function and complete the response afterwards.

# 1. Create Toy Schemas

Train-Test Split on Simple and Complex Schemas

(Assume in both cases the schemas can fit in the context window)

Simple Schema = 1 Collection, 3 properties (int, text, boolean)

Complex Schema = 2 Collections, 5 properties (>=1 int, >=1 text, >=1 boolean)

# 2. Write an Inspired Query Per API

As a structured output --> how do you then ensure you get 8 APIs...?

Only way to do this is probably to loop through the APIs as well...

# 3. Write Multi-Hop Queries that require multiple APIs

Only a slightly different prompt from #2 -- double loop through APIs

# Tests

### Zero-Shot Agents vs. Zero-Shot Classifiers

Methodlogy = % Selecting the correct function

Train-Test Splits - Simple and Complex Schemas

Ablation:
- Does the task get easier with fewer APIs to choose from? (3, 5, 8)

### Optimization

Agent = Avatar, Agent Workflow Memory

Classifier = OPRO, transformers gradient descent