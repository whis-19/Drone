import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models.package import Package
from models.drone import Drone
from delivery_planner import DeliveryPlanner

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
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a bar chart of packages by destination
    dest_counts = pd.DataFrame(packages)['Destination'].value_counts()
    fig2 = px.bar(
        x=dest_counts.index,
        y=dest_counts.values,
        title='Packages by Destination',
        labels={'x': 'Destination', 'y': 'Number of Packages'}
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
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def add_city():
    """Add a new city to the delivery network."""
    st.subheader("Add New City")
    col1, col2 = st.columns(2)
    with col1:
        city_name = st.text_input("City Name")
    with col2:
        has_charging = st.checkbox("Has Charging Station")
    
    if st.button("Add City"):
        if city_name:
            st.session_state.planner.add_city(city_name, has_charging)
            st.success(f"City {city_name} added successfully!")
        else:
            st.error("Please enter a city name")
    
    # Show network visualization
    if len(st.session_state.planner.cities) > 0:
        st.subheader("Current Network")
        plot_route_network(st.session_state.planner)

def add_route():
    """Add a new route between cities."""
    st.subheader("Add New Route")
    cities = list(st.session_state.planner.cities.keys())
    
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
            st.success(f"Route from {city1} to {city2} added successfully!")
        else:
            st.error("Please select different cities")
    
    # Show network visualization
    if len(st.session_state.planner.cities) > 0:
        st.subheader("Current Network")
        plot_route_network(st.session_state.planner)

def manage_drones():
    """Add and manage drones."""
    st.subheader("Manage Drones")
    
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
            st.success(f"Drone {drone_id} added successfully!")
        except ValueError as e:
            st.error(str(e))
    
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
        st.dataframe(drones_df)
        
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
        st.plotly_chart(fig, use_container_width=True)

def manage_packages():
    """Add and manage packages."""
    st.subheader("Manage Packages")
    
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
            st.success(f"Package {package_id} added successfully!")
        except ValueError as e:
            st.error(str(e))
    
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
        st.dataframe(packages_df)
        
        # Show package distribution plots
        st.subheader("Package Distribution")
        plot_package_distribution(packages_df)

def plan_deliveries():
    """Plan and display delivery routes."""
    st.subheader("Plan Deliveries")
    
    if not st.session_state.drones or not st.session_state.packages:
        st.warning("Please add at least one drone and one package first")
        return
    
    if st.button("Plan Deliveries"):
        try:
            st.session_state.delivery_plans = st.session_state.planner.plan_delivery(
                st.session_state.packages,
                st.session_state.drones
            )
            
            if not st.session_state.delivery_plans:
                st.warning("No feasible delivery plans found")
                return
            
            # Display delivery plans
            for i, plan in enumerate(st.session_state.delivery_plans, 1):
                st.write(f"### Delivery Plan {i}")
                st.write(f"**Drone ID:** {plan['drone_id']}")
                st.write("**Packages:**")
                for package in plan['packages']:
                    st.write(f"- Package {package.id}: {package.weight}kg, ${package.value} to {package.destination}")
                st.write(f"**Route:** {' → '.join(plan['route'])}")
                st.write(f"**Total Distance:** {plan['total_distance']:.2f}")
                st.write(f"**Total Value:** ${plan['total_value']:.2f}")
                st.write("---")
            
            # Display statistics
            statistics = st.session_state.planner.get_delivery_statistics(st.session_state.delivery_plans)
            st.write("### Delivery Statistics")
            st.write(f"Total Packages: {statistics['total_packages']}")
            st.write(f"Total Value: ${statistics['total_value']:.2f}")
            st.write(f"Total Distance: {statistics['total_distance']:.2f}")
            st.write(f"Average Packages per Trip: {statistics['average_packages_per_trip']:.2f}")
            st.write(f"Average Value per Trip: ${statistics['average_value_per_trip']:.2f}")
            st.write(f"Average Distance per Trip: {statistics['average_distance_per_trip']:.2f}")
            
            # Show statistics visualizations
            st.subheader("Delivery Statistics Visualization")
            plot_delivery_statistics(statistics)
            
        except Exception as e:
            st.error(f"Error planning deliveries: {str(e)}")

def main():
    st.title("Drone Delivery System")
    
    initialize_session_state()
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Add City", "Add Route", "Manage Drones", "Manage Packages", "Plan Deliveries"]
    )
    
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