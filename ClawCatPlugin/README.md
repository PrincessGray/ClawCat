# ClawCat Plugin Documentation 🐱

A Live2D desktop pet that integrates with Claude Code to provide visual feedback and interaction overlay.

[中文文档](./README_CN.md) | [English Documentation](./README.md) | [Main README](../README.md)

![ClawCat Demo](public/cover.png)

> **📦 Installation & Quick Start**: For installation instructions and quick start guide, please see the [Main README](../README.md).

## Features

- **Live2D Animation**: Cute cat character with smooth animations
- **Claude Code Integration**: Visual feedback for Claude's actions via hooks
- **Interactive States**:
  - Resting: Cat is idle
  - Working: Cat shows activity when Claude is thinking or using tools
  - Confirming: Cat displays permission requests with interactive buttons
- **Spy Mode**: Toggle between monitoring Claude and slacking off
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Transparent Window**: Frameless, draggable overlay that stays on top

## How It Works

### Hook Integration

ClawCat automatically responds to Claude Code events through the hook system:

1. **UserPromptSubmit**: Cat enters "working" state when you send a message
2. **PreToolUse**: Cat shows which tool Claude is about to use
3. **PostToolUse**: Cat pulses based on the result size
4. **PermissionRequest**: Cat displays an interactive permission dialog
5. **Notification**: Cat notifies you when Claude needs input
6. **Stop**: Cat returns to "resting" state when the session ends

### Interactive Features

- **Drag to Move**: Click and drag the cat to reposition it
- **Spy Mode Toggle**: Click the cat to toggle between monitoring and slacking
- **Permission Dialogs**: When Claude requests permission:
  - **Allow**: Grant permission for this action
  - **Always**: Grant permission and save to settings
  - **Deny**: Reject the permission request
  - **Jump**: Switch to the terminal to see details

### States

- **Resting** (Blue): Cat is idle, waiting for activity
- **Working** (Green): Cat is active, Claude is thinking or working
- **Confirming** (Yellow): Cat is waiting for your permission decision

## Configuration

### Port Configuration

By default, ClawCat uses:
- Vite dev server: `http://localhost:6173`
- HTTP server: `http://localhost:22622`

To change ports, edit:
- `ClawCatPlugin/vite.config.ts` for Vite port
- `ClawCatPlugin/src/server.py` for HTTP server port
- `ClawCatPlugin/scripts/notify.py` for hook client port

### Window Size

To adjust the window size, edit `ClawCatPlugin/src/launch_window.py`:

```python
DEFAULT_SCALE = 1.0  # Change to 0.5 for 50%, 2.0 for 200%, etc.
```

## Commands

### `/clawcat:start`

Start all ClawCat services. Automatically checks and installs dependencies if needed.

**What it does:**
1. Validates Python and Node.js versions
2. Checks for missing dependencies
3. Installs dependencies if needed
4. Verifies ports are available
5. Starts Vite dev server
6. Starts HTTP server
7. Launches PyQt window

### `/clawcat:stop`

Stop all ClawCat services gracefully.

**What it does:**
1. Terminates the PyQt window
2. Terminates the HTTP server
3. Terminates the Vite dev server
4. Cleans up PID files

## Troubleshooting

### Services won't start

**Problem**: Port already in use

**Solution**: Check if another process is using ports 6173 or 22622:

```bash
# Windows
netstat -ano | findstr :6173
netstat -ano | findstr :22622

# macOS/Linux
lsof -i :6173
lsof -i :22622
```

Kill the process or change the port in configuration files.

### Window doesn't appear

**Problem**: PyQt5 not installed correctly

**Solution**: Reinstall PyQt5:

```bash
pip uninstall PyQt5 PyQtWebEngine
pip install PyQt5 PyQtWebEngine
```

### Hooks not working

**Problem**: ClawCat service not running

**Solution**: Make sure ClawCat is started with `/clawcat:start`. Hooks will gracefully degrade if the service is not running.

### Cat is not animating

**Problem**: Live2D models not loading

**Solution**:
1. Check that `public/` directory contains the Live2D models
2. Verify Vite dev server is running on port 6173
3. Check browser console for errors (open DevTools in the window)

## Development

### Project Structure

```
ClawCatPlugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── commands/
│   ├── start.json           # Start command definition
│   └── stop.json            # Stop command definition
├── hooks/
│   └── hooks.json           # Hook configuration
├── scripts/
│   ├── notify.py            # Hook handler script
│   ├── service_manager.py   # Service lifecycle manager
│   └── install_deps.py      # Dependency installer
├── frontend/                # Vue.js frontend
│   ├── src/
│   │   ├── App.vue          # Main app component
│   │   └── main.ts          # Entry point
│   └── ...
├── src/                     # Python backend
│   ├── server.py            # HTTP server
│   ├── launch_window.py     # PyQt window launcher
│   └── window_control*.py   # Platform-specific window control
├── public/                  # Live2D models and assets
└── ...
```

### Running in Development Mode

1. Start services manually:
   ```bash
   # Terminal 1: Start Vite
   cd ClawCatPlugin
   npm run dev

   # Terminal 2: Start server
   python ClawCatPlugin/src/server.py

   # Terminal 3: Start window
   python ClawCatPlugin/src/launch_window.py
   ```

2. Make changes to the code
3. Vite will hot-reload frontend changes
4. Restart server/window for backend changes

### Adding New Animations

1. Add Live2D model files to `public/`
2. Update `frontend/src/App.vue` to load the new model
3. Add animation triggers in the state management logic

## Requirements

- **Python**: 3.8 or higher
- **Node.js**: 18 or higher
- **Operating System**: Windows, macOS, or Linux

### Python Dependencies

- `requests>=2.31.0` - HTTP client for hook communication
- `psutil>=5.9.0` - Process management
- `PyQt5>=5.15.10` - GUI framework
- `PyQtWebEngine>=5.15.6` - Web rendering

### Node.js Dependencies

- `vue` - Frontend framework
- `vite` - Build tool and dev server
- `pixi-live2d-display` - Live2D rendering

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Acknowledgments

This project is inspired by and references the [Bongo Cat](https://github.com/Externalizable/bongo.cat) project. We are grateful to the Bongo Cat community for their creative work and open-source contributions.

Special thanks to:
- **Bongo Cat** - Original desktop pet concept and animation ideas
- **Live2D** - Character animation technology
- **Claude Code** - Hook system and plugin architecture
- **Vue.js, Vite, PyQt5** - Frontend and desktop application frameworks

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

- Live2D models: [Specify your model source]
- Built with Vue.js, Vite, and PyQt5
- Integrates with Claude Code via hooks

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Note**: This plugin requires Claude Code to be installed and running. It enhances your Claude Code experience with visual feedback but does not modify Claude's core functionality.
