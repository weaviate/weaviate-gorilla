# This folder contains old code from Weaviate Gorilla Part 1: GraphQL

You can check out our original blog post [here](https://weaviate.io/blog/weaviate-gorilla-part-1)!

# `Auto` API Repo

One of the most powerful ways to enhance the abilities of Large Language Models is to connect them with external tools! External tools describe things such as calculators, code executors, databases, and more! In order for LLMs to use tools, they need to have the right interface to the tool's APIs. For simple tools such as calculators, this can often be fit in a single JSON dictionary, but for more complex tools the Gorilla framework has shown that Retrieval-Aware fine-tuning is much more effective. `Auto` is a Database Agent that has been fine-tuned on Weaviate's APIs! This repo open-sources the code behind training `Auto`, such as generating synthetic data, as well as training and evaluating LLMs.

The `Auto` API project has began with text-to-GraphQL translation. <br />
-> The code for developing these models can be found under `Gorilla`.

Please see the following GH issue to see and comment on the latest development of `Auto` in Weaviate: https://github.com/weaviate/weaviate/issues/3289.

![Weaviate Gorilla](../visuals/weaviate-gorillas/gorilla-58.png)
