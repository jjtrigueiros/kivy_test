This is a demo app for android app development with Kivy.
I want to integrate it in my TCG card scanner project later.

## Goals

I want to:
    - build an app that runs on my android phone (arm64-v8a arch);
    - integrate it with my card scanner project.

Android app development is outside my comfort zone, so a lot of this is experimental.


## Running the project

Please follow the buildozer [installation instructions](https://buildozer.readthedocs.io/en/1.5.0/installation.html).

In short, we want to install its dependencies, most notably `openjdk-17`.:

```
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.33 virtualenv  # the --user should be removed if you do this in a venv
```

I recommend using [uv](https://docs.astral.sh/uv/) to install the project dependencies.

To create an APK for your target release, run:
`uv run buildozer android debug`

To send the app to your phone for debugging, (ensure your device architecture is in agreement with the buildozer.spec) connect your device with usb debugging on and file transfer enabled and then run:
`uv run buildozer android debug deploy run`

