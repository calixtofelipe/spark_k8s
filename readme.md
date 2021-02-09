## STEP BY STEP
1 - install a virtualenv separated
python3 -m venv venv
source venv/bin/activate

2 - install pyspark
pip install pyspark

3 - start sk8 cluster In the sk8 path (create a cluster)
./kind-with-registry.sh

4 - install minio ( we'll simulate to get a data in cloud - s3) with helm
helm repo add minio https://helm.min.io/
helm install minio --set accessKey=myaccesskey,secretKey=mysecretkey minio/minio

5 - Forward port to minio 
kubectl port-forward minio-6d77dbc49f-jc9wd 9000:9000
5.1 - to use kubefwd
sudo -E kubefwd svc


6 - copy a file to minio bucket

7 - install spark
sudo tar xfz spark-3.0.1-bin-hadoop3.2.tgz -C /usr/local/

8 - link make more easy to access spark
sudo ln -sT spark-3.0.1-bin-hadoop3.2 spark

9 - create enviroment variables bashrc
JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
10 - to apply the modifications
source ~/.bashrc

11 - 2 jar sources are necessary to this code, we found in maven and put in spark/jars folder.
WS SDK For Java Bundle 
Apache Hadoop Amazon Web Services Support » 3.2.0

12 - run the job in spark submit in source path
spark-submit main.py

13 - install spark operator
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm install sparkoperator spark-operator/spark-operator --set sparkJobNamespace=default
helm uninstall sparkoperator

14 - Create own image sparkprogram
At folder /usr/local/spark/bin/ there is a command to build this image docker-image-tool.sh
more info: https://spark.apache.org/docs/latest/running-on-kubernetes.html
./bin/docker-image-tool.sh -r calixto-spark -t v1 -p ./kubernetes/dockerfiles/spark/bindings/python/Dockerfile build

15 - freeze requirements
pip freeze > requirements.txt

16 - create a docker image personalized send to registry
 if needed to tag
 - docker tag sparkjob01:v2 localhost:5000/airflow-image:1.0.0
 - build image
 docker build -t localhost:5000/sparkjob:v1 .
 - send to registry
docker push localhost:5000/sparkjob:v1

17- CREATE RBAC authorization to pod
kubectl apply -f cluster-role.yaml
kubectl create clusterrolebinding role-binding-spark \
  --clusterrole=cluster-role-spark  \
  --serviceaccount=default:default


18 - execute sparkoperator
kubectl apply -f spark-operator.yml

19 - check logs in driver executor
kubectl logs [driver_pod_name]

20 - show sparkapplication
kubectl get SparkApplication