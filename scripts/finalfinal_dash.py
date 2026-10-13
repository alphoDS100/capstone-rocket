# Import Libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataframe
df =  pd.read_csv('spacex_launch_dash.csv')

# Get the launch sites
launch_sites = sorted(df["Launch Site"].dropna().unique())

# Payload limits
min_payload = df["Payload Mass (kg)"].min()
max_payload = df["Payload Mass (kg)"].max()

# Dash app
app = dash.Dash(__name__)

# Dropdown options
dropdown_options = [
    {"label": "All Launch Sites", "value": "ALL"}
] + [
    {"label": site, "value": site}
    for site in launch_sites
]

app.layout = html.Div([
    html.H1("Launch Site Success Analysis"),

    html.Label("Select a Launch Site:"),

    dcc.Dropdown(
        id="site-dropdown",
        options=dropdown_options,
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    dcc.Graph(id="success-pie-chart"),

    # Payload Range Slider
    html.Label("Select Payload Mass Range (kg):"),
    dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={
                0: "0",
                2000: "2,000",
                4000: "4,000",
                6000: "6,000",
                8000: "8,000",
                10000: "10,000"
            },
            tooltip={
                "placement": "bottom",
                "always_visible": True
            }
        ),

    html.Br(),

    html.Br(),

    dcc.Graph(id="success-payload-scatter-chart"),

])

@app.callback(
Output(
            component_id="success-pie-chart", component_property="figure"
        ),

        [
        Input(
            component_id="site-dropdown", component_property="value"
        ),
        Input(
            component_id="payload-slider", component_property="value"
        )
        ]
    )
def update_dashboard(selected_site, payload_range):
    min_payload_selected = payload_range[0]
    max_payload_selected = payload_range[1]

    # Filter by payload range
    filtered_df = df[
        (df["Payload Mass (kg)"] >= min_payload_selected) &
        (df["Payload Mass (kg)"] <= max_payload_selected)
        ].copy()

    # Filter by launch site
    if selected_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == selected_site
            ]

    # ALL launch sites pie chart
    if selected_site == "ALL":

        success_by_site = (
            filtered_df[filtered_df["class"] == 1]
            .groupby("Launch Site")
            .size()
            .reset_index(name="Successes")
        )

        if len(success_by_site) > 0:

            fig_pie = px.pie(
                success_by_site,
                names="Launch Site",
                values="Successes",
                title="Successful Launches by Site"
            )

        else:
            fig_pie = px.pie(
                title="No Successful Launches in Selected Range"
            )

    # Individual launch site pie chart
    else:

        class_counts = (
            filtered_df["class"]
            .value_counts()
            .reindex([0, 1], fill_value=0)
        )

        chart_df = pd.DataFrame({
            "Class": [
                "Failure (class=0)",
                "Success (class=1)"
            ],
            "Count": [
                class_counts[0],
                class_counts[1]
            ]}
        )

        fig_pie = px.pie(
            chart_df,
            names="Class",
            values="Count",
            title=f"Successful vs. Failed Launches — {selected_site}",
            color="Class",
            color_discrete_map={
                "Failure (class=0)": "red",
                "Success (class=1)": "blue"
            }
        )

    return fig_pie

@app.callback(
Output(
        component_id="success-payload-scatter-chart",
        component_property="figure"
        ),
        [
        Input(
            component_id="site-dropdown",
            component_property="value"
        ),
        Input(
            component_id="payload-slider",
            component_property="value"
            )
        ]
)
def update_success_payload_scatter(selected_site, payload_range):

    # Filter by selected payload range
    filtered_df = df[
        (df["Payload Mass (kg)"] >= payload_range[0]) &
        (df["Payload Mass (kg)"] <= payload_range[1])
    ].copy()

    # Check whether ALL sites or a specific site
    if selected_site == "ALL":

        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Payload Mass vs. Mission Outcome — All Launch Sites",
            labels={
                "Payload Mass (kg)": "Payload Mass (kg)",
                "class": "Mission Outcome"
            },
            hover_data=[
                "Launch Site",
                "Booster Version Category"
            ]
        )

    else:

        # Filter dataframe for selected launch site
        site_df = filtered_df[
            filtered_df["Launch Site"] == selected_site
        ]

        fig = px.scatter(
            site_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=(
                f"Payload Mass vs. Mission Outcome — "
                f"{selected_site}"
            ),
            labels={
                "Payload Mass (kg)": "Payload Mass (kg)",
                "class": "Mission Outcome"
            },
            hover_data=[
                "Launch Site",
                "Booster Version Category"
            ]
        )

    return fig


# Run the application
if __name__ == "__main__":
    app.run(debug=True)