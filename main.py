import joblib
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import row, column, layout
from bokeh.models import Select, ColumnDataSource, Div, Range, HoverTool, Legend, RangeSlider, Range1d, LinearAxis
from bokeh.plotting import figure
from bokeh.models.widgets import Panel, Tabs
from bokeh.themes import Theme
from sqlalchemy import create_engine
from os.path import join, dirname

# COVID-19 data
df = joblib.load('data/processed/covid.pkl')
sp = joblib.load('data/processed/sp500.pkl')
sp['date'] = pd.to_datetime(sp['date'])

# SARS data
sars = joblib.load('data/processed/sars.pkl')
sp_sars = joblib.load('data/processed/sp500_sars.pkl')
sp_sars['date'] = pd.to_datetime(sp_sars['date'])


# Constants
plot_width = 1200
plot_height = 600

# Outbreak tooltips
TOOLTIPS = [
    ('Date', '@date{%F}'),
    ('Value', '@cases{int}'),
    ('S&P500 Index', '@close{int}')
]
outbreak_hover = HoverTool(
    tooltips=TOOLTIPS,
    formatters={
        '@date': 'datetime'
    },
    mode='vline'
)

# Outbreak Graph
ob_cases_ds = ColumnDataSource(data=dict(date=[], cases=[]))
outbreak = figure(title='Outbreak', x_axis_type='datetime',
                  plot_height=plot_height, plot_width=plot_width, y_axis_label='# Cases',
                  y_range=(0, 100))
ob1 = outbreak.line(x='date', y='cases', source=ob_cases_ds, legend_label='ob1',
                    line_width=2, line_color='blue')
outbreak.add_tools(outbreak_hover)
outbreak.xaxis.major_label_orientation = 3.14 / 4

# Add second graph to fig
sp500_cs = ColumnDataSource(data=dict(date=[], close=[]))
sp500_cs.data = dict(
    date=sp['date'],
    close=sp['close']
)
outbreak.extra_y_ranges = {'SP500': Range1d(start=sp.close.min(), end=sp.close.max())}
outbreak.add_layout(LinearAxis(y_range_name='SP500', axis_label='S&P Index'), 'right')
sp5 = outbreak.line(x='date', y='close', source=sp500_cs, line_color='black', y_range_name='SP500',
                    legend_label='S&P500')

legend = Legend(items=[
    ('Cases', [ob1]),
    ('S&P500', [sp5])
])

# Measure dict for stylistic purposes
measure_dict = {
    'New Cases': 'cases',
    'New Deaths': 'deaths',
    'Cases, Running total': 'running_cases',
    'Deaths, Running total': 'running_death'
}

# Graph legend location
outbreak.legend.location = 'top_left'

def update():
    if disease_select.value == 'COVID-19':
        ob_cases_ds.data = dict(
            date=df[df['countriesAndTerritories'] == country_select.value]['dateRep'],
            cases=df[df['countriesAndTerritories'] == country_select.value][measure_dict[measure_select.value]]
        )
        outbreak.title.text = 'COVID-19: ' + measure_select.value

        outbreak.legend.items= [
            (measure_select.value, [ob1]),
            ('S&P500', [sp5])
        ]

        sp500_cs.data = dict(
            date=sp['date'],
            close=sp['close']
        )

        outbreak.y_range.start = df[df['countriesAndTerritories'] == country_select.value][
            measure_dict[measure_select.value]].min()
        outbreak.y_range.end = df[df['countriesAndTerritories'] == country_select.value][
            measure_dict[measure_select.value]].max()
        outbreak.extra_y_ranges['SP500'].start = sp.close.min()
        outbreak.extra_y_ranges['SP500'].end = sp.close.max()

    if disease_select.value == 'SARS':
        ob_cases_ds.data = dict(
            date=sars[sars['countriesAndTerritories'] == country_select.value]['dateRep'],
            cases=sars[sars['countriesAndTerritories'] == country_select.value][measure_dict[measure_select.value]]
        )
        outbreak.title.text = 'SARS: ' + measure_select.value

        outbreak.legend.items = [
            (measure_select.value, [ob1]),
            ('S&P500', [sp5])
        ]

        sp500_cs.data = dict(
            date=sp_sars['date'],
            close=sp_sars['close']
        )

        outbreak.extra_y_ranges['SP500'].start = sp_sars.close.min()
        outbreak.extra_y_ranges['SP500'].end = sp_sars.close.max()
        outbreak.y_range.start = sars[sars['countriesAndTerritories'] == country_select.value][measure_dict[measure_select.value]].min()
        outbreak.y_range.end = sars[sars['countriesAndTerritories'] == country_select.value][measure_dict[measure_select.value]].max()

    print('Updated')

    return True


# Filters
country_select = Select(title='Country', options=df.countriesAndTerritories.unique().tolist(), value='World')
measure_select = Select(title='Measure',
                        options=['New Cases', 'New Deaths', 'Deaths, Running total', 'Cases, Running total'],
                        value='New Cases')
disease_select = Select(title='Disease', options=['COVID-19', 'SARS'], value='COVID-19')

filters = [country_select, measure_select, disease_select]
for filter in filters:
    filter.on_change('value', lambda attr, new, old: update())

filter_layout = column(filters, width=350, height=350, sizing_mode='fixed')

app_layout=layout([
    [filter_layout, outbreak]
    ]
    , sizing_mode = 'stretch_both'
)

update()

curdoc().add_root(app_layout)
curdoc().title = 'COVID-19'
