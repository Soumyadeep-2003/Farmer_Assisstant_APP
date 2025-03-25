import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_health_history(data):
    """
    Create a line plot of crop health history
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['ndvi'],
        mode='lines+markers',
        name='Health Score',
        line=dict(color='#4CAF50', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Crop Health History',
        xaxis_title='Date',
        yaxis_title='Health Score (NDVI)',
        template='plotly_white',
        height=400
    )
    
    return fig

def plot_health_metrics(data):
    """
    Create a dashboard of health metrics
    """
    # Calculate stress level distribution
    stress_dist = data['stress_level'].value_counts()
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=stress_dist.index,
        values=stress_dist.values,
        hole=0.4,
        marker_colors=['#4CAF50', '#FFC107', '#F44336']
    ))
    
    fig.update_layout(
        title='Stress Level Distribution',
        template='plotly_white',
        height=400,
        showlegend=True
    )
    
    return fig
