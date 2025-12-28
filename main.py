from streamlit_option_menu import option_menu

selected = option_menu(
    "メニュー",
    ["Home", "Profile", "Settings", "About", "More1", "More2", "More3"],
    styles={
        "container": {
            "max-height": "200px",
            "overflow-y": "auto",
            "width": "240px",
            "padding": "0.5rem"
        },
        "nav": {
            "padding": "0.25rem"
        }
    },
    key="my_menu"
)
