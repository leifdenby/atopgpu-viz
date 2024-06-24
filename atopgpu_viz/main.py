import pandas as pd

import panel as pn
import holoviews as hv
from holoviews import opts

import datasource

hv.extension("bokeh")


def create_app():

    # Create a Select widget
    variable_select = pn.widgets.Select(
        name="Variable", options=datasource.DATA_COLUMNS, value=datasource.DATA_COLUMNS[0]
    )
    
    # create a date selector
    calendar = pn.widgets.DatePicker(name="Date", value=pd.Timestamp.now(), end=pd.Timestamp.now().date())

    # Create a dynamic map that updates the plot based on the selected variable
    @pn.depends(variable_select.param.value, calendar.param.value)
    def create_plot(variable, date):
        # Create a DataFrame
        df = datasource.get_data(date=date)
        unique_gpus = df["busaddr"].unique()

        # Create a curve for each GPU
        curves = []
        for gpu in unique_gpus:
            df_gpu = df[df["busaddr"] == gpu]
            curves.append(hv.Curve(df_gpu, "time", variable, label=f"GPU: {gpu}"))

        # include legend in plot
        return hv.Overlay(curves).opts(
            width=600, height=400, title="GPU Utilization", legend_position="right"
        )

    # Create a Panel application
    app = pn.Row(pn.Column(calendar, variable_select), create_plot)
    
    return app


app = create_app()
app.servable(title="GPU utilization")