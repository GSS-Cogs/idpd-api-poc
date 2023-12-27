
# Oxgigraph: Remote Data Sync

This document describes the process for deleting then replacing the RDF data for the remote oxigraph (and therefore sparql endpoint) used by this proof of concept api.

As it's a proof of concept, this is quite a manual process.

Please note - the api poc has a sparql endpoint but the graph data is **not** used to populate the graph, the graph _just so happens_ to use the same data that is served as jsonld by the api. The princple reason to follow these instruction is to keep these two sources of data syncronised.

**IMPORTANT** - we're not updating the data here so much as nuking it and starting again, be aware there will be a short period where the `/sparql` is offline followed by short periods where it is un or partially populated while the data is being ingested.

## Pre requisites

- 1.) You must have the [gcloud command line tool installed](https://cloud.google.com/sdk/docs/install-sdk).
- 2.) You must have configured your terminal and kubernetes context to access the staging cluster (please contact the dev team for guidance on doing this as its not suitable content for a public document).


## Explanation

Oxigraph runs as a pod on the GCP kubernetes engine. The graph is _not_ currently used to power the poc but oxigraph (and the sparql endpoint) are populated from the same data, to give the _illusion_ of a single source of truth.

To keep up this illusion we need to regularly replace the RDF data in oxigraph with the same RDF that's being published as jsonld via the api, otherwise they desync in a way that is potentially confusing to users.

Oxigraph itself runs on a kubernetes pod, with data persisted between restarts via a k8s volume (which works similarly to a docker volume for those familiar with that technology). 

The update process follows (this is the high level goal - we'll walk through each step in turn):

- 1. confirm access to the correct cluster
- 2. delete the k8s oxigraph deployment.
- 3. delete the k8s oxigraph volume claim (this will also delete the volume itself)
- 4. recreate the envionrment via the IAC pipeline (this is idempotent so will put everying back to the desired state - so all oxgraph componets will be restored... just without data).
- 5. port forward the remote oxigrapg to http://localhost:7878 and use `make populate` to populate the graph.

## 1. Confirm access to the correct cluster

Run the command:

```
kubectl config current-context
```

This will list your kubernetes context (i.e which kubernetes cluster your terminal is currently able to connect to). The context should say staging (if you've set up k8s helpers) or have the name "staging" in it if you have not. If its not clearly saying staging then _seek help from the development team_.

Then if you do:

```
kubectl get pods
```

All pods running in staging will be listed, if one of them starts with oxigraph then you are using the correct cluster (oxigraph only runs in the staging environment).

## 2. Delete the k8s oxigraph delpoyment

List all deployments on the cluster via

```
kubectl get deployments
```

One of these deployments _should say oxigraph_. Delete this deployment via:

```
kubectl delete deployment oxigraph
```

## 3. Delete the k8s oxigraph volume claim

List all persistent volume claims on the cluster via:

```
kubectl get persistentvolumeclaims
```

There should be one and it should be named `oxigraph-persistent-volume-claim`. If that is not the case then stop and highlight the issue.

If everything is as expected then delete the persistent volume claim via:

```
kubectl delete persistentvolumeclaim oxigraph-persistent-volume-claim
```

_Note: This will be a slow and may take a few minutes, please be patient._


## 4. Recreate the environment via the IAC pipeline

- to go google cloud in your browser (be signed in with your gsscogs email)
- to to cloud build (use the search bar)
- go to triggers in the left hand menu
- **run** the trigger for `environment-staging` via hitting the big "RUN" button at the end of the line.
- go to history in the left hand menu and you should be a able to see the pipeline run then complete with a green tick.

At this point the infrastructure you've removed has been restored - just without any data in it.

As a sanity check you can then go to `https://staging.idpd.uk/sparql` and you should have an empty graph database.


## 5. Port forward the remote oxigraph to http://localhost:7878

You need to first get the name of the new oxigraph pod. So run `kubectl get pods` and one of the names with start with `oxigraph-` - copy that name, it's the name of the pod, then:

```
kubectl port-forward <NAME OF OXIGRAPH POD> 7878:7878
```

As a sanity check you can then go to `http://localhost:7878` and you should have an empty graph database (the same one you checked remotely in the previous stage).

**Leave this terminal as-is and open a new terminal window for the next step.**

## 6. Populate the graph

First make sure you've exported the graph db url, via:

```
export GRAPH_DB_URL=http://localhost:7878
```

Then in a freshly cloned, up to date and on the `main` branch [idpd-api-poc repo](https://github.com/GSS-Cogs/idpd-api-poc) repo...

```
make populate
```

**Note:** this can also a slow process, be patient please. You'll get a "Data upload complete." message in the non port formwarded terminal once the remote graph has been updated (the port forwarded terminal will spam "Handling connection" messages, this is fine).

Once the data upload has completed, use `ctrl+c` to stop the port forwarding in the terminal where you port forwarded.

As a sanity check, if you visit https://staging.idpd.uk/sparql the graph should now be populated.