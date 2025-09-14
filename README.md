# AI-Powered Commit Buddy

An intelligent CLI tool that automates commit message generation using artificial intelligence. It analyzes changes in your Git repository and generates clear and concise commit messages following the Conventional Commits convention.

## ✨ Features

- 🤖 **Intelligent message generation** using AI (Groq API)
- 📝 **Automatic Conventional Commits format** (feat, fix, docs, etc.)
- 📋 **Perfect for multi-file changes** with detailed file-by-file breakdown
- 🔄 **Fallback mode** for offline functionality
- 🎨 **Colorful interface** and easy to use
- ⚡ **Native Kiro integration**
- 🛡️ **Robust error handling**

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Git installed and configured
- Kiro IDE
- Groq account (for AI functionality)

### Installation steps

1. **Clone or download the project** to your Kiro workspace
2. **Install dependencies**:
   ```bash
   pip install -r .kiro/scripts/requirements.txt
   ```
3. **Configure your Groq API key** (see configuration section)
4. **Ready!** The command is now registered in Kiro

## ⚙️ Configuration

### Configure GROQ_API_KEY

To use AI functionality, you need to configure your Groq API key:

#### Option 1: Environment variable (Recommended)

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your_api_key_here"
# To make it permanent:
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your_api_key_here", "User")
```

**Windows (CMD):**
```cmd
set GROQ_API_KEY=your_api_key_here
# To make it permanent, use Control Panel > System > Environment Variables
```

**macOS/Linux:**
```bash
export GROQ_API_KEY="your_api_key_here"
# To make it permanent, add the above line to your ~/.bashrc or ~/.zshrc
```

#### Option 2: .env file (Alternative)

Create a `.env` file in your project root:
```
GROQ_API_KEY=your_api_key_here
```

### Get your Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Create an account or sign in
3. Navigate to "API Keys" in the panel
4. Create a new API key
5. Copy the key and configure it as indicated above

## 📖 Usage

### Basic command

```bash
python .kiro/scripts/commit_buddy.py --from-diff
```

This command excels at handling complex changes across multiple files:
1. Analyzes staged changes in your repository
2. Generates intelligent commit messages with file-by-file breakdown using AI
3. Shows you the proposed message with specific descriptions for each file
4. Allows you to confirm, edit, or cancel
5. Executes the commit automatically

### Typical workflow

Perfect for complex features affecting multiple files:

```bash
# 1. Make changes across multiple files
git add auth.py login.html styles.css config.py

# 2. Generate detailed commit with file-by-file breakdown
python .kiro/scripts/commit_buddy.py --from-diff
```

### Session example

Kiro Commit Buddy excels at handling complex changes across multiple files:

```
$ python .kiro/scripts/commit_buddy.py --from-diff

🔍 Analyzing staged changes...
✨ Generated message:
feat: add user authentication system

- auth.py: implement login and registration functions
- login.html: create user login form with validation  
- styles.css: add authentication page styling
- config.py: add authentication configuration settings

💬 Use this message? (y/n/e to edit): y
✅ Committed successfully!
```

The tool automatically analyzes each file's changes and provides specific descriptions of what was modified, making it perfect for complex features that span multiple files.

> **Note:** For simpler single-line messages, you can use the `--simple` flag if preferred.

## 🎯 Supported commit types

The tool automatically generates the correct prefix based on your changes:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

## 🔧 Troubleshooting

### Error: "You are not in a Git repository"

**Problem:** The command is executed outside of a Git repository.

**Solution:**
```bash
cd your-git-project
python .kiro/scripts/commit_buddy.py --from-diff
```

### Error: "No staged changes for commit"

**Problem:** You don't have files in the staging area.

**Solution:**
```bash
git add file1.py file2.js
python .kiro/scripts/commit_buddy.py --from-diff
```

### Error: "GROQ_API_KEY not configured"

**Problem:** The API key is not configured.

**Solution:**
1. Follow the GROQ_API_KEY configuration steps
2. Restart your terminal/IDE
3. Verify with: `echo $GROQ_API_KEY` (Linux/Mac) or `echo $env:GROQ_API_KEY` (Windows PowerShell)

### AI is not available

**Problem:** Groq API doesn't respond or there are connection issues.

**Behavior:** The tool automatically uses a fallback message:
```
⚠️  API not available, generating basic message...
📝 Proposed message: chore: update file1.py, file2.js
```

### Generated message is not appropriate

**Solution:** Use the edit option:
```
Use this message? (y/n/e to edit): e
Edit message: feat: implement user login system
```

### Permission issues on Windows

**Problem:** Error executing Python scripts.

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependencies not installed

**Problem:** Module import error.

**Solution:**
```bash
pip install -r .kiro/scripts/requirements.txt
```

## 🧪 Testing

To run the tests:

```bash
# Run all tests
python -m pytest .kiro/scripts/test_*.py -v

# Run specific tests
python -m pytest .kiro/scripts/test_commit_buddy_integration.py -v
```

## 📁 Project structure

```
.kiro/
├── hooks/
│   └── commit.yml              # Kiro command configuration
├── scripts/
│   ├── commit_buddy.py         # Main entry point
│   ├── config.py              # Configuration and environment variables
│   ├── git_operations.py      # Git operations
│   ├── groq_client.py         # Groq API client
│   ├── message_generator.py   # Message generation logic
│   ├── user_interface.py      # User interface
│   ├── requirements.txt       # Python dependencies
│   └── test_*.py             # Test files
└── specs/
    └── kiro-commit-buddy/     # Project documentation
```

## 🤝 Contributing

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/new-functionality`)
3. Commit your changes (`git commit -am 'feat: add new functionality'`)
4. Push to the branch (`git push origin feature/new-functionality`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License. See the `LICENSE` file for more details.

## 🆘 Support

If you encounter problems or have questions:

1. Review the **Troubleshooting** section
2. Search existing issues
3. Create a new issue with problem details

## 🔄 Changelog

### v1.1.0 (Latest)
- ✅ **Enhanced multi-file analysis** - Detailed file-by-file breakdown by default
- ✅ **Intelligent commit messages** - Specific descriptions for each file's changes
- ✅ **Improved AI prompts** - Better context understanding for complex changes
- ✅ **Optimized for complex features** - Perfect for changes spanning multiple files
- ✅ **Simple mode option** - Added `--simple` flag for single-line messages when needed
- ✅ **Better fallback messages** - Smarter file-type detection and descriptions
- ✅ **Increased diff size limit** - Handles larger changesets (up to 12KB)

### v1.0.0
- ✅ Automatic message generation with AI
- ✅ Conventional Commits support
- ✅ Offline fallback mode
- ✅ Complete Kiro integration
- ✅ Interactive user interface
- ✅ Robust error handling
