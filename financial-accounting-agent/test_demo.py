"""
CLI Test & Demonstration Script for Financial & Accounting AI Agent
Run this script to test all core AI agent modules in terminal.
"""

import os
import sys
import json
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.accounting_engine import AccountingEngine
from modules.document_parser import DocumentParser
from modules.reconciliation import BankReconcilationEngine
from modules.forecasting import CashFlowForecaster
from modules.ai_advisor import AIAdvisor
from utils.helper import format_thb

def run_demo():
    print("=" * 60)
    print("💼 Financial & Accounting AI Agent - CLI Demonstration")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    coa_path = os.path.join(base_dir, "data", "chart_of_accounts.json")
    tx_path = os.path.join(base_dir, "data", "sample_transactions.json")
    bank_csv_path = os.path.join(base_dir, "data", "sample_bank_statement.csv")

    # 1. Test Accounting Engine
    engine = AccountingEngine(coa_path, tx_path)
    pnl = engine.calculate_profit_loss()
    print("\n📊 1. [Financial Dashboard Metrics]")
    print(f"   • Total Income : {format_thb(pnl['total_income'])}")
    print(f"   • Total Expense: {format_thb(pnl['total_expense'])}")
    print(f"   • Net Profit   : {format_thb(pnl['net_profit'])} (Margin: {pnl['profit_margin']}%)")
    print(f"   • Net VAT (7%) : {format_thb(pnl['vat_net'])}")

    # 2. Test Document Parser
    parser = DocumentParser()
    parsed = parser.parse_document("ใบเสร็จค่าเช่าสำนักงาน.pdf")
    print("\n📄 2. [AI Smart Receipt Extraction]")
    print(f"   • Vendor      : {parsed['vendor_customer']}")
    print(f"   • Tax ID      : {parsed['tax_id']}")
    print(f"   • Amount Net  : {format_thb(parsed['amount_before_vat'])}")
    print(f"   • VAT 7%      : {format_thb(parsed['vat_amount'])}")
    print(f"   • WHT (5%)    : {format_thb(parsed['wht_amount'])}")

    print("\n   📖 [Generated Double-Entry Journal Entry]")
    journal = engine.generate_journal_entry(parsed)
    df_j = pd.DataFrame(journal)
    print(df_j[["Account_Code", "Account_Name", "Debit", "Credit"]].to_string(index=False))

    # 3. Test Bank Reconciliation
    if os.path.exists(bank_csv_path):
        bank_df = pd.read_csv(bank_csv_path)
        reconciler = BankReconcilationEngine()
        reconciled = reconciler.reconcile(bank_df, engine.get_all_transactions())
        matched_count = len(reconciled[reconciled["Confidence"] == 100.0])
        print("\n🏦 3. [Bank Reconciliation Engine]")
        print(f"   • Total Bank Lines Matched: {matched_count} / {len(bank_df)} (100% Confidence)")

    # 4. Test AI Advisor
    advisor = AIAdvisor()
    answer = advisor.ask("ยื่น ภ.พ. 30 เมื่อไหร่ และต้องจ่าย VAT เท่าไหร่?", context_metrics=pnl)
    print("\n💬 4. [AI Advisor Q&A Sample]")
    print(answer)

    print("\n" + "=" * 60)
    print("✅ All AI Agent modules executed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()
