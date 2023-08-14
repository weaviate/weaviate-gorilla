# Weaviate Gorilla
Fine-tuned LLMs to use the Weaviate APIs!

Here is a quick quide to our repo!
<ul>
  <li>selfInstruct: contains the code to generate training data where Weaviate APIs are formatted for toy schemas. The Weaviate API reference data can be found here as well as the 3 engines for query generation: the initEngine, validator, and retryEngine.</li>
  <li>substratus: contains the code to use the substratus system for training and serving models with kubernetes!</li>
  <li>data: contains the datasets generated from selfInstruct and used for training with substratus.</li>
</ul>
