# Contributing to Simulated Marketplace

The Simulated Marketplace is an open source research framework and we love to receive contributions from our community. There are many ways to contribute:

- **Writing tutorials or blog posts** about using the framework for research
- **Improving the documentation** to make it easier for newcomers to get started
- **Submitting bug reports** and helping us reproduce issues
- **Proposing new features** for studying market dynamics
- **Writing or improving tests** to increase code coverage and reliability
- **Implementing new agent types** or bidding strategies
- **Adding analysis tools** and visualization methods
- **Extending the framework** with new market mechanisms
- **Conducting validation studies** and sharing your results
- **Improving performance** and optimization of the simulation engine


# Ground Rules

## Code of Conduct

This is a research project and we expect all contributors to maintain professional and respectful communication. Be welcoming to newcomers and encourage diverse new contributors from all backgrounds.

## Responsibilities

* **Ensure compatibility** - Test your changes work on macOS, Linux, and Windows where possible
* **Write tests** - All new features and bug fixes should include appropriate test coverage
* **Create issues first** - For any major changes or enhancements, create an issue to discuss before implementing. Discuss things transparently and get community feedback
* **Keep changes focused** - Each pull request should address one feature or bug. Break large changes into multiple PRs
* **Maintain code quality** - Follow the existing code style and ensure all tests pass
* **Document your work** - Update relevant documentation and add docstrings to new functions
* **Preserve reproducibility** - Don't change framework assumptions or core mechanics without clear justification and discussion
* **Be respectful** - This project may be used by researchers worldwide. Be considerate in your communication

# Getting Started

## For Small Changes

Small contributions such as fixing spelling errors, where the content is small enough to not be considered intellectual property, can be submitted directly as a pull request without creating an issue first.

As a rule of thumb, changes are obvious fixes if they do not introduce any new functionality or creative thinking. Some likely examples include:

* Spelling / grammar fixes
* Typo correction, white space and formatting changes  
* Comment clean up
* Bug fixes that change default return values or error codes stored in constants
* Adding logging messages or debugging output
* Changes to configuration files like `.gitignore`, `requirements.txt`, etc.
* Moving source files from one directory or package to another

## For Larger Changes

For something that is bigger than a one or two line fix:

1. **Fork the repository** and create your branch from `master`
2. **Set up your development environment**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/simploy.git
   cd simploy
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure your API credentials** (see [SETUP_GUIDE.md](SETUP_GUIDE.md))
4. **Make your changes** in your fork
5. **Add tests** if you've added code that should be tested
6. **Run the test suite** to ensure everything passes:
   ```bash
   python -m pytest
   ```
7. **Test your changes** with a small simulation run:
   ```bash
   python run_marketplace.py --freelancers 5 --clients 2 --rounds 10
   ```
8. **Ensure your code follows the project style** (see Code Conventions below)
9. **Update documentation** if you've changed APIs or added features
10. **Write a clear commit message** describing your changes
11. **Submit a pull request** with a clear description of the problem and solution

# How to Report a Bug

## Security Vulnerabilities

**If you find a security vulnerability, do NOT open an issue.** Security issues should be reported privately to avoid exploitation. Please contact the maintainers directly through your institutional channels or create a private security advisory on GitHub.

## Bug Reports

When filing a bug report, please include:

1. **What version are you using?** Include Python version and key dependency versions
2. **What operating system are you using?** (macOS, Linux, Windows)
3. **What did you do?** Include the exact command you ran and any relevant configuration
4. **What did you expect to see?**
5. **What did you see instead?** Include the full error message and stack trace if applicable
6. **Can you reproduce it consistently?** Does it happen every time or intermittently?

**Include code samples** that demonstrate the bug. The better your bug report, the faster it will be fixed!

## Example Bug Report Template

```markdown
**Description:**
Brief description of the bug

**Steps to Reproduce:**
1. Run command: `python run_marketplace.py --freelancers 20 --clients 5`
2. See error in round 15

**Expected Behavior:**
Simulation should complete all 50 rounds

**Actual Behavior:**
Simulation crashes with KeyError at round 15

**Environment:**
- OS: macOS 14.0
- Python: 3.11.5
- Key dependencies: (from pip list)

**Error Message:**
```
[paste full stack trace]
```

**Additional Context:**
Any other information that might be helpful
```

# How to Suggest a Feature or Enhancement

## Project Philosophy

The Simulated Marketplace framework is designed as a controlled environment for studying emergent economic behavior with LLM agents. Our philosophy emphasizes:

- **Reproducibility** - Changes should maintain ability to reproduce results
- **Simplicity** - We prefer clear, understandable implementations over complex optimizations
- **Modularity** - New features should be modular and not tightly coupled to existing code
- **Research Focus** - Extensions should enable new research questions or improve experimental control
- **Transparency** - Market mechanisms should be interpretable and well-documented

## Proposing Features

If you find yourself wishing for a feature that doesn't exist, you are probably not alone! Open an issue on GitHub which describes:

