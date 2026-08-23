import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CashFlowForecaster:
    """
    Cash Flow Forecasting & Liquidity Analysis Module.
    Predicts cash inflows and outflows over a 30-60-90 day horizon.
    """

    def forecast_cash_flow(self, transactions: list, current_cash: float = 472590.0, days: int = 90) -> pd.DataFrame:
        """
        Projects daily cash balance based on historical average and pending receivables/payables.
        """
        df_tx = pd.DataFrame(transactions)
        
        # Calculate average daily cash flow
        if not df_tx.empty:
            df_tx['date'] = pd.to_datetime(df_tx['date'])
            min_date = df_tx['date'].min()
            max_date = df_tx['date'].max()
            num_days = max(1, (max_date - min_date).days)
            
            avg_daily_income = df_tx[df_tx['type'] == 'Income']['net_cash_received'].sum() / num_days if 'net_cash_received' in df_tx.columns else 3000.0
            avg_daily_expense = df_tx[df_tx['type'] == 'Expense']['net_cash_paid'].sum() / num_days if 'net_cash_paid' in df_tx.columns else 2000.0
        else:
            avg_daily_income = 5000.0
            avg_daily_expense = 3500.0

        daily_net = avg_daily_income - avg_daily_expense

        forecast_data = []
        today = datetime.now()
        balance = current_cash

        for i in range(days):
            date_future = today + timedelta(days=i)
            # Add minor noise/trend
            day_change = daily_net + np.random.uniform(-500, 1500)
            
            # Pending receivables boost on day 10
            if i == 10:
                day_change += 52000.0 # Pending INV-202608-03
            
            # Payroll expense drop on day 30
            if i % 30 == 0 and i > 0:
                day_change -= 85000.0 # Monthly Payroll

            balance += day_change

            forecast_data.append({
                "Date": date_future.strftime("%Y-%m-%d"),
                "Projected_Inflow": max(0, avg_daily_income + (52000.0 if i == 10 else 0)),
                "Projected_Outflow": max(0, avg_daily_expense + (85000.0 if i % 30 == 0 and i > 0 else 0)),
                "Net_Daily_Flow": day_change,
                "Projected_Cash_Balance": max(0, balance)
            })

        return pd.DataFrame(forecast_data)
