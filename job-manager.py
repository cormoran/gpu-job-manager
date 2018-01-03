#! /usr/bin/env python3
import os
import shutil
import subprocess
import GPUtil
import time

script_dir = './jobs'
target_gpus = list(map(int, os.environ["CUDA_VISIBLE_DEVICES"].split(',')))
used_gpu = {}
running_procs = []

for state in ['queue', 'running', 'success', 'fail']:
    path = os.path.join(script_dir, state)
    os.makedirs(path, exist_ok=True)


def make_path(state, job):
    return os.path.join(script_dir, state, job)


def get_next_job():
    scripts = os.listdir(os.path.join(script_dir, 'queue'))
    scripts.sort()
    scripts = map(lambda f: os.path.join(script_dir, 'queue', f), scripts)
    scripts = filter(os.path.isfile, scripts)
    scripts = map(lambda f: os.path.basename(f), scripts)
    scripts = list(scripts)
    return scripts[0] if len(scripts) > 0 else None


def get_available_gpu():
    global used_gpu
    available_gpus = GPUtil.getAvailable(order='random', limit=100, maxLoad=0.01, maxMemory=0.01)
    available_gpus = list(filter(lambda id: target_gpus.count(id), available_gpus))
    for gpu in available_gpus:
        if gpu in used_gpu:
            # TODO: remove bad hard coding
            if time.time() - used_gpu[gpu] < 30:
                continue
        return gpu
    return None


def execute(gpu, job):
    global used_gpu
    global running_procs
    job_timestamp = job + '.' + time.strftime("%Y-%m-%d-%H-%M-%S")
    job_log = job_timestamp + '.log'
    # TODO: find better way to handle output
    command = 'bash ' + make_path('running', job_timestamp) + \
              ' > ' + make_path('running', job_log)

    shutil.move(make_path('queue', job), make_path('running', job_timestamp))
    p = subprocess.Popen(command, shell=True,
                         env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)})
    print("executed job '{}' on gpu {}".format(job, gpu))
    subprocess.call("slack start " + job_timestamp, shell=True)

    running_procs.append((p, gpu, job_timestamp, job_log))
    used_gpu[gpu] = time.time()


def try_execute():
    # TODO: don't show same messages twice
    gpu = get_available_gpu()
    if gpu is None:
        print('no available gpu')
        return False
    job = get_next_job()
    if job is None:
        print('no available job')
        return False
    execute(gpu, job)
    return True


def check_end_procs():
    global used_gpu
    global running_procs
    finished = []
    for i, proc_info in enumerate(running_procs):
        (p, gpu, job, log) = proc_info
        if p.poll() is not None:
            if p.returncode == 0:
                print("succees job '{}' on gpu {}".format(job, gpu))
                subprocess.call("slack end success " + job, shell=True)
                shutil.move(make_path('running', job), make_path('success', job))
                shutil.move(make_path('running', log), make_path('success', log))
            else:
                print("failed job '{}' on gpu {}".format(job, gpu))
                subprocess.call("slack end fail " + job, shell=True)
                shutil.move(make_path('running', job), make_path('fail', job))
                shutil.move(make_path('running', log), make_path('fail', log))
            finished.append(i)
            if gpu in used_gpu:
                del used_gpu[gpu]
    for i in reversed(finished):
        running_procs.pop(i)

while True:
    executed = try_execute()
    check_end_procs()
    time.sleep(10)
