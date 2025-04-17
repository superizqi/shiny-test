# app.py
from shiny import App, ui, render
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Load registration_data.csv
def load_registration_data():
    if not os.path.exists("registration_data.csv"):
        raise FileNotFoundError("registration_data.csv tidak ditemukan!")
    
    df = pd.read_csv("registration_data.csv")
    return df

# Save to global variable
registration_df = load_registration_data()


# Load  transaction_data.csv
def load_transaction_data():
    if not os.path.exists("transaction_data.csv"):
        raise FileNotFoundError("transaction_data.csv tidak ditemukan!")

    df = pd.read_csv("transaction_data.csv", parse_dates=["date"])
    return df

transaction_df = load_transaction_data()

# monthly new paying users
def get_monthly_new_paying_users(df):
    # new transaction
    df = df[df["status"] == "success"].copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    first_tx = df.groupby("user_id")["date"].min().reset_index()
    first_tx["month"] = first_tx["date"].dt.to_period("M").dt.to_timestamp()

    monthly_new_users = first_tx.groupby("month").size().reset_index(name="new_users")
    return monthly_new_users

def get_monthly_cumulative_paying_users(df):
    df = df[df["status"] == "success"].copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df = df.sort_values("date")

    # cumulative transaction monthly
    cumulative = (
        df.groupby("month")["user_id"]
        .apply(lambda x: x.unique())
        .explode()
        .drop_duplicates()
        .reset_index()
        .groupby("month")
        .size()
        .cumsum()
        .reset_index(name="cumulative_users")
    )
    return cumulative

def get_monthly_new_paying_users_by_platform(transactions, registrations):

    merged = pd.merge(transactions, registrations, on="user_id", how="left")
    merged = merged[merged["status"] == "success"].copy()

    first_tx = merged.groupby("user_id")["date"].min().reset_index()
    first_tx["month"] = first_tx["date"].dt.to_period("M").dt.to_timestamp()

    first_tx = pd.merge(first_tx, registrations[["user_id", "platform"]], on="user_id", how="left")

    monthly_new = first_tx.groupby(["month", "platform"]).size().reset_index(name="new_users")
    return monthly_new


app_ui = ui.page_fluid(
    ui.br(),
    ui.row(
        ui.h2("Sekolah.Mu User Analytical Dashboard", class_="text-center"),
    ),
    ui.br(),
    ui.layout_columns(
        ui.card(
            ui.h4("Monthly Number of New Paying Users"),
            ui.output_plot("line_chart_new_users")
        ),
        ui.card(    
            ui.h4("Monthly Cumulative Number of Paying Users"),
            ui.output_plot("line_chart_cumulative_users")
        ),
         ui.card(
            ui.h4("% Registered Users by Platform"),
            ui.output_plot("pie_chart")
        )
    )
)


# Server
def server(input, output, session):
    @output
    @render.plot
    def pie_chart():
        platform_counts = registration_df["platform"].value_counts()
        fig, ax = plt.subplots()
        ax.pie(platform_counts, labels=platform_counts.index, autopct="%1.1f%%", startangle=140)
        return fig

    @output
    @render.plot
    def line_chart_new_users():
        data = get_monthly_new_paying_users(transaction_df)

        fig, ax = plt.subplots()
        ax.plot(data["month"], data["new_users"], marker='o', color='green')
        # ax.set_title("Monthly Number of New Paying Users")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of New Paying Users")
        ax.grid(True)
        fig.autofmt_xdate()  # Format tanggal di x-axis
        return fig
    
    @output
    @render.plot
    def line_chart_cumulative_users():
        data = get_monthly_cumulative_paying_users(transaction_df)

        fig, ax = plt.subplots()
        ax.plot(data["month"], data["cumulative_users"], marker='o', color='blue')
        ax.set_title("Monthly Cumulative Number of Paying Users")
        ax.set_xlabel("Month")
        ax.set_ylabel("Cumulative Paying Users")
        ax.grid(True)
        fig.autofmt_xdate()
        return fig

app = App(app_ui, server)
