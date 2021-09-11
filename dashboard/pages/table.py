import pandas as pd
from dash import Dash
from dash.dash_table import DataTable
from dash.dependencies import Input, Output


layout = DataTable(
    id="table",
    columns=[
        {"name": "url", "id": "url"},
        {"name": "usable_area", "id": "usable_area"},
        {"name": "type_unit", "id": "type_unit"},
        {"name": "total_fee", "id": "total_fee"},
        {"name": "estacao", "id": "estacao"},
        {"name": "distance", "id": "distance"},
    ],
    style_header={"fontWeight": "bold"},
    page_current=0,
    page_size=25,
    page_action="custom",
    sort_action="custom",
    sort_mode="multi",
    sort_by=[],
    style_cell={"textOverflow": "ellipsis"},
    style_cell_conditional=[
        {"if": {"column_id": "url"}, "maxWidth": 50, "textAlign": "left"},
        {"if": {"column_id": "usable_area"}, "maxWidth": 20},
        {"if": {"column_id": "type_unit"}, "maxWidth": 20, "textAlign": "left"},
        {"if": {"column_id": "total_fee"}, "maxWidth": 20},
        {"if": {"column_id": "estacao"}, "maxWidth": 50, "textAlign": "left"},
        {"if": {"column_id": "distance"}, "maxWidth": 20},
    ],
)


def init_app(app: Dash) -> Dash:
    @app.callback(
        Output("table", "data"),
        Input("filtered_data", "data"),
        Input("table", "sort_by"),
        Input("table", "page_current"),
        Input("table", "page_size"),
    )
    def updateTable(data, sort_by, page_current, page_size):
        dff = pd.DataFrame(data)

        if dff.shape[0] == 0:
            return []

        dff["distance"] = dff["distance"].round(0)

        if len(sort_by):
            dff = dff.sort_values(
                [col["column_id"] for col in sort_by],
                ascending=[col["direction"] == "asc" for col in sort_by],
            )

        return dff.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")

    return app
