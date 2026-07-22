# 📊 Log Analyzer

A production-grade command-line tool for analyzing log files using **Python**, **Regular Expressions**, **JSON configuration**, and **Pytest**.

The Log Analyzer helps developers quickly identify log severity levels, summarize log data, and detect critical issues from application log files.

---

## 🚀 Features

- 📂 Read log files efficiently
- 🔍 Detect log severity using Regular Expressions
- ⚙️ Configurable patterns through `config.json`
- 📈 Generate log summaries
- 🚨 Alert based on configurable thresholds
- 🧪 Comprehensive unit tests with Pytest
- 💻 Simple command-line interface (CLI)

---

## 🛠️ Tech Stack

- Python 3.12+
- Regular Expressions (Regex)
- JSON
- Pytest
- Rich (CLI Output)

---

## 📁 Project Structure

```text
log-analyzer/
├── sample_logs/
│   ├── app.log
│   ├── empty.log
│   └── malformed.log
│
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── pattern_matcher.py
│   ├── severity.py
│   ├── config.py
│   ├── reporter.py
│   └── cli.py
│
├── tests/
│   ├── test_parser.py
│   ├── test_matcher.py
│   ├── test_config.py
│   ├── test_reporter.py
│   └── test_integration.py
│
├── config.json
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/log-analyzer.git
cd log-analyzer
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Tests

```bash
pytest -v
```

---

## 📄 Sample Log

```text
2026-07-22 10:00:01 INFO Server started successfully
2026-07-22 10:01:10 WARNING High memory usage detected
2026-07-22 10:01:20 ERROR Database connection failed
2026-07-22 10:02:30 CRITICAL System shutting down
```

---

## ⚙️ Configuration

Severity patterns and alert thresholds are configurable in:

```text
config.json
```

Example:

```json
{
  "patterns": {
    "CRITICAL": "CRITICAL|FATAL",
    "ERROR": "ERROR",
    "WARNING": "WARN|WARNING",
    "INFO": "INFO"
  },
  "thresholds": {
    "CRITICAL": 1,
    "ERROR": 5,
    "WARNING": 10,
    "INFO": 100
  }
}
```

---

## 🧪 Testing

Run all tests

```bash
pytest -v
```

Generate test coverage

```bash
pytest --cov=src
```

---

## 📌 Roadmap

- [x] Project setup
- [x] Log file parser
- [ ] Configuration loader
- [ ] Pattern matcher
- [ ] Severity detection
- [ ] Report generation
- [ ] CLI interface
- [ ] Rich terminal output
- [ ] Full integration tests

---

## 🎯 Learning Objectives

This project demonstrates:

- File handling in Python
- Exception handling
- Regular Expressions
- JSON parsing
- Modular project architecture
- Unit testing with Pytest
- Configuration-driven development
- Command-line application development
- Git & GitHub workflow

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.
