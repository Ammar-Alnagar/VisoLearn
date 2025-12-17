# Contributing

### Getting Started with Development

#### Development Environment Setup
```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/VisoLearn-2.git
cd VisoLearn-2

# 2. Set up development environment
python -m venv venv-dev
source venv-dev/bin/activate  # or venv-dev\Scripts\activate on Windows

# 3. Install development dependencies
pip install -e .
pip install -r requirements-dev.txt

# 4. Set up pre-commit hooks
pre-commit install

# 5. Create development configuration
cp .env.example .env.dev
# Edit .env.dev with your development API keys
```

#### Development Workflow
```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... edit files ...

# 3. Run tests
pytest tests/ -v
pytest tests/ --cov=models --cov-report=html

# 4. Run linting and formatting
black src/
flake8 src/
mypy src/

# 5. Test your changes
python app.py  # Manual testing
pytest tests/test_integration.py  # Integration tests

# 6. Commit and push
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name

# 7. Create pull request
```

### Contribution Guidelines

#### Code Style Standards

#### Documentation Standards

### Areas for Contribution

#### High-Priority Development Areas

**1. Accessibility Enhancements**

**2. Therapeutic Module Extensions**

**3. Research Integration**

### Code Review Process

#### Pull Request Checklist
