import plotly.express as px

# Load stock data as a DataFrame and set the date as the index
df = px.data.stocks(indexed=True)["MSFT"].reset_index()

# Create a bar chart using Plotly Express
fig = px.line(df, x="date", y="MSFT", title="Google Stock Prices Over tiiiiiiime")

# Show the figure
fig.show()

# Save the figure as an HTML file
try:
    fig.write_html("/var/www/html/pyethone/scripts/plotly/plot.html")
    print("Plot generation successful.")
except Exception as e:
    print(f"Error writing HTML file: {e}")

print("Plot generation successful.")