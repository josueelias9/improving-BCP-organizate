import streamlit as st
from io import StringIO
import mediator


st.set_page_config(layout="wide")


st.title('Improving "BCP organizate"')

st.image("BCP.png", caption="BCP")

uploaded_file = st.file_uploader("Load the html from BCP")

if uploaded_file is not None:
    # To read file as string:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    mediator.ETL_transaction(string_data)


if mediator.create_if_doesnt_exist()["type"] == "success":

    st.title("Edit you story")
    st.write("Edit the story of each transaction. Order by `date_id`.")

    edited_df = st.data_editor(
        mediator.create_merged_df(),
        column_order=(
            "date",
            "description",
            "type",
            "amount",
            "date_id",
            "story",
            "requires_update",
            "new_category",
        ),
        hide_index=True,
        column_config={
            "story": st.column_config.TextColumn(
                help="Streamlit **widget** commands 🎈",
                width="large",
                max_chars=500,
            ),
            "requires_update": st.column_config.CheckboxColumn(
                help="Select your **favorite** widgets",
                width="small",
            ),
            "new_category": st.column_config.SelectboxColumn(
                help="The category of the app",
                width="medium",
                options=mediator.get_categories(),
                required=True,
            ),
        },
        use_container_width=True,
    )
    # count how many empty strings are ing the "story" column
    st.write(f"missing stories: {mediator.get_count(edited_df)}")

    mediator.update_requires_update_column(edited_df)

    if st.button("Save data"):
        mediator.save_df(edited_df)
        st.write("data to database")

    st.title("Overview")

    # graphs!
    fig = mediator.make_graphs(edited_df)
    st.pyplot(fig, use_container_width=False)

    st.title("Filter by month, type and category")
    # dataframe
    col1, col2, col3 = st.columns(3)
    with col1:
        option1 = st.selectbox(
            "Select month",
            tuple(mediator.get_months()) + ("all",),
        )

    with col2:
        option2 = st.selectbox(
            "Select type",
            ("expense", "income") + ("all",),
        )

    with col3:
        option3 = st.selectbox("select category", tuple(mediator.get_categories()) + ("all",))

    condition = True

    if option1 != "all":
        condition &= edited_df["month"] == option1
    if option2 != "all":
        condition &= edited_df["type"] == option2
    if option3 != "all":
        condition &= edited_df["new_category"] == option3

    condition &= edited_df["description"] != "TRAN.CTAS.PROP.BM"

    st.dataframe(
        edited_df[condition],
        use_container_width=True,
    )

else:
    st.header("Upload the html from BCP")
