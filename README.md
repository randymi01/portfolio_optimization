# Python Portfolio Optimization

Small python portfolio optimizer. Given a set of stock tickers, finds the optimal weighting to either maximize portfolio utility or sharpe ratio. Optimization done using scipy.

## Requirements

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements

```bash
pip install -r requirements.txt
```

## Basic Usage

```bash
python main.py -s AAPL, MSFT, AMZN -o sharpe -p output.txt 
```

## CLI Options

| Flag                   | Description                                                                                                                                                                                         | Required |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `-s`\|`--stocks`       | Required argument, takes a comma separated list of stock tickers or the path to a newline separated txt file                                                                                        | True     |
| `-d`                   | Starting date for returns series. By default Jan 1 2020                                                                                                                                             | False    |
| `-e`                   | Ending date for returns series. By default today's date                                                                                                                                             | False    |
| `-o`\|`--optimization` | Optimization method to use. Currently only supports [Sharpe Ratio](https://en.wikipedia.org/wiki/Sharpe_ratio) and Utility. Default Sharpe Ratio.                                                   | False    |
| `-a`                   | [Risk Aversion Coefficient](https://en.wikipedia.org/wiki/Risk_aversion#Portfolio_theory) used in Utility function. Typically 1-5 where higher values represent lower risk appetite. Default is 1.  | False    |
| `-p`                   | Scipy optimization output path                                                                                                                                                                      | False    |

## License

[MIT](https://choosealicense.com/licenses/mit/)
