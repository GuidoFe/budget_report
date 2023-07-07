# report.py
from datetime import datetime as dt
import decimal
import beancount
from beancount.query import query
from tabulate import tabulate
from .budget import BudgetItem
from .period import Period

class BudgetReport:
    def __init__(self) -> None:
        self.budgetItems = {} # A dict to store budget report items
        self.accountBudgetTree = AccountBudgetTree() # a dict to store account -> budget relations
        self.total_budget = 0.0
        self.total_expenses = 0.0
        self.total_income = 0.0
        self.tag = ''
        self.period = Period('month') # default period is month
        self.start_date = self.period.getPeriodStart(dt.today())
        self.end_date = self.period.getPeriodEnd(dt.today())

    def _addBudget(self, name, date, accounts, period, budget):
        assert period == self.period.period # only allow adding budget of matching period
        if name in self.budgetItems:
            budgetItem = self.budgetItems[name]
            self.total_budget -= float(budgetItem.budget)
            budgetItem.period = period
            budgetItem.budget = budget # update budget
            for account in budgetItem.accounts:
                self.accountBudgetTree.delBudget(account)
            for account in accounts:
                self.accountBudgetTree.addAccountBudget(account, budgetItem)
        else:
            be = BudgetItem(name, date, accounts, period, budget)
            self.budgetItems[name] = be # add new budget
            for account in accounts:
                self.accountBudgetTree.addAccountBudget(account, be)

        self.total_budget += float(budget)

    def addBudget(self, budget):
        # print('addBudget: {}'.format(budget))
        self._addBudget(budget.name, budget.date, budget.accounts, budget.period, budget.budget)

    def addBudgetExpense(self, date, name, expense):
        if not (name in self.budgetItems): # if budget does no exist
            raise Exception('addBudgetExpense: Unhandled budget {} in budget.\nself.budgetItems: {}'.format(name, self.budgetItems))

        # print('date: ', date, 'start_date: ', self.start_date, 'end_date: ', self.end_date)
        if date >= self.start_date and date <= self.end_date: # Expense should fall withing the period
            self.total_expenses += float(expense)
            self.budgetItems[name].expense += float(expense)

    def getBudgetBudget(self, name):
        ret = 0.0
        try:
            ret = self.budgetItems[name].budget
        except Exception as e:
            return 0.0
        else:
            return ret
    
    def changeBudgetBudget(self, name, newBudget):
        budgetItem = self.budgetItems[name]
        assert budgetItem != None
        self.total_budget -= float(budgetItem.budget)
        budgetItem.budget = newBudget
        self.total_budget += float(budgetItem.budget)

    def getBudgetExpense(self, name):
        ret = 0.0
        try:
            ret = self.budgetItems[name].expense
        except Exception as e:
            return 0.0
        else:
            return ret

    def getTotalRemaining(self):
        return float(self.total_budget) - float(self.total_expenses)

    def getPercentExpenses(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.total_expenses) / float(self.total_budget), 1)

    def getPercentRemaining(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.getTotalRemaining()) / float(self.total_budget), 1)

    def getBudgetItems(self):
        return self.budgetItems

    def setPeriod(self, period, start_date=dt.today()):
        self.period = Period(period)
        self.start_date = self.period.getPeriodStart(start_date)
        self.end_date = self.period.getPeriodEnd(start_date)

    def toList(self):
        result = []
        for name in self.budgetItems:
            result.append(self.budgetItems[name].toList())
        # Append totals
        result.append(['Totals', self.total_budget, self.total_expenses,
            self.getPercentExpenses(), self.getTotalRemaining(),
            self.getPercentRemaining()])
        return result

    def printReport(self, args):
        print('Budget Report:\n  Period: \'{}\' ({} to {})'.format(self.period.period, self.start_date, self.end_date))
        if args.tag:
            print('  Tag \'{}\''.format(args.tag))
        print('Total Income: {:,.2f}'.format(self.total_income))
        print('Total Budget: {:,.2f}'.format(self.total_budget))
        print('Budget Surplus/Deficit: {:,.2f}'.format(decimal.Decimal(self.total_income) - decimal.Decimal(self.total_budget)), '\n')

        headings = ['Name', 'Budget', 'Expense', '(%)', 'Remaining', '(%)']
        budget_data = self.toList()
        print(tabulate(budget_data, headings, numalign="right", floatfmt=".2f"))


    # Collect Budget accounts
    def collectBudgets(self, entries, options_map):
        # Collect all budgets
        for entry in entries:
            if not (isinstance(entry, beancount.core.data.Custom) and \
                    entry.type == 'budget' and \
                    entry.date <= self.end_date):
                continue
            if entry.values[0].value == 'open' and \
                    entry.values[3].value == self.period.period:
                name = str(entry.values[1].value)
                period = self.period.period
                budget = abs(entry.values[4].value.number)
                accounts = [];
                for account in str(entry.values[2].value).split():
                    accounts.append(account)
                self._addBudget(name, entry.date, accounts, period, budget)
            elif str(entry.values[0].value) == "allocate":
                name = str(entry.values[1].value)
                if name in self.budgetItems:
                    budget = abs(entry.values[2].value.number)
                    self.changeBudgetBudget(name, budget)


        # Collect expense accounts not budgetted but have expenses within the report period
        acct_query = "select account WHERE account ~ 'Expense' "
        if self.tag:
            acct_query += " and '{}' in tags ".format(self.tag)

        if self.start_date:
            acct_query += " and date >= {} ".format(self.start_date)

        if self.end_date:
            acct_query += " and date <= {} ".format(self.end_date)

        rtypes, rrows = query.run_query(
            entries, options_map, acct_query, '', numberify=True)

        for i in range(len(rrows)):
            account = rrows[i][0]
            if self.accountBudgetTree.getBudget(account) == None:
                self._addBudget(account, dt.today().strftime(
                    "%Y-%m-%d"), [account], self.period.period, 0.0)

    def generateBudgetReport(self, entries, options_map, tag, start_date, end_date, period):
        if tag:
            self.tag = tag
            self.start_date = dt.min.date() # Start from begining to include all entries within the tag
        if period:
            self.setPeriod(period)
        if start_date:
            self.setPeriod(self.period.period, dt.fromisoformat(start_date).date())
        if end_date:
            self.end_date = dt.fromisoformat(end_date).date()
            assert self.end_date >= self.start_date
        self.collectBudgets(entries, options_map)
        # ========================================================================================
        # Get actual postings for all budgetted accounts
        for name in self.budgetItems: # budgets:
            budget = self.budgetItems[name]
            postings_query = "select date, account, position, balance, number, other_accounts WHERE ( {} ) and not (findfirst('Liabilities', other_accounts) ~ 'Liabilities') and number >= 0.0 ".format(" OR ".join(map(lambda a: f"account ~ \"{a}\"", budget.accounts)))
            if tag:
                postings_query += " and '{}' in tags ".format(self.tag)

            if self.start_date:
                postings_query += " and date >= {} ".format(self.start_date)#.strftime('%Y-%m-%d'))

            if self.end_date:
                postings_query += " and date <= {} ".format(self.end_date)#.strftime('%Y-%m-%d'))

            #print('query: ', postings_query)
            rtypes, rrows = query.run_query(entries, options_map, postings_query, '', numberify=True)

            if len(rrows) != 0:
                try:
                    date = rrows[len(rrows)-1][0] # Get date of last posting
                    amount = abs(rrows[len(rrows)-1][3]) # get balance from last row
                    if amount == 0.0:
                        print('Warning: adding zero expense for budget= {}'.format(name))
                except Exception as e:
                    print('Exception caused by rrows value: \n  ', rrows[len(rrows)-1])
                else:
                    #print('adding expense: {}-{}'.format(account, amount))
                    self.addBudgetExpense(date, name, amount)

        # Get total income during the report period
        income_query = "select date, account, position, balance where account ~ 'Income'"

        if tag:
            income_query += " and '{}' in tags ".format(self.tag)

        if self.start_date:
            income_query += " and date >= {} ".format(self.start_date)#.strftime('%Y-%m-%d'))

        if self.end_date:
            income_query += " and date <= {} ".format(self.end_date)#.strftime('%Y-%m-%d'))

        rtypes, rrows = query.run_query(entries, options_map, income_query, '', numberify=True)
        # print(rrows)
        if len(rrows) != 0:
            self.total_income = abs(rrows[len(rrows)-1][3])

