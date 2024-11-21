import pandas as pd
from pathlib import Path
import extract_information
from datetime import datetime
import matplotlib.pyplot as plt

story_table_str = "./db/story.csv"
transaction_table_str = "./db/transaction.csv"
story_columns = ["date_id", "story", "new_category", "requires_update"]


def create_merged_df():

    # create dataframe
    transaction_table_df = pd.read_csv(transaction_table_str, dtype={"amount": float})
    story_table_df = pd.read_csv(story_table_str, dtype={"requires_update": bool})

    # left join
    merged_df = transaction_table_df.merge(story_table_df, how="left", left_on="date_id", right_on="date_id")

    # fill "story" and "requires_update" columns / why? / this should be made by the ETL????
    # this is required because in this process new data is being added to the story table
    merged_df = merged_df.fillna(
        {i: (False if i == "requires_update" else (merged_df["category"] if i == "new_category" else "")) for i in story_columns}
    )

    # convert to datetime type / think this should be deleted
    merged_df["date_id"] = pd.to_datetime(merged_df["date_id"])

    return merged_df


def create_if_doesnt_exist():

    # check db directory
    empty_data = {i: [] for i in story_columns}

    # if directory doesnt exist, create the directory and file
    if not (Path.cwd() / "db").exists():
        (Path.cwd() / "db").mkdir()

    # if story table doesnt exist, create it
    if not (Path.cwd() / "db" / "story.csv").exists():
        pd.DataFrame(data=empty_data).to_csv(story_table_str, index=False)

    # check transaction table
    if not (Path.cwd() / "db" / "transaction.csv").exists():
        return {
            "log": f"""
directory/db        EXISTS
transaction.csv     NOT EXISTS
story.csv         EXISTS """,
            "type": "error",
        }

    return {
        "log": f"""
directory/db        EXISTS
transaction.csv     EXISTS
story.csv         EXISTS """,
        "type": "success",
    }


def get_months():
    return pd.read_csv("./db/transaction.csv")["month"].unique()


def get_categories():
    return pd.read_csv("./db/category.csv")["category"].to_list()


def ETL_transaction(string_data):
    extract_information.ETL_transaction(string_data)


def make_graphs(edited_df):
    fig, axs = plt.subplots(3, 3, figsize=(20, 20))

    # only expenses, only october, no TRAN.CTAS.PROP.BM
    filtered_df = edited_df[(edited_df["type"] == "expense") & (edited_df["month"] == 7) & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["new_category", "amount"]].groupby(["new_category"]).sum().reset_index()
    axs[0, 0].set_title("july")
    axs[0, 0].bar(alfa["new_category"], alfa["amount"])
    axs[0, 0].set_xticklabels(alfa["new_category"], rotation=90)
    axs[0, 0].grid(True)

    # only expenses, only october, no TRAN.CTAS.PROP.BM
    filtered_df = edited_df[(edited_df["type"] == "expense") & (edited_df["month"] == 8) & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["new_category", "amount"]].groupby(["new_category"]).sum().reset_index()
    axs[0, 1].set_title("august")
    axs[0, 1].bar(alfa["new_category"], alfa["amount"])
    axs[0, 1].set_xticklabels(alfa["new_category"], rotation=90)
    axs[0, 1].grid(True)

    # only expenses, only october, no TRAN.CTAS.PROP.BM
    filtered_df = edited_df[(edited_df["type"] == "expense") & (edited_df["month"] == 9) & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["new_category", "amount"]].groupby(["new_category"]).sum().reset_index()
    axs[0, 2].set_title("september")
    axs[0, 2].bar(alfa["new_category"], alfa["amount"])
    axs[0, 2].set_xticklabels(alfa["new_category"], rotation=90)
    axs[0, 2].grid(True)

    # only expenses, only november, no TRAN.CTAS.PROP.BM
    filtered_df = edited_df[(edited_df["type"] == "expense") & (edited_df["month"] == 10) & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["new_category", "amount"]].groupby(["new_category"]).sum().reset_index()
    axs[1, 0].set_title("october")
    axs[1, 0].bar(alfa["new_category"], alfa["amount"])
    axs[1, 0].set_xticklabels(alfa["new_category"], rotation=90)
    axs[1, 0].grid(True)

    # only expenses, only november, no TRAN.CTAS.PROP.BM
    filtered_df = edited_df[(edited_df["type"] == "expense") & (edited_df["month"] == 11) & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["new_category", "amount"]].groupby(["new_category"]).sum().reset_index()
    axs[1, 1].set_title("november")
    axs[1, 1].bar(alfa["new_category"], alfa["amount"])
    axs[1, 1].set_xticklabels(alfa["new_category"], rotation=90)
    axs[1, 1].grid(True)

    # expenses by month
    filtered_df = edited_df[(edited_df["type"] == "expense") & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["amount", "month"]].groupby(["month"]).sum().reset_index()
    axs[1, 2].set_title("total expenses by month")
    axs[1, 2].bar(alfa["month"], alfa["amount"])
    axs[1, 2].grid(True)

    # income
    filtered_df = edited_df[(edited_df["type"] == "income") & (edited_df["description"] != "TRAN.CTAS.PROP.BM")]
    alfa = filtered_df[["amount", "month"]].groupby(["month"]).sum().reset_index()
    axs[2, 0].set_title("total income by month")
    axs[2, 0].bar(alfa["month"], alfa["amount"])
    axs[2, 0].grid(True)

    plt.subplots_adjust(hspace=0.6)
    return fig


# ======================= over the edited_df =======================


def get_count(edited_df):
    return (edited_df["story"] == "").sum()


def save_df(edited_df):

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    edited_df[story_columns].to_csv(story_table_str, index=False)
    edited_df[story_columns].to_csv(
        f"/mnt/c/Users/josue/Desktop/reports/personal information {now}.csv",
        index=False,
    )


def update_requires_update_column(edited_df):
    edited_df["requires_update"] = edited_df.apply(lambda x: not (x.category == x.new_category), axis=1)
