# Usage Examples - Kiro Commit Buddy

This guide contains practical examples of how to use Kiro Commit Buddy in different scenarios. Kiro Commit Buddy excels at handling complex changes across multiple files, providing detailed file-by-file breakdowns.

## 🚀 Basic usage

### Example 1: First commit

```bash
# 1. Create a new file
echo "print('Hello, World!')" > hello.py

# 2. Add to staging
git add hello.py

# 3. Generate detailed commit with AI (default behavior)
python .kiro/scripts/commit_buddy.py --from-diff
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
python .kiro/scripts/commit_buddy.py --from-diff
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
# Add new authentication system (multiple files)
git add auth.py login.html styles.css
python .kiro/scripts/commit_buddy.py --from-diff
# Result: 
# feat: add user authentication system
# 
# - auth.py: implement login and registration functions
# - login.html: create user login form with validation
# - styles.css: add authentication page styling

# Add API endpoint
git add api/users.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "feat: add users API endpoint"
```

### fix: Fixes

```bash
# Fix validation error
git add validation.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "fix: correct email validation regex"

# Fix memory problem
git add memory_manager.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "fix: resolve memory leak in cache"
```

### docs: Documentation

```bash
# Update README
git add README.md
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "docs: update installation instructions"

# Add code comments
git add complex_algorithm.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "docs: add comments to sorting algorithm"
```

### refactor: Refactoring

```bash
# Reorganize code across multiple files
git add utils.py helpers.py main.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result:
# refactor: extract utility functions to separate module
#
# - utils.py: extract common utility functions
# - helpers.py: add helper functions for data processing
# - main.py: update imports to use new utility modules

# Improve class structure
git add models/user.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "refactor: simplify user model structure"
```

### test: Tests

```bash
# Add unit tests
git add test_calculator.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "test: add unit tests for calculator functions"

# Update existing tests
git add test_auth.py
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "test: update authentication test cases"
```

### chore: Maintenance tasks

```bash
# Update dependencies
git add requirements.txt
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "chore: update project dependencies"

# Build configuration
git add .github/workflows/ci.yml
python .kiro/scripts/commit_buddy.py --from-diff
# Result: "chore: configure CI/CD pipeline"
```

## 🎛️ Interaction options

### Confirm message (y)

```bash
python .kiro/scripts/commit_buddy.py --from-diff
# Proposed message: "feat: add user dashboard"
# Use this message? (y/n/e to edit): y
# ✅ Commit created successfully
```

### Reject message (n)

```bash
python .kiro/scripts/commit_buddy.py --from-diff
# Proposed message: "chore: update files"
# Use this message? (y/n/e to edit): n
# ❌ Commit cancelled
```

### Edit message (e)

```bash
python .kiro/scripts/commit_buddy.py --from-diff
# Proposed message: "feat: add login"
# Use this message? (y/n/e to edit): e
# Edit message: feat: implement secure user login system
# ✅ Commit created with edited message
```

## 🔄 Fallback scenarios

### No internet connection

```bash
git add multiple_files.py config.json
python .kiro/scripts/commit_buddy.py --from-diff
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
python .kiro/scripts/commit_buddy.py --from-diff
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

Perfect for complex features spanning multiple files:

```bash
# 1. Create feature branch
git checkout -b feature/user-profile

# 2. Implement complete feature across multiple files
echo "class UserProfile: pass" > user_profile.py
echo "<form>...</form>" > profile_form.html
echo ".profile { ... }" > profile.css
echo "def test_user_profile(): pass" > test_user_profile.py

# 3. Stage all related files
git add user_profile.py profile_form.html profile.css test_user_profile.py

# 4. Generate comprehensive commit message
python .kiro/scripts/commit_buddy.py --from-diff
# Result:
# feat: implement user profile management system
#
# - user_profile.py: add UserProfile model with validation
# - profile_form.html: create user profile form interface
# - profile.css: add styling for profile components
# - test_user_profile.py: add comprehensive profile tests
```

### Bugfix workflow

```bash
# 1. Create bugfix branch
git checkout -b fix/login-error

# 2. Identify and fix the problem
# Edit auth.py to fix the bug
git add auth.py
python .kiro/scripts/commit_buddy.py --from-diff
# "fix: resolve login timeout issue"

