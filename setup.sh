#!/bin/bash

# Detect OS
case "$(uname -s)" in
    Linux*)     OS='Linux';;
    Darwin*)    OS='Mac';;
    MINGW*)     OS='Windows';;
    CYGWIN*)    OS='Windows';;
    *)          OS='Unknown';;
esac

# Default configuration
DEFAULT_MODEL_URL="https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz"
DEFAULT_MODEL_NAME="rfcn_resnet101_coco_2018_01_28"
DEFAULT_MODEL_PATH="tmp/model/rfcn/1"

# Use environment variables if set, otherwise use defaults
MODEL_URL=${MODEL_URL:-$DEFAULT_MODEL_URL}
MODEL_NAME=${MODEL_NAME:-$DEFAULT_MODEL_NAME}
MODEL_PATH=${MODEL_PATH:-$DEFAULT_MODEL_PATH}

# Default force flag to false
FORCE=false
BUILD=false

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -f, --force           Force model download even if it exists"
    echo "  -h, --help            Show this help message"
    echo "  -d, --down            Stop and remove containers"
    echo "  -b, --build           Force rebuild of containers"
    echo ""
    echo "Environment variables:"
    echo "  MODEL_URL             URL to download the model from"
    echo "                        Default: $DEFAULT_MODEL_URL"
    echo "  MODEL_NAME            Name of the extracted model directory"
    echo "                        Default: $DEFAULT_MODEL_NAME"
    echo "  MODEL_PATH            Path where to store the model"
    echo "                        Default: $DEFAULT_MODEL_PATH"
    echo ""
    echo "Platform-specific notes:"
    echo "  Windows: Run this script using Git Bash or WSL"
    echo "  Linux/Mac: Run directly in terminal"
    echo ""
    echo "Example:"
    echo "  MODEL_URL=https://example.com/model.tar.gz MODEL_PATH=tmp/custom/path $0"
}

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --force|-f)
            FORCE=true
            shift
            ;;
        --build|-b)
            BUILD=true
            shift
            ;;
        --down|-d)
            echo "Stopping and removing containers..."
            docker compose down -v
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "Starting setup process..."
echo "Detected OS: $OS"
echo "Using configuration:"
echo "Model URL: $MODEL_URL"
echo "Model Name: $MODEL_NAME"
echo "Model Path: $MODEL_PATH"

# Function to convert paths for Windows
convert_path() {
    if [ "$OS" = "Windows" ]; then
        echo "$1" | sed 's/\\/\//g'
    else
        echo "$1"
    fi
}

# Create directories only if they don't exist
if [ ! -d "$MODEL_PATH" ]; then
    echo "Creating directories..."
    mkdir -p "$MODEL_PATH"
else
    echo "Directory structure already exists"
fi

# Check if model exists and handle download based on force flag
if [ ! -f "$MODEL_PATH/saved_model.pb" ] || [ "$FORCE" = true ]; then
    echo "Downloading model..."

    # Extract filename from URL
    ARCHIVE_NAME=$(basename "$MODEL_URL")

    # Use curl if wget is not available (common on Windows)
    if command -v wget >/dev/null 2>&1; then
        wget "$MODEL_URL" -O "$ARCHIVE_NAME"
    else
        curl -L "$MODEL_URL" -o "$ARCHIVE_NAME"
    fi

    tar -xzvf "$ARCHIVE_NAME" -C tmp
    mv "tmp/$MODEL_NAME/saved_model/saved_model.pb" "$MODEL_PATH/"
    rm "$ARCHIVE_NAME"
    rm -rf "tmp/$MODEL_NAME"
else
    echo "Model already exists, skipping download (use --force to override)"
fi

# Set permissions (skip on Windows)
if [ "$OS" != "Windows" ]; then
    echo "Setting permissions..."
    chmod -R 777 tmp
fi

# Calculate cores for TensorFlow Serving
echo "Calculating CPU cores..."
if [ "$OS" = "Windows" ]; then
    # Use number of processors environment variable on Windows
    NUM_CORES=$NUMBER_OF_PROCESSORS
else
    # Use lscpu on Linux/Mac
    if command -v lscpu >/dev/null 2>&1; then
        cores_per_socket=$(lscpu | grep "Core(s) per socket" | cut -d':' -f2 | xargs)
        num_sockets=$(lscpu | grep "Socket(s)" | cut -d':' -f2 | xargs)
        NUM_CORES=$((cores_per_socket * num_sockets))
    else
        # Fallback for macOS
        NUM_CORES=$(sysctl -n hw.physicalcpu)
    fi
fi

# Export core count for docker compose
echo $NUM_CORES
export NUM_CORES

# Check if docker compose is available
if ! command -v docker compose >/dev/null 2>&1; then
    echo "Error: docker compose is not installed. Please install docker compose first."
    exit 1
fi

# Stop existing containers
echo "Stopping any existing containers..."
docker compose down

# Start services
echo "Starting services with Docker Compose..."
if [ "$BUILD" = true ]; then
    echo "Forcing rebuild of containers..."
    docker compose up -d --build
else
    docker compose up -d
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Verify services are running
echo "Verifying services..."
services=$(docker compose config --services)
echo "--------------------------------"

for service in $services; do
    container_name=$(docker compose ps -q $service)
    if [ "$(docker inspect --format '{{.State.Running}}' $container_name 2>/dev/null)" = "true" ]; then
        ports=$(docker inspect --format='{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}; {{end}}' $container_name)
        echo "✅ $service"
        echo "   Container: $(docker inspect --format='{{.Name}}' $container_name | sed 's/\///')"
        echo "   Ports: $ports"
    else
        echo "❌ $service is not running"
    fi
    echo "--------------------------------"
done


echo "Setup complete!"
echo "Useful commands:"
echo "- View logs: docker compose logs -f"
echo "- Stop services: $0 --down"
echo "- Rebuild services: $0 --build"
echo "- Force model download: $0 --force"
