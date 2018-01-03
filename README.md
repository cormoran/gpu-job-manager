# gpu-job-manager
very simple job manager for nvidia gpu server

## usage

start job manager

~~~
cd <path/to/...>
export CUDA_VISIBLE_DEVICES=0,1,2,3
./job-manager.py
~~~

place run script under <path/to/...>/jobs/queue

~~~
mv run.sh <path/to/...>/jobs/queue/
~~~

manager will watch gpu usage every 30s, if there is free gpu, start script automatically.

when the script started, the script will be moved to <path/to/...>/jobs/running/<script name>.timestamp

and it's stdout will be redirected to <path/to/...>/jobs/running/<script name >.<timestamp>.log

After the script end, manager will move them to <path/to/...>/jobs/success/ or fail/ following the return code.

