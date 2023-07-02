import sys
from budgetreport import report, main
from beancount import loader

def testSingleAccountBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" "Groceries" Expenses:Groceries "month"   1000.0 USD

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Groceries" in br.budgetItems
      assert br.getBudgetExpense('Groceries') == 400.0
      assert br.getBudgetBudget('Groceries') == 1000.0
      assert br.total_budget == 1000.0
      assert br.total_expenses == 400.0
      assert br.getTotalRemaining() == 600.0

def testBudgetWithZeroValue(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" "Groceries" Expenses:Groceries "month"   0.0 USD

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 0.0
      assert br.total_expenses == 400.0
      assert br.getTotalRemaining() == -400.0
      assert br.getBudgetBudget('Groceries') == 0.0
      assert br.getBudgetExpense('Groceries') == 400.0

def testTaggedBugget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" "Groceries" Expenses:Groceries "month"   1000.0 USD

    pushtag #test-budget

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    200.0 USD
      Assets:CashInHand

    poptag #test-budget

    2021-01-03 * "Payee 2" "Some description"
      Expenses:Groceries                    100.0 USD
      Assets:CashInHand

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", "-t", "test-budget", "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 1000.0
      assert br.total_expenses == 600.0
      assert br.getTotalRemaining() == 400.0
      assert br.getBudgetBudget('Groceries') == 1000.0
      assert br.getBudgetExpense('Groceries') == 600.0

def testBuggetWithStartAndEndDate(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" "Groceries" Expenses:Groceries "month"   1000.0 USD

    2020-12-31 * "TestPayee" "Some description"
      Expenses:Groceries                    500.0 USD
      Assets:CashInHand

    2021-01-01 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    300.0 USD
      Assets:CashInHand

    2021-01-10 * "TestPayee" "Some description"
      Expenses:Groceries                    200.0 USD
      Assets:CashInHand

    2021-01-13 * "Payee 2" "Some description"
      Expenses:Groceries                    100.0 USD
      Assets:CashInHand

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", "-s" "2021-01-01", "-e", "2021-01-10", "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 1000.0
      assert br.total_expenses == 900.0
      assert br.getTotalRemaining() == 100.0
      assert br.getBudgetBudget('Groceries') == 1000.0
      assert br.getBudgetExpense('Groceries') == 900.0


def testMultipleAccountBudgets(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Clothing
2001-01-01 open Expenses:Education

2021-01-01 custom "budget" "Clothing" Expenses:Clothing "month"     1000.0 USD
2021-01-01 custom "budget" "Education" Expenses:Education "month"    2000.0 USD

2021-01-02 * "Test Payee 2" "Clothes etc"
    Expenses:Clothing                          300.0 USD
    Assets:CashInHand

2021-01-03 * "School" "Fees"
    Expenses:Education                        1200.0 USD
    Assets:CashInHand
  """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 3000.0
      assert br.total_expenses == 1500.0
      assert br.getTotalRemaining() == 1500.0
      assert br.getBudgetBudget('Education') == 2000.0
      assert br.getBudgetExpense('Education') == 1200.0
      assert br.getBudgetBudget('Clothing') == 1000.0
      assert br.getBudgetExpense('Clothing') == 300.0


def testBudgetRedefinitionOverridesOldValue(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Clothing
2001-01-01 open Expenses:Education

2021-01-01 custom "budget" "Clothing" Expenses:Clothing "month"     1000.0 USD
2021-01-01 custom "budget" "Clothing" Expenses:Clothing "month"    2000.0 USD

  """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 2000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 2000.0
      assert br.getBudgetBudget('Clothing') == 2000.0
      assert br.getBudgetExpense('Clothing') == 0.0

def testAutomaticallyAddsZeroBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2001-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2001-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 0.0
      assert br.total_expenses == 400.0
      assert br.getTotalRemaining() == -400.0
      assert br.getBudgetBudget('Expenses:Groceries') == 0.0
      assert br.getBudgetExpense('Expenses:Groceries') == 400.0

def testYearBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" "Groceries" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" "Education" Expenses:Education "year"  20000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'year', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 32000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 32000.0
      assert br.getBudgetBudget('Groceries') == 12000.0
      assert br.getBudgetBudget('Education') == 20000.0
 
def testMonthBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" "Groceries" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" "Education" Expenses:Education "month"  2000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'month', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 3000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 3000.0
      assert br.getBudgetBudget('Groceries') == 1000.0
      assert br.getBudgetBudget('Education') == 2000.0

def testQuarterBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" "Groceries" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" "Education" Expenses:Education "quarter"  2000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'quarter', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 5000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 5000.0
      assert br.getBudgetBudget('Groceries') == 3000.0
      assert br.getBudgetBudget('Education') == 2000.0
 
def testBiannualBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" "Groceries" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" "Groceries" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" "Education" Expenses:Education "biannual"  2000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'biannual', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 8000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 8000.0
      assert br.getBudgetBudget('Groceries') == 6000.0
      assert br.getBudgetBudget('Education') == 2000.0
 
def testLiabilitiesHandling(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Assets:CheckingAccount
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education
2001-01-01 open Liabilities:CreditCard

2001-01-01 custom "budget" "Groceries" Expenses:Groceries "month"  12000.0 RS
2001-01-01 custom "budget" "CreditCard" Liabilities:CreditCard "month"  6000.0 RS
2001-01-01 custom "budget" "Education" Expenses:Education "month"  2000.0 RS

2021-01-02 * "Test Payee 2" "Groceries"
    Expenses:Groceries                            900.0 RS
    Assets:CashInHand

2021-01-03 * "School" "Fees"
    Expenses:Education                           2200.0 RS
    Assets:CashInHand

2021-01-03 * "Online Shopping" "Groceries"
    Expenses:Groceries                           2500.0 RS
    Liabilities:CreditCard

2021-01-20 * "Bank" "Credit Card Payment"
    Liabilities:CreditCard                       1000.0 RS
    Assets:CheckingAccount
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 20000.0
      assert br.total_expenses == 4100.0
      assert br.getTotalRemaining() == 15900.0

      assert br.getBudgetBudget('Groceries') == 12000.0
      assert br.getBudgetBudget('Education') == 2000.0
      assert br.getBudgetBudget('CreditCard') == 6000.0

      assert br.getBudgetExpense('Groceries') == 900.0
      assert br.getBudgetExpense('Education') == 2200.0
      assert br.getBudgetExpense('CreditCard') == 1000.0

def testTotalIncome(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Income:Salary
2001-01-01 open Income:Business
2001-01-01 open Assets:BankAccount
2001-01-01 open Assets:CashInHand

2021-01-02 * "Employer" "Salary"
    Assets:BankAccount                          150000.0 RS
    Income:Salary

2021-01-03 * "Misc" "Income from sales"
    Assets:CashInHand                           200000.0 RS
    Income:Business

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_income == 350000.0

def testBudgetEndDate(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Expenses:Clothing
2001-01-01 open Expenses:Education
2001-01-01 open Expenses:Food
2001-01-01 open Expenses:Travel

2021-01-01 custom "budget" "Clothing" Expenses:Clothing "month"     1000.0 USD
2021-01-01 custom "budget" "Education" Expenses:Education "month"    2000.0 USD
2021-01-01 custom "budget" "Food" Expenses:Food "month"     1000.0 USD

2021-02-01 custom "budget" "Travel" Expenses:Travel "month"    2000.0 USD

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 4000.0
      assert br.getBudgetBudget('Travel') == 0.0


# MULTI ACCOUNT BUDGETS TESTING

def testBudgetWithMultipleAccounts(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Takeout

2021-01-01 custom "budget" "Food" "Expenses:Takeout Expenses:Groceries" "month"   1000.0 USD

2021-01-02 * "TestPayee" "Some description"
    Expenses:Groceries                    400.0 USD
    Assets:CashInHand

2021-01-03 * "TestPayee" "Other description"
    Expenses:Takeout                      100.0 USD
    Assets:CashInHand
""")

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Food" in br.budgetItems
      assert br.getBudgetExpense('Food') == 500.0
      assert br.getBudgetBudget('Food') == 1000.0
      assert br.total_budget == 1000.0
      assert br.total_expenses == 500.0
      assert br.getTotalRemaining() == 500.0

def testThrowWhenAccountAlreadyTaken(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Takeout

2021-01-01 custom "budget" "Food" "Expenses:Takeout Expenses:Groceries" "month"   1000.0 USD

2021-01-01 custom "budget" "Other" Expenses:Takeout "month"   1000.0 USD

2021-01-02 * "TestPayee" "Some description"
    Expenses:Groceries                    400.0 USD
    Assets:CashInHand

2021-01-03 * "TestPayee" "Other description"
    Expenses:Takeout                      100.0 USD
    Assets:CashInHand
""")

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      try:
        report.generateBudgetReport(entries, options_map, test_args)
        assert 3 == 2
      except:
        assert True

def testCanAcceptAccountInDifferentBudgetsIfPeriodIsDifferent(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Takeout

2021-01-01 custom "budget" "Food" "Expenses:Takeout Expenses:Groceries" "month" 1000.0 USD

2021-01-01 custom "budget" "YearlyFood" Expenses:Groceries "year" 12000.0 USD

2021-01-02 * "TestPayee" "Some description"
    Expenses:Groceries                    400.0 USD
    Assets:CashInHand

2021-01-03 * "TestPayee" "Other description"
    Expenses:Takeout                      100.0 USD
    Assets:CashInHand
""")

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Food" in br.budgetItems
      assert "YearlyFood" not in br.budgetItems

# The test doesn't work when there is not an empty line between the two budgets, 
# but there is not this problem when using a real file
def testMultipleBudgetsWithMultipleAccounts(monkeypatch):
    s = """
    2001-01-01 open Assets:CashInHand
    
    2001-01-01 open Expenses:Groceries
    2001-01-01 open Expenses:Takeout
    2001-01-01 open Expenses:Tech:HW
    2001-01-01 open Expenses:Tech:SW
    
    2021-01-01 custom "budget" "Food" "
        Expenses:Takeout 
        Expenses:Groceries
    " "month" 1000.0 USD
    
    2021-01-01 custom "budget" "Tech" "Expenses:Tech:HW Expenses:Tech:SW" "month" 2000.0 USD
    
    2021-01-02 * "TestPayee" "Some description"
        Expenses:Groceries                    400.0 USD
        Assets:CashInHand
    
    2021-01-03 * "TestPayee" "Other description"
        Expenses:Takeout                      100.0 USD
        Assets:CashInHand
    
    2021-01-02 * "TestPayee" "Some description"
        Expenses:Tech:HW                    350.0 USD
        Assets:CashInHand
    
    2021-01-03 * "TestPayee" "Other description"
        Expenses:Tech:SW                      250.0 USD
        Assets:CashInHand
    """
    print(s)
    entries, errors, options_map = loader.load_string(s)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Food" in br.budgetItems
      assert br.getBudgetExpense('Food') == 500.0
      assert br.getBudgetBudget('Food') == 1000.0
      assert br.getBudgetExpense('Tech') == 600.0
      assert br.getBudgetBudget('Tech') == 2000.0
      assert br.total_budget == 3000.0
      assert br.total_expenses == 1100.0
      assert br.getTotalRemaining() == 1900.0

def testSupportSubAccounts(monkeypatch):
    s = """2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries:Meat
2001-01-01 open Expenses:Food:Takeout

2021-01-01 custom "budget" "Food" "
    Expenses:Food 
    Expenses:Groceries
" "month" 1000.0 USD

2021-01-02 * "TestPayee" "Some description"
    Expenses:Groceries:Meat                    400.0 USD
    Assets:CashInHand

2021-01-03 * "TestPayee" "Other description"
    Expenses:Food:Takeout                      100.0 USD
    Assets:CashInHand"""
    
    entries, errors, options_map = loader.load_string(s)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Food" in br.budgetItems
      assert br.getBudgetBudget("Food") == 1000.0
      assert br.getBudgetExpense("Food") == 500.0

def testSupportSubAccountsPartTwo(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Food:Groceries
2001-01-01 open Expenses:Food:Takeout

2021-01-01 custom "budget" "Food" Expenses:Food "month" 1000.0 USD

2021-01-02 * "TestPayee" "Some description"
    Expenses:Food:Groceries                    400.0 USD
    Assets:CashInHand

2021-01-03 * "TestPayee" "Other description"
    Expenses:Food:Takeout                      100.0 USD
    Assets:CashInHand
""")

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Food" in br.budgetItems
      assert br.getBudgetBudget("Food") == 1000.0
      assert br.getBudgetExpense("Food") == 500.0


def canOverrideBudgetWithSameName(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:A
2001-01-01 open Expenses:B
2001-01-01 open Expenses:C

2021-01-01 custom "budget" "Food" "
    Expenses:A
    Expenses:B
" "month" 1000.0 USD

2021-01-01 custom "budget" "Food" "
    Expenses:A 
    Expenses:C
" "month" 2000.0 USD

2021-01-05 * "TestPayee" "Some description"
    Expenses:A                              400.0 USD
    Assets:CashInHand

2021-01-06 * "TestPayee" "Other description"
    Expenses:B                               100.0 USD
    Assets:CashInHand

2021-01-06 * "TestPayee" "Other description"
    Expenses:C                               300.0 USD
    Assets:CashInHand
""")

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert "Food" in br.budgetItems
      assert br.getBudgetBudget("Food") == 2000.0
      assert br.getBudgetExpense("Food") == 700.0
      assert "Expenses:B" in br.budgetItems
      assert br.getBudgetBudget("Expenses:B") == 0.0
      assert br.getBudgetExpense("Expenses:B") == 100.0
