
import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Warehouse Management System",
    layout="wide"
)

BACKEND_URL = "https://effective-sniffle-xrwwvqp7p4v72vgwx-3000.app.github.dev"


# ---------------- API FUNCTIONS ----------------

def get_data():
    try:
        response = requests.get(
            f"{BACKEND_URL}/items",
            timeout=15
        )
        response.raise_for_status()

        return pd.DataFrame(response.json())

    except requests.RequestException as e:
        st.error(f"Backend connection error: {e}")

        return pd.DataFrame(
            columns=["id", "name", "location"]
        )


def add_item(name, location):
    return requests.post(
        f"{BACKEND_URL}/items",
        json={
            "name": name,
            "location": location
        },
        timeout=15
    )


def update_item(item_id, name, location):
    return requests.put(
        f"{BACKEND_URL}/items/{item_id}",
        json={
            "name": name,
            "location": location
        },
        timeout=15
    )


def delete_item(item_id):
    return requests.delete(
        f"{BACKEND_URL}/items/{item_id}",
        timeout=15
    )


# ---------------- SESSION STATE ----------------

if "success_message" not in st.session_state:
    st.session_state.success_message = None


# ---------------- SIDEBAR ----------------

st.sidebar.title("Warehouse Management")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Add Item",
        "Edit Item",
        "Remove Item"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption("Warehouse Inventory System")


# ---------------- SUCCESS MESSAGE ----------------

if st.session_state.success_message:

    st.success(st.session_state.success_message)

    st.session_state.success_message = None


# ---------------- HOME PAGE ----------------

if page == "Home":

    st.title("Warehouse management system")

    df = get_data()

    search_query = st.text_input(
        "Search by Name or Location",
        ""
    )

    if not df.empty:

        filtered_dataframe = df[
            df["name"].astype(str).str.contains(
                search_query,
                case=False,
                na=False
            ) |
            df["location"].astype(str).str.contains(
                search_query,
                case=False,
                na=False
            )
        ] if search_query else df

        st.write(
            f"Showing {len(filtered_dataframe)} items"
        )

        st.dataframe(
            filtered_dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.write("Showing 0 items")

        st.warning(
            "No data found or backend is offline."
        )

    if st.button("Refresh Inventory"):

        st.rerun()


# ---------------- ADD ITEM PAGE ----------------

elif page == "Add Item":

    st.title("Add New Item")

    st.write(
        "Enter the details of the new warehouse item."
    )

    with st.form("add_item_form"):

        name = st.text_input("Item Name")

        location = st.text_input(
            "Warehouse Location"
        )

        submit = st.form_submit_button(
            "Add Item",
            type="primary"
        )

        if submit:

            if not name.strip() or not location.strip():

                st.error(
                    "Please fill in all fields."
                )

            else:

                try:

                    response = add_item(
                        name.strip(),
                        location.strip()
                    )

                    if response.status_code == 201:

                        st.session_state.success_message = (
                            "Item added successfully! "
                            "Your inventory has been updated."
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"Error: {response.text}"
                        )

                except requests.RequestException as e:

                    st.error(
                        f"Error adding item: {e}"
                    )


# ---------------- EDIT ITEM PAGE ----------------

elif page == "Edit Item":

    st.title("Edit Existing Item")

    df = get_data()

    if not df.empty:

        item_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select Item ID",
            item_ids
        )

        selected_item = df[
            df["id"] == selected_id
        ].iloc[0]

        with st.form("edit_item_form"):

            new_name = st.text_input(
                "Item Name",
                value=str(selected_item["name"])
            )

            new_location = st.text_input(
                "Warehouse Location",
                value=str(selected_item["location"])
            )

            submit = st.form_submit_button(
                "Update Item",
                type="primary"
            )

            if submit:

                if (
                    not new_name.strip()
                    or not new_location.strip()
                ):

                    st.error(
                        "Please fill in all fields."
                    )

                else:

                    try:

                        response = update_item(
                            selected_id,
                            new_name.strip(),
                            new_location.strip()
                        )

                        if response.status_code == 200:

                            st.session_state.success_message = (
                                "Item updated successfully!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                f"Error: {response.text}"
                            )

                    except requests.RequestException as e:

                        st.error(
                            f"Error updating item: {e}"
                        )

    else:

        st.warning(
            "No items available to edit."
        )


# ---------------- REMOVE ITEM PAGE ----------------

elif page == "Remove Item":

    st.title("Remove Item")

    df = get_data()

    if not df.empty:

        selected_id = st.selectbox(
            "Select Item ID to Remove",
            df["id"].tolist()
        )

        selected_item = df[
            df["id"] == selected_id
        ].iloc[0]

        st.write("### Selected Item Details")

        st.write(
            f"**Item Name:** {selected_item['name']}"
        )

        st.write(
            f"**Location:** {selected_item['location']}"
        )

        st.warning(
            "This action cannot be undone!"
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this item."
        )

        if st.button(
            "Delete Item",
            type="primary"
        ):

            if confirm:

                try:

                    response = delete_item(selected_id)

                    if response.status_code == 200:

                        st.session_state.success_message = (
                            "Item deleted successfully!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            f"Error: {response.text}"
                        )

                except requests.RequestException as e:

                    st.error(
                        f"Error deleting item: {e}"
                    )

            else:

                st.error(
                    "Please confirm deletion first."
                )

    else:

        st.warning(
            "No items available to remove."
        )
