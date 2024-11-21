# Related Works

## LLM Tool Use

Tool use is one of the most promising opportunities to improve the capabilities of LLMs. There are two common design patterns for interfacing tool use in these systems: agentic function calling and flow engineering. Agentic function calling entails equipping the LLM with a set of functions described in the prompt. The LLM inference is then orchestrated in a function calling loop. At each step the LLM either chooses to complete the response, or call one or multiple functions and wait for their respective responses to continue the next iteration of the loop. Contrastively, flow engineering describes a pre-determined flow of inferences and external tools calls. This abstraction helps clarify how tools are interfaced to LLMs. However, there is a significant overlap and this is a constantly evolving area of AI research. For example, an engineered LLM and tool calling flow could be itself abstracted and interfaced as a function for the agent to call. In a similar analog, a flow could implement the open-ended looping core to the definition of an agent. Understanding these distinctions is important for the evolution of prior works on interfacing search and database querying as an LLM tool.

Gorilla
Structured Outputs

## Search as a Tool

Search has been one of the most commonly used tools for LLMs. Most commonly, this has taken the shape of RAG, a flow of retrieval with the user input as query, followed by response generation. RAG flows were further pioneered with architectures such as Baleen RAG, in which the user input is first translated into search queries with an LLM inference, sent to a retrieval engine, and passed into a final response generation. One of the early efforts to expand search to the agentic function calling interface was WebGPT, in which the LLM can format search queries to send to the web, as well as paginate through the results. Zhang et al. debuted the term “Agentic Information Retrieval” to capture the intersection of learning to search with the agent function calling interface.

## Database as a Tool

Developing mostly in parallel to search as a tool, AI researchers and practitioners have been exploring the use of database APIs as a tool. Even before breakthrough capabilities in LLMs, Text-to-SQL research has been a heavily studied discipline. Text-to-SQL research has mostly targeted the application of making it easier for humans to learn how to query databases. Now that most databases are evolving to support search indexes and integration with LLMs, additional query languages are emerging to expand SQL. [LOTUS is this]. [SUQL is this].

LOTUS, SUQL

In order to study machine learning for databases, we need new benchmarks and datasets reflective of the challenges of database systems. [Database Gyms are this]. [We generate schemas]. Future - [Lakehouses are this]. [Ontologies are this].

Database Gyms and Self-Instruct
Lakehouses and Ontologies

# Bibliography

