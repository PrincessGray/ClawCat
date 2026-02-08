# ClawCat 🐱

A Live2D desktop pet that integrates with Claude Code to provide visual feedback and interaction overlay.

[中文文档](./ClawCatPlugin/README_CN.md) | [English Documentation](./ClawCatPlugin/README.md)

![ClawCat Demo](ClawCatPlugin/public/cover.png)

## Quick Start

### Installation via Claude Code Marketplace

```bash
# 1. Add the marketplace
/plugin marketplace add PrincessGray/ClawCat

# 2. Install the plugin
/plugin install clawcat
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

```
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
