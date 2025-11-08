# CCCS 106 Projects
Application Development and Emerging Technologies  
Academic Year 2025-2026

## Student Information
- **Name:** Nhel Adam S. Benosa
- **Student ID:** 231003282
- **Program:** BSCS
- **Section:** 3B

## Repository Structure

### Week 1 Labs - Environment Setup and Python Basics
- `week1_labs/hello_world.py` - Basic Python introduction
- `week1_labs/basic_calculator.py` - Simple console calculator

### Week 2 Labs - Git and Flet GUI Development
- `week2_labs/hello_flet.py` - First Flet GUI application
- `week2_labs/personal_info_gui.py` - Enhanced personal information manager
- `week2_labs/enhanced_calculator.py` - GUI calculator (coming soon)

### Week 3 Labs - Flet User Login Application
- `week3_labs/main.py` - Login Application main file
- `week3_labs/db_connection` - Handles the connection to the MySQL database

### Week 4 Labs - Contact book Application Enhancement
- `week4_labs/main.py` - Contact book Application main file that builds the window and lay out the visible components
- `week4_labs/app_logic.py` - Backend logic of the main file for Contact book Application
- `week4_labs/database.py` - This file manages all communication with the contacts.db

### Module 6 Learning Task - Weather Application Enhancement
- `mod6_labs/main.py` - Weather Application main file that builds the window and lay out the visible components
- `mod6_labs/config.py` - Handles configuration management, including API keys, base URLs, and environment variable for the Weather Application.
- `mod6_labs/weather_service.py` - Contains the service layer responsible for communicating with the OpenWeatherMap API to fetch current weather and forecast data, including error handling and async HTTP requests.
- `mod6_labs/test_weather_service.py` - Unit test file that validates the functionality and reliability of the `WeatherService` class, ensuring correct API responses and proper error handling.


### Module 1 Final Project
- `module1_final/` - Final integrated project (TBD)

## Technologies Used
- **Python 3.8+** - Main programming language
- **Flet 0.28.3** - GUI framework for cross-platform applications
- **Git & GitHub** - Version control and collaboration
- **VS Code** - Integrated development environment

## Development Environment
- **Virtual Environment:** cccs106_env
- **Python Packages:** flet==0.28.3
- **Platform:** Windows 10/11

## How to Run Applications

### Prerequisites
1. Python 3.8+ installed
2. Virtual environment activated: `cccs106_env\Scripts\activate`
3. Flet installed: `pip install flet==0.28.3`

### Running GUI Applications
```cmd
# Navigate to project directory
cd week1_labs
cd week2_labs
cd week3_labs
cd week4_labs
cd mod6_labs

### Run applications

# week1_labs
hello_world.py
basic_calculator.py

# week2_labs
hello_flet.py
python personal_info_gui.py

# week3_labs
main.py
db_connection.py

# week4_labs
main.py
app_logic.py
database.py

# mod6_labs
main.py
weather_service.py
config.py
test_weather_service.py