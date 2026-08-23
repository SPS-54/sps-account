import pandas as pd

class BankReconcilationEngine:
    """
    Automated Bank Reconciliation Engine.
    Matches Bank Statement lines with General Ledger Transactions based on Date, Amount, and Reference.
    """

    def reconcile(self, bank_df: pd.DataFrame, ledger_txs: list) -> pd.DataFrame:
        """
        Performs matching between Bank Statement and Ledger Transactions.
        """
        matched_results = []
        ledger_df = pd.DataFrame(ledger_txs)

        for idx, bank_row in bank_df.iterrows():
            date_str = str(bank_row.get("Date", ""))
            withdrawal = float(bank_row.get("Withdrawal", 0) or 0)
            deposit = float(bank_row.get("Deposit", 0) or 0)
            bank_desc = str(bank_row.get("Description", ""))
            ref_no = str(bank_row.get("RefNo", ""))

            bank_amt = deposit if deposit > 0 else withdrawal
            tx_type = "Income" if deposit > 0 else "Expense"

            # Match candidates in Ledger
            matched_tx = None
            match_status = "Unmatched"
            confidence = 0.0

            if not ledger_df.empty:
                for _, tx in ledger_df.iterrows():
                    tx_net = tx.get("net_cash_received") if tx_type == "Income" else tx.get("net_cash_paid")
                    if tx_net is None:
                        tx_net = tx.get("net_cash", 0.0)

                    # Amount Match check
                    if abs(float(tx_net) - bank_amt) < 0.01:
                        # Exact amount match
                        if tx.get("date") == date_str:
                            matched_tx = tx
                            match_status = "Exact Match (100%)"
                            confidence = 100.0
                            break
                        else:
                            matched_tx = tx
                            match_status = "Amount Match (Date Diff)"
                            confidence = 85.0

            matched_results.append({
                "Bank_Date": date_str,
                "Bank_Description": bank_desc,
                "Bank_Amount": bank_amt,
                "Bank_RefNo": ref_no,
                "Matched_Ledger_ID": matched_tx.get("id") if matched_tx is not None else "-",
                "Matched_Customer_Vendor": matched_tx.get("vendor_customer") if matched_tx is not None else "-",
                "Match_Status": match_status,
                "Confidence": confidence
            })

        return pd.DataFrame(matched_results)
