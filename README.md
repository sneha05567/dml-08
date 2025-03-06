# dml-08
Run
```
docker-compose up -d
docker ps
docker exec -it dml-08-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list
docker exec -it dml-08-kafka-1 kafka-console-consumer.sh \ --bootstrap-server localhost:9092 \ --topic predictions \ --from-beginning

# View data in topics
docker exec -it dml-08-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic predictions --from-beginning
docker exec -it dml-08-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic input-data --from-beginning
```

