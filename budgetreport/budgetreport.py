#!/usr/bin/env python3

import re
import beancount
from beancount import loader
from beancount.query import query
from tabulate import tabulate


class BudgetReportItem:
    def __init__(self, date, account, budget):
        self.date = date
        self.account = account
        self.budget = float(budget)
        self.expense = 0.0

    # def __str__(self):
    #     return self.account

    def getRemaining(self):
        return self.budget - self.expense

    def getPercentExpense(self):
        if self.budget:
            return round(100.0 * float(self.expense) / float(self.budget), 1)

    def getPercentRemaining(self):
        if self.budget:
            return round(100.0 * float(self.getRemaining()) / float(self.budget), 1)

    def toList(self):
        return [self.account, self.budget, self.expense,
                self.getPercentExpense(), self.getRemaining(),
                self.getPercentRemaining()]

class BudggetReport:
    def __init__(self) -> None:
        self.budgetReportItems = {} # An dict to store budget report items
        self.total_budget = 0.0
        self.total_expenses = 0.0

    def addBudget(self, date, account, budget):
        be = BudgetReportItem(date, account, budget)
        if account in self.budgetReportItems:
            self.total_budget -= self.budgetReportItems[account].budget

        self.total_budget += float(budget)
        self.budgetReportItems[account] = be

    def addBudgetExpense(self, account, expense):
        self.total_expenses += float(expense)
        self.budgetReportItems[account].expense = float(expense)

    def getAccountBudget(self, account):
        return self.budgetReportItems[account].budget

    def getAccountExpense(self, account):
        return self.budgetReportItems[account].expense

    def getTotalRemaining(self):
        return self.total_budget - self.total_expenses

    def getPercentExpenses(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.total_expenses) / float(self.total_budget), 1)

    def getPercentRemaining(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.getTotalRemaining()) / float(self.total_budget), 1)

    def getBudgetReportItems(self):
        return self.budgetReportItems

    def toList(self):
        result = []
        for account in self.budgetReportItems:
            result.append(self.budgetReportItems[account].toList())
        # Append totals
        # result.append(['-----------------------', '--------', '---------',
        #     '-----', '-----------', '-----'])
        result.append(['Totals', self.total_budget, self.total_expenses,
            self.getPercentExpenses(), self.getTotalRemaining(),
            self.getPercentRemaining()])
        return result

    def printReport(self):
        headings = ['Account', 'Budget', 'Expense', '(%)', 'Remaining', '(%)']
        budget_data = self.toList()
        print(tabulate(budget_data, headings, numalign="right", floatfmt=".1f"))

    def printReport2(self):
        print("\n")
        print("{:<30} {:<8} {:<17} {:<17}".format(
            "Budget Account", "Budget", "Expense (%)", "Remaining (%)"))
        print("{:<30} {:<8} {:<17} {:<17}".format(
            "------------------------------", "-------", "----------------", "----------------"))

        for budget_account in self.budgetReportItems:
            bri = self.budgetReportItems[budget_account]
            if bri.budget == 0:
                str_expense = "{:<8}({:<5})".format(bri.expense, ' ')
            else:
                str_expense = "{:<8}({:<5})".format(
                    bri.expense, round(bri.getPercentExpense(), 1))

            if bri.budget == 0:
                str_remaining = "{:<8}({:<5})".format(bri.getRemaining(), ' ')
            else:
                str_remaining = "{:<8}({:<5})".format(
                    bri.getRemaining(), round(bri.getPercentRemaining(), 1))
            print("{:<30} {:<8} {:<17} {:<17}".format(
                bri.account, bri.budget, str_expense, str_remaining))

        # Print totals
        print("{:<30} {:<8} {:<17} {:<17}".format(
            "------------------------------", "-------", "----------------", "----------------"))
        str_expense_total = "{:<8}({:<5})".format(
            self.total_expenses, round(self.getPercentExpenses(), 1))
        str_remaining_total = "{:<8}({:<5})".format(
            self.getTotalRemaining(), round(self.getPercentRemaining(), 1))
        print("{:<30} {:<8} {:<17} {:<17}".format(
            " ", self.total_budget, str_expense_total, str_remaining_total))

# getBudgetReport : entries, options_map -> { account: BudgetReportItem }
def generateBudgetReport(entries, options_map, args):
    br = BudggetReport()

    for entry in entries:
        if isinstance(entry, beancount.core.data.Custom) and entry.type == 'budget':
            br.addBudget(entry.date, str(entry.values[0].value), abs(entry.values[1].value.number))

    # Get actual expenses for all budget accounts
    for budget_account in br.getBudgetReportItems():
        sql_query = "select account, SUM(position) AS amount WHERE account ~ '{}'".format(budget_account)
        if args.tag:
            sql_query += " and '{}' in tags".format(args.tag)

        if args.start_date:
            sql_query += " and date >= {}".format(args.start_date)

        if args.end_date:
            sql_query += " and date <= {}".format(args.end_date)

        rtypes, rrows = query.run_query(entries, options_map, sql_query, '', numberify=True)
        if len(rrows) != 0:
            account = rrows[0][0]
            amount = abs(rrows[0][1])
            br.addBudgetExpense(account, amount)

    return br

# ========================================================================
import argparse
import pkg_resources  # part of setuptools

def init_arg_parser():
    parser = argparse.ArgumentParser(description="Budget report for beancount files")
    parser.add_argument("-v", "--version", action="version", help="Print version number and exit",
        version='%(prog)s {}'.format(pkg_resources.require("budget_report")[0].version))
    parser.add_argument("-t", "--tag", help="Budget tag to use")
    parser.add_argument("-s", "--start-date", help="Budget start date")
    parser.add_argument("-e", "--end-date", help="Budget end date")
    parser.add_argument("filename", help="Name of beancount file to process")
    return parser

def script_main():
    parser = init_arg_parser()
    args = parser.parse_args()

    entries, errors, options_map = loader.load_file(args.filename)
    if errors:
        print(errors)
        #assert False

    br = generateBudgetReport(entries, options_map, args)
    br.printReport()

