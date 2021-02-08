from pyspark import conf
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming import KafkaUtils
import config
from pymongo import MongoClient


def run_spark_streaming():

    spark = SparkSession.builder.appName("client_click_in_out") \
        .config("spark.jars.packages", "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.2.0") \
        .config("spark.streaming.kafka.maxRatePerPartition", 2000) \
        .config("spark.default.parallelism", "5") \
        .config("spark.driver.memory", "16g")\
        .getOrCreate() #create if session doesn't exists.
    
    sc = spark.sparkContext
    ssc = StreamingContext(sc, 5) # 5 in 5 seconds
    kvs = KafkaUtils.createStream(ssc, config.KAFKA_CONN, "spark-streaming-consumer", {"client_click_in_out" : 3})
    lines = kvs.map(lambda x: transform_data(x[1]))


def transform_data(kafka_topic_data):
    # This function has company information that I can't share. Basically, it do transformation before insert de database table.
    data_to_mongo = kafka_topic_data
    send_to_mongo(data_to_mongo)


def send_to_mongo(data: dict()):
    try:
        client = MongoClient(config.MONGO_IP, config.MONGO_PORT)
        db = client.client_access
        doc = db.find_one_and_update(
        {"_id" : data[0]},
        {"$set":
            {"count_access": data[10]}
        },upsert=True
        )
    except Exception:
        pass
     ## send log error

    #client_dd = db.client.find({ "_id": data[0] })
