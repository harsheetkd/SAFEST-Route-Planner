# 🚦 SAFEST Route Planner – Dehradun 🛣️

A **Streamlit-based web application** for planning the safest and most efficient routes in **Dehradun, India**. This app combines road network data with **synthetic crime statistics** to help users avoid unsafe areas.

---

## 📌 Features

- 🗺️ **Interactive Map** using Folium
- 📍 **Location selection** via dropdown or map click
- 🔄 **Routing Algorithms**: Dijkstra and A* Pathfinding
- 🛡️ **Safety-aware Routing** based on crime data
- 🚨 **Emergency Contact Info** (Police, Ambulance, Fire)
- 🎯 **Safety Thresholds** and distance alerts
- ⚡ **Caching & Performance Optimizations**
- 📈 **Dynamic Safety Scores** on route paths

---

## ⚙️ Tech Stack

- Python 3.9+
- Streamlit
- OpenRouteService (ORS API)
- Folium & Streamlit-Folium
- Pandas & NumPy
- Geopy (for geocoding)
- Custom crime-weighted routing logic

---

## 🗂️ Project Structure

```
.
├── app.py                       # Main Streamlit app
├── dehradun_crime_synthetic.csv # Synthetic crime dataset
├── src/
│   └── config/
│       └── config.py            # Configuration: API keys, weights
├── requirements.txt             # All dependencies
└── README.md                    # Project documentation
```

---

## 🔧 Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/dehradun-route-planner.git
   cd dehradun-route-planner
   ```

2. **Create Virtual Environment (Optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Configuration**

   Create or edit the file: `src/config/config.py`

   ```python
   ORS_API_KEY = "your_openrouteservice_api_key"

   DEFAULT_SAFETY_THRESHOLD = 70

   EMERGENCY_CONTACTS = {
       "police": "100",
       "ambulance": "108",
       "fire_station": "101",
   }

   MAP_DEFAULT_CENTER = [30.3165, 78.0322]  # Dehradun

   DEHRADUN_BOUNDING_BOX = {
       "min_lat": 30.2,
       "max_lat": 30.5,
       "min_lon": 77.9,
       "max_lon": 78.3,
   }

   CRIME_WEIGHTS = {
       "Theft": 2,
       "Assault": 3,
       "Robbery": 4,
       "Harassment": 1,
       "Vandalism": 1,
       "Other": 1,
   }
   ```

5. **Run the App**
   ```bash
   streamlit run app.py
   ```

---

## 📊 Data Overview

- **Source**: `dehradun_crime_synthetic.csv`
- **Fields**:
  - `Location`: Area or neighborhood
  - `Crime_Type`: Theft, Assault, Robbery, etc.
- **Routing Logic**:
  - Crime types are weighted using `CRIME_WEIGHTS` from `config.py`
  - Unsafe areas increase path cost and are avoided in route planning

---

## 🧪 Sample Test Locations

Try planning routes between:

- ISBT Dehradun
- Rajpur Road
- Clock Tower
- Ballupur Chowk

---

## 📞 Emergency Numbers

Displayed on the app sidebar for quick access:

- 🚓 Police: 100
- 🚑 Ambulance: 108
- 🔥 Fire Station: 101

---

## ✅ Example Use Cases

- Safer travel planning
- Delivery route optimization
- Emergency dispatch routing
- Urban crime analysis

---

## 🚀 Future Enhancements

- [x] Toggle between routing algorithms
- [ ] Save custom/named locations
- [ ] Add analytics (ETA, avg. safety, etc.)
- [ ] Integrate real-time police/traffic data
- [ ] Export route summary (PDF/JSON)

---

## 📜 License

Released under the **MIT License** – free to use, modify, and distribute.

---

## 🙌 Acknowledgements

- [OpenRouteService](https://openrouteservice.org/)
- [Streamlit](https://streamlit.io/)
- [Folium](https://python-visualization.github.io/folium/)
