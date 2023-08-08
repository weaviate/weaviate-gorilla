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
Note: It can take up to 10-20 minutes before the Server is fully
ready to start serving traffic.

You can run the following command to see the logs of the server:
```
kubectl logs deployments/llama-2-7b-weaviate-gorilla-server
```
Make sure you see a line that says:
```
start listening on 0.0.0.0:8080
```

By default the serving endpoint is only accessible from within the
Kubernetes cluster. You can change service type to LoadBalancer
to make it available over the internet by running:
```bash
kubectl patch svc llama-2-7b-weaviate-gorilla-server \
  -p '{"spec": {"type": "LoadBalancer"}}'
```

Alternatively you can use local port forwarding to the remote pod:
```
kubectl port-forward service/llama-2-7b-weaviate-gorilla-server 8080:8080
```

After port forwarding the Web UI will be accessible on [http://localhost:8080](http://localhost:8080)

You can also call the OpenAI compatible API by running:
```
curl http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{ \
    "model": "weaviate-gorilla", \
    "prompt": "REPLACE ME with your prompt template for Gorilla. Needs to match prompt template that was used for finetuning", \
    "max_tokens": 10\
  }'
```

### Cleanup
Once you're done with your testing make sure to delete the server
by running:
```
kubectl delete -f server.yaml
```

Note: If you forget to delete the Server you will be paying
for L4 GPU 24/7, which is ~$200 / month when using spot VMs.
