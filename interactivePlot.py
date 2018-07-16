# Load pandas library
import pandas as pd

# Import the necessary modules for bokeh plotting
from bokeh.io import curdoc
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper, ColorBar,
    LogTicker, Span, Label
)
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Magma256  as palette
palette.reverse()

# Import the necessary modules to add interactions
from bokeh.layouts import row, column, widgetbox
from bokeh.models import Slider

# read Sports Capital Allotment data
df = pd.read_json("data/SportsCapital.json")

# read gdp data
gdp = pd.read_csv("data/gdp.csv", dtype={'Year': object})

# Get the maximum capital Allocated for the counties
max_a=df.iloc[:,:17].max().max()

# Set min to 1 as log sclaing starts here
min_a=1  # df.iloc[:,:17].min().min()

# Extract total for each Year
tot = df.sum()[:17]

# Fill Missing Values with ""(Bokeh specification)
df.fillna("", inplace=True)

######################### Plotting Choropleth map
# Create a ColumnDataSource: source
source1 = ColumnDataSource(data=dict(
    x       =   list(df.lat),
    y       =   list(df.lon),
    name    =   list(df.County),
    Amount  =   list(df["2000"]),
))

# Define Color Scheme for color bar
color_mapper = LogColorMapper(palette=palette,low=min_a,high=max_a)

color_bar = ColorBar(color_mapper=color_mapper, ticker=LogTicker(),
                major_tick_out=0, major_tick_in=0, major_label_text_align='left',
                major_label_text_font_size='10pt', label_standoff=2, border_line_color=None, location=(0,0))

# Create the figure: plot
TOOLS = "pan,wheel_zoom,reset,hover,save"

p1 = figure(
    title="Ireland Sports Capital Allotment",
    tools=TOOLS,plot_height =600, plot_width =600,
    x_axis_location=None, y_axis_location=None, toolbar_location="left"
)
p1.title.text_font_size = '15pt'
p1.grid.grid_line_color = None

# Add patches glyphs to the plot
p1.patches('x', 'y', source=source1,
          fill_color={'field': 'Amount', 'transform': color_mapper},
          fill_alpha=0.7, line_color="black", line_width=0.5)

# Add hover to the plot
hover = p1.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@name"),
    ("Amount Allocated in Euros)", "@Amount"),
    ("(Long, Lat)", "($x, $y)"),
]

# Add a color bar to represent the numeric scale
p1.add_layout(color_bar, 'right')
################### Plotting line graph

# Create a ColumnDataSource: source
source2 = ColumnDataSource(data=dict(
    x       =   gdp['Year'],
    y_gdp   =   gdp['value'],
    y_stot  =   tot.values/10**6,
))

# define HoverTool
hv = HoverTool(
    tooltips=[
        ( 'Year',   '@x'            ),
        ( 'GDP',  '@y_gdp Billion US$' ), # use @{ } for field names with spaces
        ( 'Sports Capital Allotted', '@y_stot Million Euros'      ),
    ],

    # display a tooltip whenever the cursor is vertically in line with a glyph
    mode='mouse'
)

# draw a line-plot for GDP
p2 = figure(x_axis_label="Year", title="GDP of Ireland",tools=["pan,wheel_zoom,reset,save",hv],
            plot_height =500, plot_width =600)
p2.title.text_font_size = '15pt'
p2.grid.grid_line_alpha=0.3
p2.xaxis.axis_label = 'Year'
p2.yaxis.axis_label = 'Amount'

# Add line graph and circle to each observation
p2.line("x","y_gdp",source = source2, color='red')
p2.circle("x","y_gdp",source = source2, color='red',size=16, fill_alpha=0.1)
p2.line("x","y_stot",source = source2, color='blue')
p2.triangle("x","y_stot",source = source2, color='blue',size=16, fill_alpha=0.1)

# Add Legend near the line
L1 = Label(x=2011,y=203,text='GDP in Billion US$',text_color='red')
L2 = Label(x=2009,y=55,text='Sports Capital in Million Euros',text_color='blue')
p2.add_layout(L1)
p2.add_layout(L2)

source3 = ColumnDataSource(data=dict(
        x   =   ['2000'],
        y   =   [0],
))
p2.ray('x', 'y', source = source3, length=16, angle=1.57079633, color='black')


################### Code to add interaction

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # set the `yr` name to `slider.value` and `source.data = new_data`
    yr = slider.value
    new_data1 = dict(
        x       =   list(df.lat),
        y       =   list(df.lon),
        name    =   list(df.County),
        Amount  =   list(df['%d' % yr]),
    )
    source1.data = new_data1
    # Add title to map
    p1.title.text = 'Ireland Sports Capital Allotment for %d' % yr

    new_data3 = dict(
        x       =   ['%d' % yr],
        y       =   [0],
    )
    source3.data = new_data3
    # Add title to line-plot
    p2.title.text = 'Ireland GDP for %d' % yr


# Make a slider object: slider
slider = Slider(start = 2000, end = 2016, step = 1,value = 2000, title='Year')

# Attach the callback to the 'value' property of slider
slider.on_change('value',update_plot)

# Make a row layout of widgetbox(slider) and plot and add it to the current document
layout = row(p1,column(widgetbox(slider),p2))
curdoc().add_root(layout)
curdoc().title = 'Ireland Sports Capital Allotment'