def generateBudgetReport(entries, options_map, args):
    br = BudgetReport()
    br.generateBudgetReport(entries, options_map, args.tag, args.start_date, args.end_date, args.period)
    return br


class ABItem:
    def __init__(self, name):
        self.name = name
        self.links = {}
        self.budget = None

class AccountBudgetTree:
    def __init__(self):
        self.root = ABItem("root")

    def addAccountBudget(self, path, budget):
        assert budget != None
        cursor = self.root
        for el in path.split(':'):
            if el in cursor.links:
                if cursor.budget != None and cursor.budget != budget:
                    raise Exception("budget of {} conflicts with {}".format(path, budget.name))
                cursor = cursor.links[el]
                continue
            newAccount = ABItem(el)
            cursor.links[el] = newAccount
            cursor = newAccount
        cursor.budget = budget

    def getItem(self, path):
        cursor = self.root
        for el in path.split(':'):
            if not el in cursor.links:
                return None
            cursor = cursor.links[el]
        return cursor

    def delBudget(self, path):
        item = self.getItem(path)
        if item != None:
            item.budget = None

    def getBudget(self, account):
        cursor = self.root
        for el in account.split(':'):
            if not el in cursor.links:
                return None
            cursor = cursor.links[el]
            if cursor.budget != None:
                return cursor.budget
        return None