# 3. Add test to prevent regression
git add test_auth.py
python .kiro/scripts/commit_buddy.py --from-diff
# "test: add test for login timeout scenario"

# 4. Update documentation if necessary
git add README.md
python .kiro/scripts/commit_buddy.py --from-diff
# "docs: update troubleshooting section"
```

### Refactoring workflow

```bash
# 1. Extract common functions
git add utils.py
python .kiro/scripts/commit_buddy.py --from-diff
# "refactor: extract common utilities"

# 2. Update imports in existing files
git add main.py auth.py
python .kiro/scripts/commit_buddy.py --from-diff
# "refactor: update imports to use new utilities"

# 3. Remove duplicate code
git add legacy_utils.py
python .kiro/scripts/commit_buddy.py --from-diff
# "refactor: remove duplicate utility functions"
```

## 🎯 Best practices

### 1. Logical grouping of related changes

```bash
# ✅ Excellent: Related files for one feature
git add user_model.py user_controller.py user_view.html
python .kiro/scripts/commit_buddy.py --from-diff
# Result:
# feat: implement user management system
#
# - user_model.py: add User model with validation
# - user_controller.py: implement user CRUD operations
# - user_view.html: create user interface templates

# ✅ Good: Single file changes
git add bug_fix.py
python .kiro/scripts/commit_buddy.py --from-diff
# "fix: resolve authentication timeout issue"

# ❌ Avoid: Multiple unrelated changes
# git add user_model.py payment_system.py random_bug_fix.py
```

### 2. Selective staging

```bash
# Add only specific parts of a file
git add -p complex_file.py
python .kiro/scripts/commit_buddy.py --from-diff

# Add specific files
git add src/models/user.py src/controllers/user.py
python .kiro/scripts/commit_buddy.py --from-diff
```

### 3. Review changes before commit

```bash
# Review what's staged
git diff --staged

# Generate detailed commit (default behavior)
python .kiro/scripts/commit_buddy.py --from-diff
```

### 4. Use editing when necessary

```bash
python .kiro/scripts/commit_buddy.py --from-diff
# If the generated message is: "chore: update files"
# Use 'e' to edit it to something more descriptive:
# "feat: implement user authentication middleware"
```

## 🔍 Specific use cases

### Python project

```bash
# Add new class
git add models/product.py
python .kiro/scripts/commit_buddy.py --from-diff
# "feat: add product model with validation"

# Update requirements
git add requirements.txt
python .kiro/scripts/commit_buddy.py --from-diff
# "chore: update dependencies to latest versions"

# Fix import
git add __init__.py
python .kiro/scripts/commit_buddy.py --from-diff
# "fix: correct module imports in package"
```

### JavaScript/Node.js project

```bash
# New React component
git add components/UserCard.jsx
python .kiro/scripts/commit_buddy.py --from-diff
# "feat: add user card component"

# Update package.json
git add package.json package-lock.json
python .kiro/scripts/commit_buddy.py --from-diff
# "chore: update npm dependencies"

# Fix bug in async function
git add api/users.js
python .kiro/scripts/commit_buddy.py --from-diff
# "fix: handle async errors in user API"
```

### Configuration and DevOps

```bash
# Docker configuration
git add Dockerfile docker-compose.yml
python .kiro/scripts/commit_buddy.py --from-diff
# "chore: add Docker configuration"

# CI/CD pipeline
git add .github/workflows/deploy.yml
python .kiro/scripts/commit_buddy.py --from-diff
# "chore: configure deployment pipeline"

# Environment variables
git add .env.example
python .kiro/scripts/commit_buddy.py --from-diff
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
python .kiro/scripts/commit_buddy.py --from-diff
# Edit: "feat: add user endpoint" → "feat: add GET /api/users endpoint"

# For frontend projects
python .kiro/scripts/commit_buddy.py --from-diff
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
python .kiro/scripts/commit_buddy.py --from-diff
# "style: fix linting issues in components"
```

These examples will help you make the most of Kiro Commit Buddy in your daily workflow! 🚀

## 📝 Additional Options

### Simple mode (optional)

If you prefer single-line commit messages for simple changes, you can use the `--simple` flag:

```bash
git add single_file.py
python .kiro/scripts/commit_buddy.py --from-diff --simple
# Result: "feat: add user authentication function"
```

However, the default detailed mode is recommended as it provides much more context about your changes, especially when working with multiple files.