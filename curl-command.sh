#curl -H "Content-Type: application/json" -X POST --data '{"name":"cassandraseed","cpu":"4","ram":"8192", "command":"cd cassandra;./script.sh;./startcassandra.sh;while sleep 5; do bin/nodetool -h localhost status; done","docker_image":"yasaswikishore/cassandra:initialcommit","storage":"False"}' http://127.0.0.1:5000/submit

#curl -H "Content-Type: application/json" -X POST --data '{"name":"cassandraseed","cpu":"1","ram":"1024", "command":"echo hello mesos!!!!!!!!!", "storage":"False"}' http://127.0.0.1:5000/submit

curl -H "Content-Type: application/json" -X POST --data '{"name":"cassandraseed","cpu":"1","ram":"1024", "command":"cd /home/shahidikram0701/apache-cassandra-3.10/bin;./cassandra -f;while sleep 5; do ./nodetool -h localhost status; done", "storage":"False"}' http://127.0.0.1:5000/submit

#curl -H "Content-Type: application/json" -X POST --data '{"name":"cassandraseed","cpu":"1","ram":"4096", "command":"cd cassandra;./script.sh;./startcassandra.sh;while sleep 5; do ps aux | grep java; ifconfig; done","docker_image":"yasaswikishore/cassandra:initialcommit","storage":"False"}' http://127.0.0.1:5000/submit
#curl -H "Content-Type: application/json" -X POST --data '{"name":"cassandraseed","cpu":"1","ram":"8196", "command":"cd cassandra;./script.sh;./startcassandra.sh; tailf ./logs/system.log","docker_image":"yasaswikishore/cassandra:initialcommit","storage":"False"}' http://127.0.0.1:5000/submit
#sleep 60
#curl -H "Content-Type: application/json" -X POST --data '{"name":"prometheus","cpu":"0.5","ram":"1024", "command":"cd prometheus;./config.sh cassandraseed 127.0.0.1;./prometheus;while sleep 5; do ps aux | grep prometheus; done","docker_image":"yasaswikishore/prometheus","storage":"False"}' http://127.0.0.1:5000/submit
