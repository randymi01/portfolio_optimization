import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import argparse
from datetime import datetime
import itertools

from tqdm import tqdm
# py main.py -s {comma seperated stock tickers or link to txt file with tickers seperated by newline} 
#            -d {start date mm/dd/yyyy optional}
#            -e {end date mm/dd/yyyy optional} 
#            --optimization {"sharpe, utility"} 
#            -a {risk aversion for utility 1-5}
#            -p {output file name optional}

# Create ArgumentParser object
parser = argparse.ArgumentParser()

parser.add_argument('-s', '--stocks', type=str, help='comma seperated list of stock tickers or link to txt file with tickers', required=True, nargs='+')

parser.add_argument('-d', type=str, default='1/1/2020', help='start date')

parser.add_argument('-e', type=str, default=datetime.now().strftime("%m/%d/%Y"), help='end date')

parser.add_argument('--optimization', "-o", type=str, default='sharpe', help='optimization method')

parser.add_argument('-a', type=int, default=1, help='risk aversion for utility optimization')

parser.add_argument('-p', type=str, default=None, help='output file name')

# Parse the command-line arguments
args = parser.parse_args()


# Access the values of the arguments
if args.stocks[0].endswith('.txt'):
    with open(args.stocks[0], 'r') as f:
        stocks = f.read().splitlines()
else:
    stocks = ''.join(args.stocks).replace(" ","").split(",")
method = args.optimization
starting_date = datetime.strptime(args.d, '%m/%d/%Y')
ending_date = datetime.strptime(args.e, '%m/%d/%Y')
a = args.a
output_path = args.p

# get stock data
merged = pd.DataFrame()
for stock in tqdm(stocks):
    temp = yf.Ticker(stock)
    df = temp.history(start=starting_date, end=ending_date)
    df.rename(columns={'Close': stock}, inplace=True)
    merged = pd.merge(merged, df[[stock]], how = 'outer', left_index = True, right_index = True)

merged.index = merged.index.map(lambda x: x.strftime('%Y-%m-%d'))

# convert to percentage change
def percentage_change(lst):
    # Create two iterators over the list
    it1, it2 = itertools.tee(lst)

    # Advance the second iterator by one step
    next(it2)

    # Calculate percentage change
    temp = list(map(lambda i, j: (j-i)/i, it1, it2))
    temp.insert(0, 0)
    return temp

merged = merged.apply(percentage_change)

merged = merged.iloc[1:]

w = np.ones(len(stocks))/len(stocks)


# we assume iid so var(x + x) = var(x) + var(x) + 2cov(x,x) = var(x) + var(x) = 2var(x)... var(x + x...) = n * var(x)... sd(x + x...) = sqrt(n)sd(x)
# if we assume just identical, var(2x) = var(x) + var(x) + 2cov(x,x) = 2var(x) + 2var(x) = 4var(x)... var(nx) = n^2 * var(x)... sd(nx) = n * sd(x)
cov = merged.cov() * 252
mean = merged.mean() * 252

# get 10 year treasury rate
temp = yf.Ticker("^TNX")
rf = temp.history()['Close'].iloc[-1]/100

# negate because we are minimizing
def sharpe_ratio(w):
    return (w @ mean - rf) / (np.sqrt(w @ cov @ w)) * -1

def utility(w):
    return (w @ mean - 0.5 * a * w @ cov @ w) * -1

def optimize(func):
    from scipy.optimize import minimize

    constraints = ({'type': 'eq', 'fun': lambda x:  np.sum(x) - 1})

    res = minimize(func, w, constraints=constraints, bounds = [(0, None)])

    return res

if method == 'sharpe':
    output = optimize(sharpe_ratio)
    print("WEIGHTS:")
    print(pd.Series(output.x, index = mean.index))
    print(f"Return: {w @ mean}")
    print(f"Variance: {w @ cov @ w}")
    print(f"Sharpe Ratio: {output.fun * -1}")

if method == 'utility':
    output = optimize(utility)
    print("WEIGHTS:")
    print(pd.Series(output.x, index = mean.index))
    print(f"Return: {w @ mean}")
    print(f"Variance: {w @ cov @ w}")
    print(f"Sharpe Ratio: {sharpe_ratio(output.x) * -1}")
    print(f"Utility (a = {a}): {output.fun * -1}")

if output_path:
    with open(output_path, 'w') as f:
        f.write(str(output))
