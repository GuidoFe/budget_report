# Budget Report for Beancount Ledgers

## 1. Introduction

If you use the text-based ledger system ie [beancount](https://github.com/beancount/beancount), and feel the need for a tools to track your expenses against your budget, then this tool may be what you need.

`budget-report` is a simple tool to read beancount ledger files as input and generate simple budget report based on the budget entries within the input beancount file. 

## 2. Installation

This fork is still not in the pip store. To install it manually:

1. Type `make build` in the terminal from the project folder
2. Type 
```
cd dist && pip install budget_report-X.X.tar.gz
```
where X.X is the current version


## 3. How-To Use

Using `budget-report` with your beancount files is a three step process:  

1. Specify your budget in the beancount files,  
2. Specifying the transactions to include in a particular budget and  
3. Generate budget report using `budget-report` script provided by this package.


### 3.1 Specifying Budget in beancount files

You specify your budget by entering a sequenct of beancount `custom` directives in the following format:  

```
<Date> custom "budget" "open" <Name> <Accounts> <Period> <Amount> <Currency>
```

Where:  

- **Date** is in the formate **YYYY-MM-DD**,   
- **Name** is an arbitrary name of the budget. 
- **Period** is the applicable period of the budget ie one of "year", "biannual", "quarter", "month", "week" or "day"
- **Amount** is a number specifying the budget amount allocated for this account,  
- **Accounts** are the names of the accounts covered by the budget, separated by a space. The entire list must be enclosed by quotes.
- **Currency** is the currency in which budget is specified.  

Here is an example budget:  


```
2021-11-06 custom "budget" "open" "Credit Card" "
    Liabilities:CreditCard
" "month"                          10000.0 RS

2021-11-06 custom "budget" "open" "Fuel" "
    Expenses:Car:Fuel
    Expenses:Truck:Fuel
" "month"                         5000.0 RS

2021-11-06 custom "budget" "open" "Fun" "
    Expenses:Fun:Gaming
    Expenses:Subscriptions:Twitch
" "month"                         1000.0 RS

2021-11-06 custom "budget" "open" "Clothing" "
    Expenses:Clothing 
    Expenses:Accessories
" "month"                         10000.0 RS

2021-11-06 custom "budget" "open" "School" Expenses:Education "month" 11000 RS

2021-11-06 custom "budget" "open" "Dining out" "
    Expenses:Food:DiningOut 
    Expenses:Vacation:Restaurant
" "month"                          3000.0 RS

2021-11-06 custom "budget" "open" "Groceries" Expenses:Groceries "month" 50000 RS

2021-11-06 custom "budget" "open" "Medicine" Expenses:Medicine "month" 2000 RS

2021-11-06 custom "budget" "open" "Pocket Money" Expenses:PocketMoney "month" 10000 RS
```

Please note that:   

a. Any budgets entries in the beancount file would override any previously specified entries for the same account.  
b. The budget entries could also be put into a separate file such as `mybudget.bean` and included into your main ledger file with `include "mybudget.bean"`
c. If you specify multiple accounts for a budget, they must be inside double quotes. You can put them in multiple lines, but the first quote must be in the first line and the second quote must be in the last one. For example, this is **WRONG**:
```
2021-11-06 custom "budget" "open" "Fuel" 
   "Expenses:Car:Fuel
    Expenses:Truck:Fuel"
month"                         5000.0 RS
```
These are **RIGHT**:
```
2021-11-06 custom "budget" "open" "Fuel" "
    Expenses:Car:Fuel
    Expenses:Truck:Fuel
" "month"                         5000.0 RS

2021-11-06 custom "budget" "open" "Groceries" Expenses:Groceries "month" 50000 RS
```

#### 3.1.1 Allocate a new amount

To define a new amount of an existing budget, instead of recreating the budget you can use this command:
```
<Date> custom "budget" "allocate" <Name> <Amount> <Currency>
```
The amount will replace the old one from the specified date, but the accounts and period will remain the same.

### 3.2 Specifying Transaction to include in budget  

By default, `bean-report` includes all transactions with dates falling within the specified budget report period (ie via the -p or --period switch on command line).  If no report period is given, the period is assumed to be "month" (ie current month's budget report would be generated).

a. The default start and/or end date(s) may be overridden by giving other values as command line arguments (-s and -e options), which would then overried the reports's start and end dates.  This may be usefule when say, you are generating report of one month (or other period), but some of the tranactions from a previous (or next) month/period should actually be counted in this budget's report.   

a. Budget name tags can also be used in your beancount ledger to identify/enclose transactions to include in a budget report.  Then the same tag may be specified at the command line while generating the budget report.

#### 3.2.1  Using Budget Tags

Tags can be used in your beancount ledger to specify transactions to include in a particular budget report.  The easiest way is to use beancount `pushtag` and `poptag` directive as below.  However, individullay tagging each transaction with a tag should also work.

    pushtag #Budget-Dec21 ; or any tag you want to use to name your budget!
    
    ....
    << transactions go here! >>
    ....

    poptag #Budget-Dec21  

Later, you can specify the same tag at `budget-report` command line using `-t` or `--tag` option, while generating budget report.

Note: If `budget-report` encounters a posting in the ledger with the budget tag, it is included into the bugetted postings regardless of the existence a corresponding `budget` directive.  If no corresponding `budget` directive entry is found, an entry for the posting account with zero budget value is automatically added for this purpose.  

#### 3.2.2 Using start and end dates  

               0.0     2000.0             -2000.0
Another way to tell `budget-report` which ledger entries to include in budget calculation, is to give it a start date (`-s` or `--start-date` command line option) and/or an end date (`-e` or `--end-date` command line option).  `budget-report` will include all transactions in the ledger falling at or after the given start date and at or before the given end date.

Note: Both the tag and start/end dates could be given together to fine tune the filtering, if that makes sense in your case.

### 3.3 Generating Budget report

After you have added the budget entries in your beancount file, you can generate the budget report by calling the `budget-report` script provided by this package from your shell console as below:  

`$ budget-report -t Budget-Dec21 /path/to/your/beancount_file.bean`, or  

`$ budget-report -s 2021-12-01 -e 2021-12-31 /path/to/your/beancount_file.bean`  

It would generate output similar to that shown below:

```
Budget Report:
  Period: 'month' (2021-12-01 to 2021-12-31)
Total Income: 150,000.00
Total Budget: 102,000.00
Budget Surplus/Deficit: 48,000.00

Name                   Budget    Expense     (%)    Remaining     (%)
------------------  ---------  ---------  ------  -----------  ------
Credit Card          10000.00       0.00    0.00     10000.00  100.00
Fuel                  5000.00    2500.00   50.00      2500.00   50.00
Fun                   1000.00     300.00   30.00       700.00   70.00
Clothing             10000.00    8000.00   80.00      2000.00   20.00
School               11000.00    5200.00   47.30      5800.00   52.70
Dining out            3000.00    4000.00  133.30     -1000.00  -33.30
Groceries            50000.00   10800.00   21.60     39200.00   78.40
Medicine              2000.00    1000.00   50.00      1000.00   50.00
Pocket Money         10000.00    6000.00   60.00      4000.00   40.00
Expenses:Gardening       0.00    2000.00             -2000.00
Totals              102000.00   39800.00   39.00     62200.00   61.00
```

Notes:  

a. If end date is omitted, all entries in the ledger at/after the start date would be included in the computation.  
b. If start date is omitted, and only end date is given, all entries at/before the end date would be included.  
c. If both tag and start/end dates are given, bothe will be used to filter the entries in the ledger.

# Help at Command Line

You can get help about all `budget-report` options at the command line using the -h switch.

    usage: budget-report [-h] [-v] [-V] [-t TAG] [-s START_DATE] [-e END_DATE] [-p PERIOD] filename

    Budget report for beancount files

    positional arguments:
      filename              Name of beancount file to process

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         Print version number and exit
      -V, --verbose         Print verbose output for errors
      -t TAG, --tag TAG     Budget tag to use
      -s START_DATE, --start-date START_DATE
                            Budget start date
      -e END_DATE, --end-date END_DATE
                            Budget end date
      -p PERIOD, --period PERIOD
                            Budget period
 
