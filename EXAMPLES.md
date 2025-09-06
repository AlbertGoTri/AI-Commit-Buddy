# Usage Examples - Kiro Commit Buddy

This guide contains practical examples of how to use Kiro Commit Buddy in different scenarios.

## 🚀 Basic usage

### Example 1: First commit

```bash
# 1. Create a new file
echo "print('Hello, World!')" > hello.py

# 2. Add to staging
git add hello.py

# 3. Generate commit with AI
kiro commit --from-diff
```

**Expected output:**
```
🔍 Analyzing staged changes...
🤖 Generating message with AI...

📝 Proposed message:
feat: add hello world script

Use this message? (y/n/e to edit): y

✅ Commit created successfully: a1b2c3d
```

### Example 2: Bug fix

```bash
# 1. Fix a bug in the code
# Change: result = x / y
# To: result = x / y if y != 0 else 0

# 2. Add changes
git add calculator.py

# 3. Generate commit
kiro commit --from-diff
```

**Expected output:**
```
📝 Proposed message:
fix: prevent division by zero in calculator

Use this message? (y/n/e to edit): y
```

## 📝 Automatic commit types

### feat: New features

```bash
# Add new authentication function
git add auth.py login.html
kiro commit --from-diff
# Result: "feat: add user authentication system"

# Add API endpoint
git add api/users.py
kiro commit --from-diff
# Result: "feat: add users API endpoint"
```

### fix: Fixes

```bash
# Fix validation error
git add validation.py
kiro commit --from-diff
# Result: "fix: correct email validation regex"

# Fix memory problem
git add memory_manager.py
kiro commit --from-diff
# Result: "fix: resolve memory leak in cache"
```

### docs: Documentation

```bash
# Update README
git add README.md
kiro commit --from-diff
# Result: "docs: update installation instructions"

# Add code comments
git add complex_algorithm.py
kiro commit --from-diff
# Result: "docs: add comments to sorting algorithm"
```

### refactor: Refactoring

```bash
# Reorganize code
git add utils.py helpers.py
kiro commit --from-diff
# Result: "refactor: extract utility functions to separate module"

# Improve class structure
git add models/user.py
kiro commit --from-diff
# Result: "refactor: simplify user model structure"
```

### test: Tests

```bash
# Add unit tests
git add test_calculator.py
kiro commit --from-diff
# Result: "test: add unit tests for calculator functions"

# Update existing tests
git add test_auth.py
kiro commit --from-diff
# Result: "test: update authentication test cases"
```

### chore: Maintenance tasks

```bash
# Update dependencies
git add requirements.txt
kiro commit --from-diff
# Result: "chore: update project dependencies"

# Build configuration
git add .github/workflows/ci.yml
kiro commit --from-diff
# Result: "chore: configure CI/CD pipeline"
```

## 🎛️ Interaction options

### Confirm message (y)

```bash
kiro commit --from-diff
# Proposed message: "feat: add user dashboard"
# Use this message? (y/n/e to edit): y
# ✅ Commit created successfully
```

### Reject message (n)

```bash
kiro commit --from-diff
# Proposed message: "chore: update files"
# Use this message? (y/n/e to edit): n
# ❌ Commit cancelled
```

### Edit message (e)

```bash
kiro commit --from-diff
# Proposed message: "feat: add login"
# Use this message? (y/n/e to edit): e
# Edit message: feat: implement secure user login system
# ✅ Commit created with edited message
```

## 🔄 Fallback scenarios

### No internet connection

```bash
git add multiple_files.py config.json
kiro commit --from-diff
```

**Output:**
```
🔍 Analyzing staged changes...
⚠️  API not available, generating basic message...

📝 Proposed message:
chore: update multiple_files.py, config.json

Use this message? (y/n/e to edit): e
Edit message: feat: add configuration management system
```

### API key not configured

```bash
# Without GROQ_API_KEY configured
kiro commit --from-diff
```

**Output:**
```
⚠️  GROQ_API_KEY not configured. Using basic message...
Configure your API key to get smarter messages.

📝 Proposed message:
chore: update 3 files
```

## 🛠️ Advanced workflows

### Feature development workflow

```bash
# 1. Create feature branch
git checkout -b feature/user-profile

# 2. Implement basic functionality
echo "class UserProfile: pass" > user_profile.py
git add user_profile.py
kiro commit --from-diff
# "feat: add user profile model"

# 3. Add validations
# Edit user_profile.py to add validations
git add user_profile.py
kiro commit --from-diff
# "feat: add validation to user profile"

# 4. Add tests
echo "def test_user_profile(): pass" > test_user_profile.py
git add test_user_profile.py
kiro commit --from-diff
# "test: add user profile tests"

# 5. Document
echo "# User Profile\n\nManages user profiles..." > docs/user_profile.md
git add docs/user_profile.md
kiro commit --from-diff
# "docs: add user profile documentation"
```

