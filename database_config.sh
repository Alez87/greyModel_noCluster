#!/bin/bash
Tstart=$(date +%s%3N) 

#compress and send with one command
#ssh -i /home/ubuntu/key/mcn-key.pem ubuntu@ip_old 'cd /var/lib/influxdb; sudo tar zcvf - data hh wal meta' > influxdb.backup.tar.gz

oldfloatingip=$(<../influxdb_oldip)
echo $oldfloatingip

#compress data
Tcompress_start=$(date +%s%3N)
ssh -y -i /home/ubuntu/key/mcn-key.pem ubuntu@$oldfloatingip 'cd /var/lib/influxdb; sudo tar -zcvf /home/ubuntu/influxdb.backup.tar.gz data hh wal meta'
Tcompress_end=$(date +%s%3N)
#send data
Tmove_start=$(date +%s%3N)
scp -oStrictHostKeyChecking=no -i /home/ubuntu/key/mcn-key.pem ubuntu@$oldfloatingip:/home/ubuntu/influxdb.backup.tar.gz /home/ubuntu/
Tmove_end=$(date +%s%3N)
#remove data folders
rm -rf /var/lib/influxdb/*
#extract data
Textract_start=$(date +%s%3N)
cd /home/ubuntu
tar -zxvf influxdb.backup.tar.gz -C  /var/lib/influxdb
Textract_end=$(date +%s%3N)
#restart database
Trestart_start=$(date +%s%3N)
service influxdb restart
Trestart_end=$(date +%s%3N)
Tend=$(date +%s%3N)

Tcompress=$(((Tcompress_end-Tcompress_start)/1000))
Tmove=$(((Tmove_end-Tmove_start)/1000))
Textract=$(((Textract_end-Textract_start)/1000))
Trestart=$(((Trestart_end-Trestart_start)/1000))
Ttotal=$(((Tend-Tstart)/1000))

echo "Time to compress data: " $Tcompress >> /home/ubuntu/times_influxdb
echo "Time to move data: " $Tmove >> /home/ubuntu/times_influxdb
echo "Time to extract data: " $Textract >> /home/ubuntu/times_influxdb
echo "Time total: " $Ttotal >> /home/ubuntu/times_influxdb
