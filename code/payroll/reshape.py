"""reshape.py - Step 3: the same numbers, turned sideways."""

import pandas as pd


def hours_grid(history: pd.DataFrame) -> pd.DataFrame:
    """Employees down the side, weeks across the top, hours in the cells."""
    grid = history.pivot_table(
        index=["employee_id", "display_name"],
        columns="week_ending",
        values="hours_worked",
        aggfunc="sum",
        fill_value=0,
    )
    grid = grid.reset_index().rename_axis(columns=None)
    return grid.sort_values("employee_id").reset_index(drop=True)


def missed_weeks(grid: pd.DataFrame) -> pd.DataFrame:
    """Every (employee, week) with zero hours in the grid."""
    long = grid.melt(
        id_vars=["employee_id", "display_name"],
        var_name="week_ending",
        value_name="hours_worked",
    )
    missed = long[long["hours_worked"] == 0]
    missed = missed.sort_values(["employee_id", "week_ending"])
    return missed.reset_index(drop=True)


def pay_by_month(history: pd.DataFrame) -> pd.DataFrame:
    """Total gross pay by month (rows) and department (columns), to the cent."""
    wide = history.pivot_table(
        index="month",
        columns="department",
        values="gross_pay",
        aggfunc="sum",
        fill_value=0.0,
    )
    wide = wide.reset_index().rename_axis(columns=None)
    return wide.sort_values("month").reset_index(drop=True)