## LLM Tool Use
1. Gorilla: Large Language Model Connected with Massive APIs. Shishir G. Patil, Tianjun Zhang, Xin Wang, Joseph E. Gonzalez. 2023. [Arxiv Link](https://arxiv.org/abs/2305.15334)
2. Toolformer: Language Models Can Teach Themselves to use Tools. Timo Schick, Jane Dwivedi-Yu, Roberto Dessi, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Niccola Cancedda, Thomas Scialom. 2023. [Arxiv link](https://arxiv.org/abs/2302.04761)
3. AvaTaR: Optimizing LLM Agents for Tool-Assisted Knowledge Retrieval. Shirley Wu, Shiyu Zhao, Qian Huang, Kexin Huang, Michihiro Yasunaga, Kaidi Cao, Vassilis N. Ioannidis, Karthik Subbian, Jure Leskovec, James Zou. 2024. [Arxiv Link](https://arxiv.org/pdf/2406.11200)
4. Agentic Information Retrieval. Weinan Zhang, Junwei Liao, Ning Li, Kounianhua Du. 2024. [Arxiv Link](https://arxiv.org/abs/2410.09713)
5. WebGPT: Browser-assisted question-answering with human feedback. Reiichiro Nakano et al. 2021. [Arxiv Link](https://arxiv.org/abs/2112.09332)
6. Code Generation with AlphaCodium: From Prompt Engineering to Flow Engineering. Tal Ridnik, Dedy Kredo, Itamar Friedman. 2024. [Arxiv Link](https://arxiv.org/abs/2401.08500)
7. DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines. Omar Khattab et al. 2023. [Arxiv Link](https://arxiv.org/abs/2310.03714)
8. Agent Workflow Memory. Zora Zhiruo Wang, Jiayuan Mao, Daniel Fried, Graham Neubig. 2024. [Arxiv Link](https://arxiv.org/abs/2409.07429)

## Synthetic Data Creation
9. Self-Instruct: Aligning Language Models with Self-Generated Instructions. Yizhong Wang, Yeganeh Kordi, Swaroop Mishra, Alisa Liu, Noah A. Smith, Daniel Khashabi, Hannaneh Hajishirzi. 2023. [Arxiv Link](https://arxiv.org/abs/2212.10560)

## Database API Testing
10. Database Gyms. Wan Shen Lim, Matthew Butrovich, William Zhang, Andrew Crotty, Lin Ma, Peijing Xu, Johannes Gehrke, Andrew Pavlo. 2023. [Brown University](https://cs.brown.edu/people/acrotty/pubs/p27-lim.pdf).
11. Hit the Gym: Accelerating Query Execution to Efficiently Bootstrap Behavior Models for Self-Driving Database Management Systems. Wan Shen Lim, Lin Ma, William Zhang, Matthew Buttrovich, Samuel Arch, Andrew Pavlo. 2024. [CMU](https://www.pdl.cmu.edu/PDL-FTP/Database/p3680-lim.pdf)
12. Make Your Database System Dream of Electric Sheep: Towards Self-Driving Operation. Andrew Pavlo, Matthew Butrovich, Lin Ma, Prashanth Menon, Wan Shen Lim, Dan Van Aken, William Zhang. 2021. [NSF](https://par.nsf.gov/servlets/purl/10312181)
13. LLM as DBA. Xuanhe Zhou, Guoliang Li, Zhiyuan Liu. 2023. [Arxiv Link](https://arxiv.org/abs/2308.05481)

## Advanced Database Schemas
14. Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics. Michael Armbrust, Ali Ghodsi, Reynold Xin, Matei Zaharia. 2021. [Semantic Scholar](https://www.semanticscholar.org/paper/Lakehouse%3A-A-New-Generation-of-Open-Platforms-that-Zaharia-Ghodsi/451cf5fc9786ed4f7e1d9877f08d00f8b1262121)
15. Bringing semantic knowledge graph technology to your data. Bob van Luijt and Micha Verhagen. 2020. [IEEE](https://ieeexplore.ieee.org/abstract/document/8994851)

## Text-to-SQL
16. BIRD-SQL
17. LOTUS: Enabling Semantic Queries with LLMs Over Tables of Unstructured and Structured Data. Liana Patel, Siddharth Jha, Carlos Guestrin, Matei Zaharia. 2024. [Arxiv Link](https://arxiv.org/abs/2407.11418)
18. SUQL: Conversational Search over Structured and Unstructured Data with Large Language Models. Shicheng Liu, Jialiang Xu, Wesley Tjangnaka, Sina J. Semnani, Chen Jie Yu, Monica S. Lam. 2023. [Arxiv Link](https://arxiv.org/abs/2311.09818)

## Structured Outputs
19. Efficient Guided Generation for Large Language Models. Brandon T. Willard, Remi Louf. 2023. [Arxiv Link](https://arxiv.org/abs/2307.09702)
20. StructuredRAG: JSON Response Formatting with Large Language Models. Connor Shorten, Charles Pierse, Thomas Benjamin Smith, Erika Cardenas, Akanksha Sharma, John Trengrove, Bob van Luijt. 2024. [Arxiv Link](https://arxiv.org/abs/2408.11061)

## Query Writing
21. Baleen: Robust Multi-Hop Reasoning at Scale via Condensed Retrieval. Omar Khattab, Christopher Potts, Matei Zaharia. 2022. [Arxiv Link](https://arxiv.org/abs/2101.00436)
22. Decomposing Complex Queries for Tip-of-the-tongue Retrieval. Kevin Lin, Kyle Lo, Joseph E. Gonzalez, Dan Klein. 2023. [Arxiv Link](https://arxiv.org/abs/2305.15053)
23. Grounding by Trying: LLMs with Reinforcement Learning-Enhanced Retrieval. Sheryl Hsu, Omar Khattab, Chelsea Finn, Archit Sharma. 2024. [Arxiv Link](https://arxiv.org/pdf/2410.23214?)

==
<br />
Compound AI Systems
<br />
Retrieval-Augmented Generation
<br />
GPT-4
