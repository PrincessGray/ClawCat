# ClawCat 🐱

A Live2D desktop pet that integrates with Claude Code to provide visual feedback and interaction overlay.

[中文文档](./README_CN.md) | [English Documentation](./README.md) | [Plugin Documentation](./ClawCatPlugin/README.md)

![ClawCat Demo](ClawCatPlugin/public/cover.png)

## Quick Start

### Installation via Claude Code Marketplace

```bash


# 1. Add the marketplace
/plugin marketplace add PrincessGray/ClawCat

# 2. Install the plugin
/plugin install clawcat
```

### Activate Hooks

After installation, you need to exit and resume Claude Code to activate the hooks:

```bash
# Exit Claude Code
exit

# Resume Claude Code (this activates the hooks)
claude-resume

# Now you can start ClawCat
/clawcat:start
```

### Usage

Start ClawCat with a single command:

```bash
/clawcat:start
```

Stop ClawCat when you're done:

```bash
/clawcat:stop
```

That's it! Dependencies will be automatically installed on first start.

### Installation from GitHub

If you prefer to run ClawCat directly from this GitHub repo (JS frontend is already bundled, no Node.js required for normal use):

```bash
# 1. Clone the repository
git clone https://github.com/PrincessGray/ClawCat.git
cd ClawCat/ClawCatPlugin

# 2. Prepare conda environment:
# The launcher scripts will automatically activate conda 'base' environment.
# If you prefer a dedicated environment, create and activate it first:

conda create -n clawcat python=3.10
conda activate clawcat

# 3. Install Python dependencies (or let the scripts install them on first run)
pip install -r requirements.txt
```

Then start ClawCat:

**Option A: Use the launcher scripts** (automatically activates conda base):

- On **Windows** (PowerShell or cmd):

```bash
scripts\start_window.bat
```

- On **macOS / Linux**:

```bash
bash scripts/start_window.sh
```

**Option B: Use your current conda environment** (if you've activated a custom environment):

```bash
python scripts/service_manager.py start
```

**Note**: The launcher scripts (`start_window.bat` / `start_window.sh`) will automatically activate conda `base` environment. If you want to use a custom conda environment, activate it first and then use Option B.  
You only need Node.js and npm if you want to **develop** or **modify** the frontend; they are not required just to run ClawCat from GitHub.

## Features

- **Live2D Animation**: Cute cat character with smooth animations
- **Claude Code Integration**: Visual feedback for Claude's actions via hooks
- **Interactive States**: Resting, Working, and Confirming modes
- **Spy Mode**: Toggle between monitoring Claude and slacking off
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Transparent Window**: Frameless, draggable overlay that stays on top

## Documentation

For detailed documentation, please see:

- [English Documentation](./ClawCatPlugin/README.md)
- [中文文档](./ClawCatPlugin/README_CN.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)

## Requirements

- **Python**: 3.8 or higher
- **Node.js**: 18 or higher
- **Operating System**: Windows, macOS, or Linux

## Project Structure

```text
ClawCat/
├── marketplace.json              # Marketplace configuration
├── ClawCatPlugin/                # Plugin directory
│   ├── .claude-plugin/           # Plugin metadata
│   ├── commands/                 # Command definitions
│   ├── hooks/                    # Hook configuration
│   ├── scripts/                  # Python scripts
│   ├── frontend/                 # Vue.js frontend
│   ├── src/                      # Python backend
│   ├── public/                   # Live2D models
│   ├── README.md                 # English documentation
│   └── README_CN.md              # Chinese documentation
├── LICENSE                       # MIT License
└── IMPLEMENTATION_SUMMARY.md     # Implementation details
```

## Development

See the [plugin documentation](./ClawCatPlugin/README.md#development) for development instructions.

## License

MIT License - see [LICENSE](./LICENSE) file for details.

## Acknowledgments

This project is inspired by and references the [Bongo Cat](https://github.com/Externalizable/bongo.cat) project. We are grateful to the Bongo Cat community for their creative work and open-source contributions.

- **Bongo Cat**: Original desktop pet concept and animation ideas
- **Live2D**: Character animation technology
- **Claude Code**: Hook system and plugin architecture

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Note**: This plugin requires Claude Code to be installed and running. It enhances your Claude Code experience with visual feedback but does not modify Claude's core functionality.
