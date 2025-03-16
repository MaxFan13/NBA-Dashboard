import pandas as pd
import plotly.graph_objects as go

def make_sankey(df, *cols, vals=None, **kwargs):
    sankey_data = pd.DataFrame()
    for i in range(len(cols) - 1):
        src_col = cols[i]
        targ_col = cols[i + 1]

        temp = df.groupby([src_col, targ_col])[vals].sum().reset_index()
        temp.columns = ['src', 'targ', 'values']
        sankey_data = pd.concat([sankey_data, temp], ignore_index=True)

    labels = pd.concat([sankey_data['src'], sankey_data['targ']]).unique()
    label_dict = {label: idx for idx, label in enumerate(labels)}

    sankey_data['src'] = sankey_data['src'].map(label_dict)
    sankey_data['targ'] = sankey_data['targ'].map(label_dict)

    pad = kwargs.get('pad', 15)
    thickness = kwargs.get('thickness', 20)
    line_color = kwargs.get('line_color', 'black')
    line_width = kwargs.get('line_width', 1)

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=pad,
                    thickness=thickness,
                    line=dict(color=line_color, width=line_width),
                    label=labels,
                ),
                link=dict(
                    source=sankey_data['src'],
                    target=sankey_data['targ'],
                    value=sankey_data['values'],
                ),
            )
        ]
    )
    fig.update_layout()
    return fig