1. **The feature you would like to see** - Be specific about what you want to add
2. **Why you need it** - What research question or use case does this enable?
3. **How it should work** - Provide a detailed proposal of the implementation
4. **Impact on existing functionality** - Will this change any existing behavior?
5. **Alternative approaches** - Have you considered other ways to solve this?

Good feature requests help us understand your needs and evaluate whether the feature aligns with the project's goals.

# Code Review Process

The maintainers review Pull Requests on a regular basis. Here's what to expect:

1. **Initial review** - A maintainer will review your PR
2. **Feedback** - You may receive requests for changes or questions about your approach
3. **Response time** - We expect responses to feedback within two weeks. After two weeks of inactivity, we may close the PR
4. **Testing** - All tests must pass before a PR can be merged
5. **Approval** - At least one maintainer must approve the changes
6. **Merge** - Once approved, a maintainer will merge your PR

## What We Look For

* **Correctness** - Does the code do what it's supposed to do?
* **Tests** - Are there appropriate tests with good coverage?
* **Documentation** - Are new features documented? Are docstrings clear?
* **Style** - Does the code follow project conventions?
* **Maintainability** - Will this be easy to understand and modify in the future?
* **Impact** - Does this change affect existing experiments or reproducibility?

# Code Conventions

## Python Style

* Follow [PEP 8](https://pep8.org/) style guidelines
* Use 4 spaces for indentation (not tabs)
* Maximum line length: 100 characters (flexible for readability)
* Use descriptive variable names (e.g., `freelancer_id` not `fid`)

## Error Handling and Logging

* **Always use `logger.exception()` instead of `logger.error()`** for exceptions
* Use appropriate log levels:
  - `logger.debug()` - Detailed diagnostic information
  - `logger.info()` - General informational messages
  - `logger.warning()` - Warning messages for recoverable issues
  - `logger.exception()` - Error messages with stack traces

```python
# Good
try:
    result = process_bid(bid)
except ValueError as e:
    logger.exception(f"Failed to process bid {bid.id}")
    return None

# Bad
try:
    result = process_bid(bid)
except ValueError as e:
    logger.error(f"Failed to process bid {bid.id}: {e}")
    return None
```

## Testing Conventions

* All test files must start with `test_`
* Use descriptive test names: `test_freelancer_bids_on_matching_job()`
* Use pytest markers for test categorization:
  - `@pytest.mark.unit` - Fast unit tests
  - `@pytest.mark.integration` - Integration tests
  - `@pytest.mark.ranking` - Ranking algorithm tests
  - `@pytest.mark.reputation` - Reputation system tests
  - `@pytest.mark.decision` - Decision making tests
  - `@pytest.mark.validation` - Pydantic validation tests

```python
import pytest

@pytest.mark.unit
def test_calculate_job_score():
    """Test job scoring with exact skill match."""
    score = calculate_job_score(freelancer, job)
    assert score > 0.8
```

## Type Safety

* Use Pydantic models for all LLM responses and data structures
* Add type hints to function signatures
* Validate inputs early and fail fast

```python
from pydantic import BaseModel, Field

class BidDecision(BaseModel):
    """Decision to bid on a job."""
    will_bid: bool
    reasoning: str = Field(..., min_length=10)
    confidence: float = Field(ge=0.0, le=1.0)
```

## Documentation

* Add docstrings to all public functions, classes, and modules
* Use Google-style docstrings:

```python
def calculate_reputation_score(freelancer_id: str, jobs: list[Job]) -> float:
    """Calculate reputation score based on job performance.
    
    Args:
        freelancer_id: Unique identifier for the freelancer
        jobs: List of completed jobs
        
    Returns:
        Reputation score between 0.0 and 1.0
        
    Raises:
        ValueError: If freelancer_id is not found
    """
    pass
```

## Commit Message Conventions

* Use clear, descriptive commit messages
* Start with a verb in present tense: "Add", "Fix", "Update", "Remove"
* Keep the first line under 72 characters
* Add detailed explanation after a blank line if needed

```bash
# Good
Add bid cooloff mechanism to prevent spam bidding

Implements a configurable cooloff period that prevents freelancers
from immediately re-bidding on the same job after rejection. This
improves market efficiency and reduces unnecessary LLM calls.

# Bad
fixed bug
```

## File Organization

* Place new agent types in `src/marketplace/`
* Place analysis tools in `src/analysis/`
* Place prompts in `src/prompts/`
* Place tests in `tests/` with corresponding names
* Update `__init__.py` files when adding new modules

# Community

This project was developed as part of AI-driven research, and we welcome collaboration from researchers and developers interested in LLM agent behavior, market simulation, and computational economics.

## Getting Help

* **Documentation**: Check [README.md](README.md), [SETUP_GUIDE.md](SETUP_GUIDE.md), and [FRAMEWORK_ASSUMPTIONS.md](FRAMEWORK_ASSUMPTIONS.md)
* **Issues**: Search existing issues before creating new ones
* **Discussions**: Use GitHub Discussions for questions and general discussion

## Recognition

Contributors will be acknowledged in the project. 
---

Thank you for contributing! 🚀

