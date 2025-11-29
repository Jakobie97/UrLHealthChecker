#!/bin/bash

# URL Health Checker - Deployment Script
# This script pulls the latest Docker image and runs it

set -e  # Exit on error

# Configuration
IMAGE_NAME="url-health-checker"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABASE_DIR="$PROJECT_ROOT/Database"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main deployment process
main() {
    log_info "Starting deployment of URL Health Checker..."
    
    # Ensure Database directory exists
    if [ ! -d "$DATABASE_DIR" ]; then
        log_info "Creating Database directory at $DATABASE_DIR"
        mkdir -p "$DATABASE_DIR"
    fi
    
    # Pull the latest image
    log_info "Pulling latest Docker image: $IMAGE_NAME"
    if docker pull "$IMAGE_NAME" 2>/dev/null; then
        log_success "Docker image pulled successfully"
    else
        log_error "Failed to pull image. Attempting to build locally..."
        cd "$PROJECT_ROOT"
        log_info "Building Docker image locally..."
        docker build -t "$IMAGE_NAME" .
        log_success "Docker image built successfully"
    fi
    
    # Run the container
    log_info "Running URL Health Checker container..."
    docker run --rm \
        -v "$DATABASE_DIR:/app/Database" \
        -v "$PROJECT_ROOT/config.yaml:/app/config.yaml:ro" \
        "$IMAGE_NAME"
    
    log_success "Deployment completed successfully!"
}

# Error handling
trap 'log_error "Deployment failed!"; exit 1' ERR

# Run main function
main "$@"
