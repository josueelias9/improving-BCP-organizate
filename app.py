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
    mediator.call_ETL(string_data)


if mediator.create_if_doesnt_exist()["type"] == "success":

    merged_df = mediator.create_merged_df()

    st.title("Edit you story")
    st.write("Edit the story of each transaction. Order by `date_id`.")

    edited_data = st.data_editor(
        merged_df,
        column_config={
            "story": {"editable": True},
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
    st.write(f'missing stories: {mediator.get_count(edited_data["story"])}')

    if st.button("Save data"):
        mediator.save_df(edited_data)
        st.write("data to database")

else:
    st.header("Upload the html from BCP")
