#!/bin/bash

# BCP Organizate Docker Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="bcp-organizate"
CONTAINER_NAME="bcp-organizate-app"
PORT=8501

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME .
    print_success "Docker image built successfully!"
}

# Function to run the container
run_container() {
    print_status "Stopping existing container if running..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    print_status "Starting new container: $CONTAINER_NAME"
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8501 \
        -v "$(pwd)/data:/app/data" \
        $IMAGE_NAME
    
    print_success "Container started successfully!"
    print_status "Access the application at: http://localhost:$PORT"
}

# Function to stop the container
stop_container() {
    print_status "Stopping container: $CONTAINER_NAME"
    docker stop $CONTAINER_NAME 2>/dev/null || print_warning "Container was not running"
    docker rm $CONTAINER_NAME 2>/dev/null || print_warning "Container was not found"
    print_success "Container stopped and removed!"
}

# Function to show logs
show_logs() {
    print_status "Showing logs for container: $CONTAINER_NAME"
    docker logs -f $CONTAINER_NAME
}

# Function to show container status
show_status() {
    print_status "Container status:"
    docker ps -a --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Function to open shell in container
shell() {
    print_status "Opening shell in container: $CONTAINER_NAME"
    docker exec -it $CONTAINER_NAME /bin/bash
}

# Function to clean up Docker resources
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    docker rmi $IMAGE_NAME 2>/dev/null || true
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "BCP Organizate Docker Helper Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the container (builds if needed)"
    echo "  stop      Stop and remove the container"
    echo "  restart   Restart the container"
    echo "  logs      Show container logs"
    echo "  status    Show container status"
    echo "  shell     Open shell in the container"
    echo "  cleanup   Remove container and image"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 logs"
    echo "  $0 stop"
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        # Build image if it doesn't exist
        if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
            print_warning "Image not found, building first..."
            build_image
        fi
        run_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        stop_container
        sleep 2
        run_container
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    shell)
        shell
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac