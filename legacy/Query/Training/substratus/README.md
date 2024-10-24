# Weaviate Gorilla Substratus instructions
Fine-tuned LLMs to use the Weaviate APIs! Substratus
is used to serve and finetune Weaviate Gorilla.

## Finetuning Weaviate Gorilla

### Load the dataset

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
## Accessing the serving endpoint
By default the serving endpoint is only accessible from within the
Kubernetes cluster.

### Option 1: Expose on the internet
You can change service type to LoadBalancer
to make it available over the internet by running:
```bash
kubectl patch svc llama-2-7b-weaviate-gorilla-server \
  -p '{"spec": {"type": "LoadBalancer"}}'
```

Wait for the external IP to get assigned:
```
kubectl get svc llama-2-7b-weaviate-gorilla-server -w
```

Now you can access the serving endpoint by using External IP
of the Service on port 8080. E.g. acccess it on:
[http://$EXTERNALIP:8080](http://$EXTERNAL_IP:8080)

### Option 2: Use port forwarding
You can use local port forwarding to the remote pod:
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

## Cleanup of serving endpoint
Once you're done with your testing make sure to delete the server
by running:
```
kubectl delete -f server.yaml
```

Note: If you forget to delete the Server you will be paying
for L4 GPU 24/7, which is ~$200 / month when using spot VMs.
