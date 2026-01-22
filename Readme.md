# Axis finder

This is a quick-and-dirty reimplementation of the axis finder provided in the Matlab reference implementation for the seminar. It is built using `panel`.

## Usage

To use the axis finder, you can first install the required packages (ideally in a virtual environment) by running:

```bash
pip install -e .
```

Then the axis finder can be started with:

```bash
axis-finder path/to/image/directory
```

for example, to use the dolphin dataset:

```bash
axis-finder "$(git rev-parse --show-toplevel)/data/images/dolphin"
```

This will open the GUI in a browser window. 
To auto-reload the applet if you make changes to the code, you can run `axis-finder` with the `--dev` flag:

```bash
axis-finder path/to/image/directory --dev
```

## Docker/Podman

The app can also be bundled in a Docker or Podman container. To build the container image, run:

```bash
docker build -t axis-finder .
```

or with Podman:

```bash
podman build -t axis-finder .
```

To run the container, use:

```bash
docker run --rm -p 5006:5006 -v path/to/image/directory:/data axis-finder /data
```

or with Podman:

```bash
podman run --rm -p 5006:5006 -v path/to/image/directory:/data axis-finder /data
```
