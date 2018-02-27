# GPU Job Manager

very simple job manager for nvidia GPU

## Features

- execute script when GPU become free.
    - only support program which use 1 GPU.     
- output stdout to file.

## Install

move job-manager.py to some directory in your PATH

or

execute job-manager.py directly 

## Usage

1. Start job manager

    ```
    cd <path/to/...>
    export CUDA_VISIBLE_DEVICES=0,1,2,3
    job-manager.py
    ```

    It will create new directory `jobs` in current directory.

2. Place script in `./jobs/queue`

    ```
    mv run.sh ./jobs/queue/
    ```

    Manager will watch gpu usage every 30s, if there is free gpu, start script under `./jobs/queue` automatically. When the script started, the script will be moved to `./jobs/running/<script name>.timestamp` and script's output will be written in `./jobs/running/<script name>.timestamp.log`.

    After the script end, manager will move them to `./jobs/success/` or `./jobs/fail/` following the return code.

## TODO

- Ability to rollback state after manager's unexpected shutdown
- Support script which use only part of GPU or multi GPU