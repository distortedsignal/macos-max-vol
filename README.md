# MacOS Max Vol
A tool that sets max volume on macos

For a while, whenever I have joined a Microsoft Teams call, the volume on my Mac has been changed to be significantly louder than I would like. This is my attempt to fix that behavior.

## How To Use

### Set up the virtual environment

```sh
> virtualenv -p python3.10 venv
...
> source ./venv/bin/activate
...
```

### Read the utility help

```sh
> python ./max_vol.py --help
...
```

### Set up the control file

```sh
> cat ./control.json
{
    "sleep_time": {
        "time_unit": "second",
        "time_amount": 0.1
    },
    "max_volume": 10,
    "debug": false
}
```

The `sleep_time.time_unit` value should be one of \[`minute`, `second`, or `millisecond`\]. The `sleep_time.time_amount` should be a float. The `max_vol` should be (effectively) a percentage of total volume. That is, 0 is "muted", while 100 would be "full volume." The `debug` value should be a boolean.

### Run the script

```sh
> python ./max_vol.py
```

### Optional: Set up the script to run when MacOS starts

// TODO
