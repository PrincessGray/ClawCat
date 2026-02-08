#!/bin/bash
# ClawCat Launcher for Unix-like systems
# Activates conda environment and starts service manager

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to plugin root
cd "$PLUGIN_ROOT"

# Try to find and activate conda
CONDA_FOUND=0

# Try conda in PATH first
if command -v conda &> /dev/null; then
    # Initialize conda
    eval "$(conda shell.bash hook)"
    conda activate base
    if [ $? -eq 0 ]; then
        CONDA_FOUND=1
    fi
fi

# If not found, try common locations
if [ $CONDA_FOUND -eq 0 ]; then
    if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        conda activate base
        if [ $? -eq 0 ]; then
            CONDA_FOUND=1
        fi
    fi
fi

if [ $CONDA_FOUND -eq 0 ]; then
    if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
        conda activate base
        if [ $? -eq 0 ]; then
            CONDA_FOUND=1
        fi
    fi
fi

# Start service manager (which will handle dependency installation and window launch)
python "$PLUGIN_ROOT/scripts/service_manager.py" start

