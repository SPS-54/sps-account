import json
import pandas as pd

class AccountingEngine:
    """
    Core Accounting Engine for Double-Entry Bookkeeping & Financial Reporting.
    Handles General Journal Entries, Debit/Credit balancing, and P&L / Balance Sheet calculation.
    """

    def __init__(self, chart_of_accounts_path: str, transactions_path: str):
        with open(chart_of_accounts_path, 'r', encoding='utf-8') as f:
            self.chart_of_accounts = json.load(f)
        
        with open(transactions_path, 'r', encoding='utf-8') as f:
            self.transactions = json.load(f)

    def get_all_transactions(self) -> list:
        return self.transactions

    def add_transaction(self, tx: dict):
        self.transactions.append(tx)

    def generate_journal_entry(self, tx: dict) -> list:
        """
        Generates Double-Entry Journal Entries (Debit / Credit) for a given transaction.
        """
        entries = []
        doc_id = tx.get("id", "TX-NEW")
        desc = tx.get("description", "")
        tx_type = tx.get("type", "Expense")

        amt_net = tx.get("amount_before_vat", 0.0)
        vat_amt = tx.get("vat_amount", 0.0)
        wht_amt = tx.get("wht_amount", 0.0)
        net_cash = tx.get("net_cash_paid", tx.get("net_cash_received", tx.get("net_cash", 0.0)))

        if tx_type == "Expense":
            # Debit: Expense Account (Amount Before VAT)
            entries.append({
                "Doc_ID": doc_id,
                "Account_Code": tx.get("account_code", "5000"),
                "Account_Name": tx.get("account_name", "ค่าใช้จ่าย"),
                "Debit": amt_net,
                "Credit": 0.0,
                "Description": desc
            })
            # Debit: Input VAT (ภาษีซื้อ)
            if vat_amt > 0:
                entries.append({
                    "Doc_ID": doc_id,
                    "Account_Code": "1150",
                    "Account_Name": "ภาษีมูลค่าเพิ่มรอเรียกคืน (Input VAT)",
                    "Debit": vat_amt,
                    "Credit": 0.0,
                    "Description": f"ภาษีซื้อ - {desc}"
                })
            # Credit: Withholding Tax Payable (ภาษีหัก ณ ที่จ่ายค้างนำส่ง)
            if wht_amt > 0:
                entries.append({
                    "Doc_ID": doc_id,
                    "Account_Code": "2160",
                    "Account_Name": "ภาษีหัก ณ ที่จ่ายค้างนำส่ง (WHT Payable)",
                    "Debit": 0.0,
                    "Credit": wht_amt,
                    "Description": f"ภาษีหัก ณ ที่จ่าย - {desc}"
                })
            # Credit: Cash / Bank (เงินสด/ธนาคาร)
            entries.append({
                "Doc_ID": doc_id,
                "Account_Code": "1000",
                "Account_Name": "เงินสดและเงินฝากธนาคาร",
                "Debit": 0.0,
                "Credit": net_cash,
                "Description": f"ชำระเงินสุทธิ - {desc}"
            })

        else: # Income
            # Debit: Cash / Bank (Net Cash Received)
            entries.append({
                "Doc_ID": doc_id,
                "Account_Code": "1000",
                "Account_Name": "เงินสดและเงินฝากธนาคาร",
                "Debit": net_cash,
                "Credit": 0.0,
                "Description": f"รับชำระเงินสุทธิ - {desc}"
            })
            # Debit: Withholding Tax Asset (ภาษีถูกหัก ณ ที่จ่ายจ่ายล่วงหน้า)
            if wht_amt > 0:
                entries.append({
                    "Doc_ID": doc_id,
                    "Account_Code": "1160",
                    "Account_Name": "ภาษีถูกหัก ณ ที่จ่าย (WHT Asset)",
                    "Debit": wht_amt,
                    "Credit": 0.0,
                    "Description": f"ภาษีถูกหัก ณ ที่จ่าย - {desc}"
                })
            # Credit: Revenue (Amount Before VAT)
            entries.append({
                "Doc_ID": doc_id,
                "Account_Code": tx.get("account_code", "4000"),
                "Account_Name": tx.get("account_name", "รายได้จากการขายและบริการ"),
                "Debit": 0.0,
                "Credit": amt_net,
                "Description": desc
            })
            # Credit: Output VAT (ภาษีขาย)
            if vat_amt > 0:
                entries.append({
                    "Doc_ID": doc_id,
                    "Account_Code": "2150",
                    "Account_Name": "ภาษีมูลค่าเพิ่มค้างจ่าย (Output VAT)",
                    "Debit": 0.0,
                    "Credit": vat_amt,
                    "Description": f"ภาษีขาย - {desc}"
                })

        return entries

    def calculate_profit_loss((self) -> dict:
        """
        Calculates P&L Summary (Revenue, Expenses, Net Profit, Tax Estimates)
        """
        df_tx = pd.DataFrame(self.transactions)
        if df_tx.empty:
            return {"total_income": 0, "total_expense": 0, "net_profit": 0, "vat_net": 0}

        income_mask = df_tx["type"] == "Income"
        expense_mask = df_tx["type"] == "Expense"

        total_income = df_tx[income_mask]["amount_before_vat"].sum()
        total_expense = df_tx[expense_mask]["amount_before_vat"].sum()
        net_profit = total_income - total_expense

        output_vat = df_tx[income_mask]["vat_amount"].sum()
        input_vat = df_tx[expense_mask]["vat_amount"].sum()
        vat_net = output_vat - input_vat # (+) Payable, (-) Refundable

        wht_collected = df_tx[expense_mask]["wht_amount"].sum()
        wht_prepaid = df_tx[income_mask]["wht_amount"].sum()

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_profit": net_profit,
            "profit_margin": round((net_profit / total_income * 100), 2) if total_income > 0 else 0,
            "output_vat": output_vat,
            "input_vat": input_vat,
            "vat_net": vat_net,
            "wht_collected": wht_collected,
            "wht_prepaid": wht_prepaid
        }
