# SAFEST-Route-Planner
🚦 Dehradun Route Planner 🛣️
A Streamlit-based route planning application for Dehradun, India. This app helps users find the safest and most efficient route between two locations by combining road network data with synthetic crime statistics.

📌 Features
🗺️ Interactive map of Dehradun using Folium
🔍 Route planning with Dijkstra and A* algorithms
🛡️ Safety-aware routing using location-based crime data
🏥 Emergency contacts and distance limit alerts
📍 Location selection via dropdown or interactive map
🧠 Caching, dynamic safety scoring, and optimized pathfinding
🚓 Visual indication of route safety on the map
🔧 Tech Stack
Python 3.8+
Streamlit
OpenRouteService
Folium & Streamlit-Folium
Pandas & NumPy
Geopy (for geocoding)
Custom crime-weighted routing logic
📁 Project Structure
. ├── app.py # Main Streamlit app

├── dehradun_crime_synthetic_data.csv # Synthetic crime dataset

├── src/

│ └── config/

│ └── config.py # Configuration: API keys, constants, weights

├── requirements.txt # Dependencies

└── README.md # This file

✅ Requirements Python 3.9+

Streamlit

OpenRouteService

Folium

Pandas

NumPy

Geopy

All listed in requirements.txt.

⚙️ Setup Instructions
1. Clone the Repository
git clone https://github.com/your-username/dehradun-route-planner.git cd dehradun-route-planner

2. Create a Virtual Environment (Optional)
python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.tx

4. Add Configuration
Edit or create the file at src/config/config.py: ORS_API_KEY = "your_openrouteservice_api_key" DEFAULT_SAFETY_THRESHOLD = 70 EMERGENCY_CONTACTS = { "police": "100", "ambulance": "108", "fire_station": "101", } MAP_DEFAULT_CENTER = [30.3165, 78.0322] # Dehradun center DEHRADUN_BOUNDING_BOX = { "min_lat": 30.2, "max_lat": 30.5, "min_lon": 77.9, "max_lon": 78.3 } CRIME_WEIGHTS = { "Theft": 2, "Assault": 3, "Robbery": 4, "Harassment": 1, "Vandalism": 1, "Other": 1 }

5. Run the App
streamlit run app.py

📊 Data
The app uses synthetic crime data for Dehradun (dehradun_crime_synthetic_data.csv) with the following fields:

Location (area/neighborhood)

Crime_Type (e.g., Theft, Robbery, etc.)

Crime types are weighted using the CRIME_WEIGHTS dictionary in config.py.

💡 Usage
Enter start and end locations manually or by clicking on the map. Adjust the safety threshold and distance limit in the sidebar. The app will compute and display: Dijkstra route (blue) A route* (green) Safety score influences path selection (routes through unsafe areas are avoided).

📞 Emergency Contact Info
Available in the sidebar for quick reference:

🚓 Police: 100

🚑 Ambulance: 108

🔥 Fire Station: 101

🧪 Sample Test Locations
Try using:

ISBT Dehradun

Rajpur Road

Clock Tower

Ballupur Chowk

📦 Example Use Cases
Urban logistics optimization

Delivery route planning with safety constraints

Real-time police dispatch routing

Urban planning and crime analysis visualization

🛠️ TODO / Enhancements
✅ Add UI to toggle between routing algorithms

📍 Allow saving named locations

📈 Add route analytics (ETA, average safety, etc.)

🧠 Integrate live traffic or police data (future)

📦 Export route summary

📜 License
This project is released under the MIT License.
