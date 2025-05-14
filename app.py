import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models.package import Package
from models.drone import Drone
from delivery_planner import DeliveryPlanner
import base64
import io

# Set page configuration
st.set_page_config(
    page_title="Drone Delivery System",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #cce5ff;
        color: #004085;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
    }
    </style>
    """, unsafe_allow_html=True)

def get_table_download_link(df, filename):
    """Generate a download link for a dataframe."""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'planner' not in st.session_state:
        st.session_state.planner = DeliveryPlanner()
    if 'drones' not in st.session_state:
        st.session_state.drones = []
    if 'packages' not in st.session_state:
        st.session_state.packages = []
    if 'delivery_plans' not in st.session_state:
        st.session_state.delivery_plans = []

def display_metrics(statistics):
    """Display metrics in a visually appealing way."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">Total Packages</div>
            </div>
        """.format(statistics['total_packages']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">${:.2f}</div>
                <div class="metric-label">Total Value</div>
            </div>
        """.format(statistics['total_value']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">{:.2f}</div>
                <div class="metric-label">Total Distance</div>
            </div>
        """.format(statistics['total_distance']), unsafe_allow_html=True)

def plot_delivery_statistics(statistics):
    """Create plots for delivery statistics."""
    # Create a bar chart for key metrics
    metrics = {
        'Total Packages': statistics['total_packages'],
        'Total Value ($)': statistics['total_value'],
        'Total Distance': statistics['total_distance']
    }
    
    fig = px.bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        title='Delivery Overview',
        labels={'x': 'Metric', 'y': 'Value'},
        color=list(metrics.values()),
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=20
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a pie chart for average metrics
    avg_metrics = {
        'Packages per Trip': statistics['average_packages_per_trip'],
        'Value per Trip ($)': statistics['average_value_per_trip'],
        'Distance per Trip': statistics['average_distance_per_trip']
    }
    
    fig2 = px.pie(
        values=list(avg_metrics.values()),
        names=list(avg_metrics.keys()),
        title='Average Metrics per Trip'
    )
    fig2.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=20
    )
    st.plotly_chart(fig2, use_container_width=True)

def plot_package_distribution(packages):
    """Create plots for package distribution."""
    # Create a scatter plot of package weight vs value
    fig = px.scatter(
        packages,
        x='Weight',
        y='Value',
        color='Destination',
        size='Weight',
        title='Package Weight vs Value Distribution',
        labels={'Weight': 'Weight (kg)', 'Value': 'Value ($)'}
    )
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=20
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a bar chart of packages by destination
    dest_counts = pd.DataFrame(packages)['Destination'].value_counts()
    fig2 = px.bar(
        x=dest_counts.index,
        y=dest_counts.values,
        title='Packages by Destination',
        labels={'x': 'Destination', 'y': 'Number of Packages'}
    )
    fig2.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=20
    )
    st.plotly_chart(fig2, use_container_width=True)

def plot_route_network(planner):
    """Create a network graph of the delivery routes."""
    # Create nodes and edges for the network
    nodes = list(planner.cities.keys())
    edges = []
    for city1 in planner.cities:
        for city2, route in planner.cities[city1].connections.items():
            if route.is_active:
                edges.append((city1, city2, route.distance))
    
    # Create the network graph
    fig = go.Figure()
    
    # Add edges
    for edge in edges:
        fig.add_trace(go.Scatter(
            x=[nodes.index(edge[0]), nodes.index(edge[1])],
            y=[0, 0],  # Simple layout for now
            mode='lines+markers+text',
            line=dict(width=edge[2]/5),  # Line width based on distance
            marker=dict(size=10),
            text=[edge[0], edge[1]],
            textposition="top center",
            name=f"{edge[0]}-{edge[1]}"
        ))
    
    fig.update_layout(
        title='Delivery Network',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        template='plotly_white',
        title_x=0.5,
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def add_city():
    """Add a new city to the delivery network."""
    st.subheader("Add New City")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            city_name = st.text_input("City Name")
        with col2:
            has_charging = st.checkbox("Has Charging Station")
        
        if st.button("Add City"):
            if city_name:
                st.session_state.planner.add_city(city_name, has_charging)
                st.markdown(f"""
                    <div class="success-box">
                        City {city_name} added successfully!
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="error-box">
                        Please enter a city name
                    </div>
                """, unsafe_allow_html=True)
    
    # Show network visualization
    if len(st.session_state.planner.cities) > 0:
        st.subheader("Current Network")
        plot_route_network(st.session_state.planner)

def add_route():
    """Add a new route between cities."""
    st.subheader("Add New Route")
    cities = list(st.session_state.planner.cities.keys())
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            city1 = st.selectbox("From City", cities)
        with col2:
            city2 = st.selectbox("To City", cities)
        with col3:
            distance = st.number_input("Distance", min_value=0.1, step=0.1)
        
        if st.button("Add Route"):
            if city1 != city2:
                st.session_state.planner.add_route(city1, city2, distance)
                st.markdown(f"""
                    <div class="success-box">
                        Route from {city1} to {city2} added successfully!
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="error-box">
                        Please select different cities
                    </div>
                """, unsafe_allow_html=True)
    
    # Show network visualization
    if len(st.session_state.planner.cities) > 0:
        st.subheader("Current Network")
        plot_route_network(st.session_state.planner)

def manage_drones():
    """Add and manage drones."""
    st.subheader("Manage Drones")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            drone_id = st.number_input("Drone ID", min_value=1, step=1)
        with col2:
            max_weight = st.number_input("Max Weight", min_value=0.1, step=0.1)
        with col3:
            max_distance = st.number_input("Max Distance", min_value=0.1, step=0.1)
        
        if st.button("Add Drone"):
            try:
                drone = Drone(drone_id, max_weight, max_distance)
                st.session_state.drones.append(drone)
                st.markdown(f"""
                    <div class="success-box">
                        Drone {drone_id} added successfully!
                    </div>
                """, unsafe_allow_html=True)
            except ValueError as e:
                st.markdown(f"""
                    <div class="error-box">
                        {str(e)}
                    </div>
                """, unsafe_allow_html=True)
    
    # Display existing drones
    if st.session_state.drones:
        st.write("Existing Drones:")
        drones_df = pd.DataFrame([
            {
                'ID': drone.id,
                'Max Weight': drone.max_weight,
                'Max Distance': drone.max_distance,
                'Status': drone.status
            }
            for drone in st.session_state.drones
        ])
        st.dataframe(drones_df, use_container_width=True)
        
        # Create drone capability visualization
        fig = px.scatter(
            drones_df,
            x='Max Weight',
            y='Max Distance',
            size='Max Weight',
            color='ID',
            title='Drone Capabilities',
            labels={'Max Weight': 'Max Weight (kg)', 'Max Distance': 'Max Distance (km)'}
        )
        fig.update_layout(
            template='plotly_white',
            title_x=0.5,
            title_font_size=20
        )
        st.plotly_chart(fig, use_container_width=True)

def manage_packages():
    """Add and manage packages."""
    st.subheader("Manage Packages")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            package_id = st.number_input("Package ID", min_value=1, step=1)
        with col2:
            weight = st.number_input("Weight", min_value=0.1, step=0.1)
        with col3:
            value = st.number_input("Value", min_value=0.0, step=0.1)
        with col4:
            destination = st.selectbox("Destination", list(st.session_state.planner.cities.keys()))
        
        if st.button("Add Package"):
            try:
                package = Package(package_id, weight, value, destination)
                st.session_state.packages.append(package)
                st.markdown(f"""
                    <div class="success-box">
                        Package {package_id} added successfully!
                    </div>
                """, unsafe_allow_html=True)
            except ValueError as e:
                st.markdown(f"""
                    <div class="error-box">
                        {str(e)}
                    </div>
                """, unsafe_allow_html=True)
    
    # Display existing packages
    if st.session_state.packages:
        st.write("Existing Packages:")
        packages_df = pd.DataFrame([
            {
                'ID': package.id,
                'Weight': package.weight,
                'Value': package.value,
                'Destination': package.destination,
                'Status': package.status
            }
            for package in st.session_state.packages
        ])
        st.dataframe(packages_df, use_container_width=True)
        
        # Show package distribution plots
        st.subheader("Package Distribution")
        plot_package_distribution(packages_df)

def plan_deliveries():
    """Plan and display delivery routes."""
    st.subheader("Plan Deliveries")
    
    if not st.session_state.drones or not st.session_state.packages:
        st.markdown("""
            <div class="info-box">
                Please add at least one drone and one package first
            </div>
        """, unsafe_allow_html=True)
        return
    
    if st.button("Plan Deliveries"):
        try:
            st.session_state.delivery_plans = st.session_state.planner.plan_delivery(
                st.session_state.packages,
                st.session_state.drones
            )
            
            if not st.session_state.delivery_plans:
                st.markdown("""
                    <div class="info-box">
                        No feasible delivery plans found
                    </div>
                """, unsafe_allow_html=True)
                return
            
            # Display delivery plans
            for i, plan in enumerate(st.session_state.delivery_plans, 1):
                st.markdown(f"### Delivery Plan {i}")
                st.markdown(f"**Drone ID:** {plan['drone_id']}")
                st.markdown("**Packages:**")
                for package in plan['packages']:
                    st.markdown(f"- Package {package.id}: {package.weight}kg, ${package.value} to {package.destination}")
                st.markdown(f"**Route:** {' → '.join(plan['route'])}")
                st.markdown(f"**Total Distance:** {plan['total_distance']:.2f}")
                st.markdown(f"**Total Value:** ${plan['total_value']:.2f}")
                st.markdown("---")
            
            # Display statistics
            statistics = st.session_state.planner.get_delivery_statistics(st.session_state.delivery_plans)
            st.markdown("### Delivery Statistics")
            display_metrics(statistics)
            
            # Show statistics visualizations
            st.markdown("### Delivery Statistics Visualization")
            plot_delivery_statistics(statistics)
            
            # Create and offer download of delivery plans
            delivery_data = []
            for plan in st.session_state.delivery_plans:
                for package in plan['packages']:
                    delivery_data.append({
                        'Drone ID': plan['drone_id'],
                        'Package ID': package.id,
                        'Weight': package.weight,
                        'Value': package.value,
                        'Destination': package.destination,
                        'Route': ' → '.join(plan['route']),
                        'Total Distance': plan['total_distance'],
                        'Total Value': plan['total_value']
                    })
            
            delivery_df = pd.DataFrame(delivery_data)
            st.markdown(get_table_download_link(delivery_df, 'delivery_plans.csv'), unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f"""
                <div class="error-box">
                    Error planning deliveries: {str(e)}
                </div>
            """, unsafe_allow_html=True)

def main():
    st.title("🚁 Drone Delivery System")
    
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.image("https://img.icons8.com/color/96/000000/drone.png", width=100)
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio(
        "",
        ["Add City", "Add Route", "Manage Drones", "Manage Packages", "Plan Deliveries"]
    )
    
    # Add download button for evaluation file
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Test Evaluation")
    evaluation_df = pd.read_csv("test_evaluation.xlsx")
    st.sidebar.markdown(get_table_download_link(evaluation_df, 'test_evaluation.csv'), unsafe_allow_html=True)
    
    if page == "Add City":
        add_city()
    elif page == "Add Route":
        add_route()
    elif page == "Manage Drones":
        manage_drones()
    elif page == "Manage Packages":
        manage_packages()
    elif page == "Plan Deliveries":
        plan_deliveries()

if __name__ == "__main__":
    main() 