### Bugfix workflow

```bash
# 1. Create bugfix branch
git checkout -b fix/login-error

# 2. Identify and fix the problem
# Edit auth.py to fix the bug
git add auth.py
kiro commit --from-diff
# "fix: resolve login timeout issue"

# 3. Add test to prevent regression
git add test_auth.py
kiro commit --from-diff
# "test: add test for login timeout scenario"

# 4. Update documentation if necessary
git add README.md
kiro commit --from-diff
# "docs: update troubleshooting section"
```

### Refactoring workflow

```bash
# 1. Extract common functions
git add utils.py
kiro commit --from-diff
# "refactor: extract common utilities"

# 2. Update imports in existing files
git add main.py auth.py
kiro commit --from-diff
# "refactor: update imports to use new utilities"

# 3. Remove duplicate code
git add legacy_utils.py
kiro commit --from-diff
# "refactor: remove duplicate utility functions"
```

## 🎯 Best practices

### 1. Atomic commits

```bash
# ✅ Good: One logical change per commit
git add user_model.py
kiro commit --from-diff
# "feat: add user model"

git add user_controller.py
kiro commit --from-diff
# "feat: add user controller"

# ❌ Avoid: Multiple unrelated changes
# git add user_model.py payment_system.py bug_fix.py
```

### 2. Selective staging

```bash
# Add only specific parts of a file
git add -p complex_file.py
kiro commit --from-diff

# Add specific files
git add src/models/user.py src/controllers/user.py
kiro commit --from-diff
```

### 3. Review changes before commit

```bash
# Review what's staged
git diff --staged

# Generate commit
kiro commit --from-diff
```

### 4. Use editing when necessary

```bash
kiro commit --from-diff
# If the generated message is: "chore: update files"
# Use 'e' to edit it to something more descriptive:
# "feat: implement user authentication middleware"
```

## 🔍 Specific use cases

### Python project

```bash
# Add new class
git add models/product.py
kiro commit --from-diff
# "feat: add product model with validation"

# Update requirements
git add requirements.txt
kiro commit --from-diff
# "chore: update dependencies to latest versions"

# Fix import
git add __init__.py
kiro commit --from-diff
# "fix: correct module imports in package"
```

### JavaScript/Node.js project

```bash
# New React component
git add components/UserCard.jsx
kiro commit --from-diff
# "feat: add user card component"

# Update package.json
git add package.json package-lock.json
kiro commit --from-diff
# "chore: update npm dependencies"

# Fix bug in async function
git add api/users.js
kiro commit --from-diff
# "fix: handle async errors in user API"
```

### Configuration and DevOps

```bash
# Docker configuration
git add Dockerfile docker-compose.yml
kiro commit --from-diff
# "chore: add Docker configuration"

# CI/CD pipeline
git add .github/workflows/deploy.yml
kiro commit --from-diff
# "chore: configure deployment pipeline"

# Environment variables
git add .env.example
kiro commit --from-diff
# "chore: add environment variables template"
```

## 📊 Statistics and analysis

### Analyze commit patterns

```bash
# View history of generated commits
git log --oneline --grep="feat:"
git log --oneline --grep="fix:"
git log --oneline --grep="docs:"

# Statistics by type
git log --pretty=format:"%s" | grep -E "^(feat|fix|docs|refactor|test|chore):" | sort | uniq -c
```

### Compare with manual commits

```bash
# Commits before using Kiro Commit Buddy
git log --before="2024-01-01" --oneline

# Commits after using Kiro Commit Buddy
git log --after="2024-01-01" --oneline
```

## 🎓 Advanced tips

### 1. Customize messages according to context

If you work on different types of projects, you can edit messages to better adapt them:

```bash
# For API projects
kiro commit --from-diff
# Edit: "feat: add user endpoint" → "feat: add GET /api/users endpoint"

# For frontend projects
kiro commit --from-diff
# Edit: "feat: add component" → "feat: add responsive user profile component"
```

### 2. Use with Git hooks

You can integrate Kiro Commit Buddy with Git hooks to automate the process even more:

```bash
# .git/hooks/prepare-commit-msg
#!/bin/sh
if [ -z "$2" ]; then
    python .kiro/scripts/commit_buddy.py --from-diff --auto > "$1"
fi
```

### 3. Combine with linting tools

```bash
# Run linter before commit
npm run lint
git add .
kiro commit --from-diff
# "style: fix linting issues in components"
```

These examples will help you make the most of Kiro Commit Buddy in your daily workflow! 🚀