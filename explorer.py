import panel as pn
from api import API
import sankey as sk

# Loads JavaScript dependencies and configures Panel (required)
pn.extension()

# Initialize API and load dataset
api = API()
api.load_stats('2023-2024 NBA Player Stats - Regular.csv')

# WIDGET DECLARATIONS

# Min Points Filter (to exclude small contributions)
min_scored = pn.widgets.IntSlider(name="Min Points Per Game", start=0, end=40, step=1, value=3)

# Plotting Controls
width = pn.widgets.IntSlider(name="Width", start=250, end=2000, step=250, value=1000)
height = pn.widgets.IntSlider(name="Height", start=200, end=2500, step=100, value=1000)

# Dropdown for Team Selection
teams = sorted(api.stats['Tm'].dropna().unique())
team_selector = pn.widgets.Select(name="Team", options=["All"] + teams, value="All")

# Checkbox Group for Position Filtering
positions = sorted(api.get_position())
position_selector = pn.widgets.CheckBoxGroup(name="Positions", options=positions, value=positions)


# CALLBACK FUNCTIONS

def get_catalog(min_scored, team, positions):
    """ Generate table showing Player → Shot Type → Points flow with filters. """
    global local
    local = api.extract_local_network()

    # Multiply shots by their respective point values
    shot_values = {"3P": 3, "2P": 2, "FT": 1}
    local["Points"] = local["Shot Type"].map(shot_values) * local["Points"]

    # Apply filter on actual points per game using the PTS column
    player_pts = api.stats.set_index("Player")["PTS"]
    filtered_players = player_pts[player_pts >= min_scored].index
    local = local[local["Player"].isin(filtered_players)]

    # Apply additional filters
    if team != "All":
        local = local[local["Player"].isin(api.stats.loc[api.stats['Tm'] == team, "Player"])]

    if positions:
        local = local[local["Player"].isin(api.stats.loc[api.stats['Pos'].isin(positions), "Player"])]

    table = pn.widgets.Tabulator(local, selectable=False)
    return table


def get_plot(min_scored, width, height, team, positions):
    """ Generate Sankey Diagram for Player → Shot Type → Points with filters. """
    return sk.make_sankey(local, "Player", "Shot Type", vals="Points", width=width, height=height)


# CALLBACK BINDINGS
catalog = pn.bind(get_catalog, min_scored, team_selector, position_selector)
plot = pn.bind(get_plot, min_scored, width, height, team_selector, position_selector)

# DASHBOARD WIDGET CONTAINERS ("CARDS")

card_width = 320

filter_card = pn.Card(
    pn.Column(
        min_scored,
        team_selector,
        position_selector,
    ),
    title="Filters", width=card_width, collapsed=False
)

# LAYOUT

layout = pn.template.FastListTemplate(
    title="NBA Scoring Flow Analysis",
    sidebar=[
        filter_card,
    ],
    theme_toggle=False,
    main=[
        pn.Tabs(
            ("Scoring Table", catalog),
            ("Scoring Flow", plot),
            active=1
        )
    ],
    header_background='#a93226'
).servable()

layout.show()
