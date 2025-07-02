#!/bin/bash

# Display help message
function show_help {
    echo "Usage: $0 [OPTION]"
    echo "Deploy the S&P Investment Calculator application"
    echo ""
    echo "Options:"
    echo "  --restart    Restart the container (stop and remove existing container)"
    echo "  --upgrade    Same as --restart"
    echo "  --help       Display this help message"
    exit 0
}

# Check if help was requested
if [ "$1" == "--help" ]; then
    show_help
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Option to restart or upgrade the container
if [ "$1" == "--restart" ] || [ "$1" == "--upgrade" ]; then
    echo "Stopping and removing existing container..."
    docker stop sp-investment-calculator || true
    docker rm sp-investment-calculator || true
fi

echo "Building Docker image..."
if ! docker build -t sp-investment-calculator .; then
    echo "Error: Failed to build Docker image"
    exit 1
fi

echo "Starting container..."
if ! docker run -d \
    --name sp-investment-calculator \
    -p 8585:8585 \
    --restart always \
    sp-investment-calculator; then
    echo "Error: Failed to start container"
    exit 1
fi

echo "S&P Investment Calculator deployed successfully on port 8585"
echo "The application is accessible at http://spcalc.ibalampanis.gr"