# Gorilla 🦍
Fine-tuned LLMs to use the Weaviate APIs!

## Setup dev env

Create venv
```
make install
```

Source the venv:
```
source .venv/bin/activate
```

## Serve the finetuned model in Substratus

You need to run this to create a serving endpoint:
```
kubectl apply -f server.yaml
```

By default the serving endpoint is only accessible from within the
Kubernetes cluster. You can change service type to LoadBalancer
to make it available over the internet by running:
```bash
kubectl patch svc llama-2-7b-weaviate-gorilla-server \
  -p '{"spec": {"type": "LoadBalancer"}}'
```

Once you're done with your testing make sure to delete the server
by running:
```
kubectl delete -f server.yaml
```

Note: If you forget to delete the server you will be paying
for L4 GPU non-stop.
