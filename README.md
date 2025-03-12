# Pyhelios Development Environment

This repository contains a VS Code devcontainer configuration for working with the PyHelios package in a Miniconda environment.

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [VS Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/Leaf2Landscape/pyhelios_dev.git
   cd pyhelios_dev
   ```

2. Open the folder in VS Code:
   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or use the Command Palette (F1) and select "Remote-Containers: Reopen in Container".

4. VS Code will build the container and install all dependencies. This may take a few minutes the first time.

## Features

- Miniconda-based Python environment
- Helios++ command line tools and PyHelios pre-installed from conda-forge
- Common Python development tools (pylint, autopep8, etc.)
- VS Code configured with appropriate Python extensions and settings

## Container Structure

The development container is defined by two files in the `.devcontainer` directory:

- `devcontainer.json`: Configures VS Code settings, extensions, and container options
- `Dockerfile`: Defines the container image based on Miniconda with necessary packages

## License

Helios++ is released under GPLv3/LGPLv3 licenses. See the [LICENSE.md](https://github.com/3dgeo-heidelberg/helios/blob/main/LICENSE.md) file in the Helios++ repository for details.

## Links

- Official website: https://uni-heidelberg.de/helios
- GitHub repository: https://github.com/3dgeo-heidelberg/helios
