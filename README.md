# UnicornVision - Investment Analytics Platform

UnicornVision is an AI-powered Streamlit application that provides comprehensive analytics for startup investments. This application has been adapted from Databricks notebooks to work locally.

## Features

- **Market Analysis**: Analyze funding trends, industry verticals, and global investment patterns
- **Competitor Analysis**: Compare startups head-to-head to understand competitive positioning
- **Portfolio Management**: Build and track your investment portfolio with ROI projections
- **Sentiment Analysis**: Analyze news sentiment for startups to gauge market perception
- **AI Investment Council**: Get AI-powered investment recommendations from multiple perspectives

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Data Files

The application needs two CSV files to run:

- `main_data.csv`: Main startup database
- `market_main.csv`: Market data for startups

These files should be in the root directory of the project.

## Usage

To start the Streamlit application, run:

```bash
streamlit run app.py
```

The application will open in your default web browser at http://localhost:8501

## Navigation

Use the sidebar to navigate between different modules:

- **Home**: Overview and quick stats
- **Market Analysis**: Analyze global startup investment trends and patterns
- **Competitor Analysis**: Compare startups head-to-head
- **Sentiment Analysis**: Analyze news sentiment for startups
- **Portfolio Management**: Build and track your investment portfolio
- **Investment Council**: Get AI-powered investment recommendations

## Notes

- The AI Investment Council module uses a simulated AI response as a replacement for the Mistral AI model used in the original Databricks implementation.
- Sentiment Analysis uses the News API with the provided API key. If the key expires, you will need to update it in the code.

## Requirements

The `requirements.txt` file includes all necessary dependencies. The main libraries used are:

- streamlit
- pandas
- matplotlib
- seaborn
- textblob
- requests
- numpy
