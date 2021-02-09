#!/bin/sh
set -o errexit

# create registry container unless it already exists
reg_name='registry'
reg_port='5000'
cluster_name='sk8-cluster'
running="$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)"
if [ "${running}" != 'true' ]; then
  docker run \
    -d --restart=always -p "${reg_port}:5000" --name "${reg_name}" \
    registry:2
fi

# create a cluster with the local registry enabled in containerd
kind create cluster --name "${cluster_name}" --config kind-cluster-local.yaml

# connect the registry to the cluster network
docker network connect "kind" "${reg_name}" || true

# tell https://tilt.dev to use the registry
# https://docs.tilt.dev/choosing_clusters.html#discovering-the-registry
for node in $(kind get nodes --name=${cluster_name}); do
  kubectl annotate node "${node}" "kind.x-k8s.io/registry=localhost:${reg_port}" --context "kind-${cluster_name}" ;
done