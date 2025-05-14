# Smart Drone Delivery Planner

This project implements a drone delivery planning system that optimizes package delivery routes while considering drone constraints and package priorities.

## Features
- Shortest path calculation using Dijkstra's algorithm
- Package selection optimization considering weight and value
- Route planning with distance constraints
- Multiple drone support
- Efficient delivery planning

## Setup
1. Install Python 3.8 or higher
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the main program:
```
python drone_delivery.py
```

## Testing
Run the test cases:
```
pytest test_drone_delivery.py
```

## Project Structure
- `drone_delivery.py`: Main program file
- `test_drone_delivery.py`: Test cases
- `requirements.txt`: Project dependencies 