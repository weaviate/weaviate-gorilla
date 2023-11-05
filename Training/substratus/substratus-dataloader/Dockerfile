FROM substratusai/base:latest

RUN mkdir -p /content/src /content/data
WORKDIR /content
COPY weaviate-gorilla-gql-training-dataset.jsonl /content/dataset.jsonl

CMD cp /content/dataset.jsonl /content/data/dataset.jsonl
