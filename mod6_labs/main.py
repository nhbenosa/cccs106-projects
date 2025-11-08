"""Weather Application using Flet v0.28.3 """

import asyncio
import json
from pathlib import Path
import httpx
import flet as ft
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        
        # History management
        self.history_file = Path("search_history.json")
        self.search_history = self.load_history()
        
        # Temperature unit management
        self.current_unit = self.load_preference("unit", "metric")
        self.current_weather_data = None
        
        # Weather condition colors
        self.weather_colors = {
            "clear": {"bg": ft.Colors.AMBER_100, "accent": ft.Colors.AMBER_700},
            "clouds": {"bg": ft.Colors.BLUE_GREY_100, "accent": ft.Colors.BLUE_GREY_700},
            "rain": {"bg": ft.Colors.BLUE_100, "accent": ft.Colors.BLUE_700},
            "drizzle": {"bg": ft.Colors.LIGHT_BLUE_100, "accent": ft.Colors.LIGHT_BLUE_700},
            "thunderstorm": {"bg": ft.Colors.DEEP_PURPLE_100, "accent": ft.Colors.DEEP_PURPLE_700},
            "snow": {"bg": ft.Colors.CYAN_50, "accent": ft.Colors.CYAN_700},
            "mist": {"bg": ft.Colors.GREY_200, "accent": ft.Colors.GREY_700},
            "fog": {"bg": ft.Colors.GREY_200, "accent": ft.Colors.GREY_700},
            "default": {"bg": ft.Colors.BLUE_50, "accent": ft.Colors.BLUE_700}
        }
        
        self.setup_page()
        self.build_ui()
    
    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Save search history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.search_history, f)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_to_history(self, city: str):
        """Add city to search history."""
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:10]  # Keep last 10
            self.save_history()
            self.update_history_dropdown()
    
    def load_preference(self, key: str, default):
        """Load user preference from file."""
        pref_file = Path("preferences.json")
        if pref_file.exists():
            try:
                with open(pref_file, 'r') as f:
                    prefs = json.load(f)
                    return prefs.get(key, default)
            except:
                return default
        return default
    
    def save_preference(self, key: str, value):
        """Save user preference to file."""
        pref_file = Path("preferences.json")
        prefs = {}
        if pref_file.exists():
            try:
                with open(pref_file, 'r') as f:
                    prefs = json.load(f)
            except:
                pass
        
        prefs[key] = value
        with open(pref_file, 'w') as f:
            json.dump(prefs, f)
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM 
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()
    
    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            self.unit_button.text = "°F"
            self.unit_button.tooltip = "Switch to Celsius"
        else:
            self.current_unit = "metric"
            self.unit_button.text = "°C"
            self.unit_button.tooltip = "Switch to Fahrenheit"
        
        self.save_preference("unit", self.current_unit)
        
        # Redisplay weather if data exists
        if self.current_weather_data:
            self.display_weather(self.current_weather_data)
        
        self.page.update()
    
    def convert_temperature(self, temp_celsius: float) -> float:
        """Convert temperature based on current unit."""
        if self.current_unit == "imperial":
            return (temp_celsius * 9/5) + 32
        return temp_celsius
    
    def get_unit_symbol(self) -> str:
        """Get current temperature unit symbol."""
        return "°F" if self.current_unit == "imperial" else "°C"
    
    def get_weather_condition(self, description: str) -> str:
        """Get weather condition category from description."""
        description = description.lower()
        if "clear" in description or "sun" in description:
            return "clear"
        elif "cloud" in description:
            return "clouds"
        elif "rain" in description:
            return "rain"
        elif "drizzle" in description:
            return "drizzle"
        elif "thunder" in description or "storm" in description:
            return "thunderstorm"
        elif "snow" in description:
            return "snow"
        elif "mist" in description or "haze" in description:
            return "mist"
        elif "fog" in description:
            return "fog"
        return "default"
    
    def update_history_dropdown(self):
        """Update the history dropdown with current history."""
        self.history_dropdown.options = [
            ft.dropdown.Option(city) for city in self.search_history
        ]
        self.history_dropdown.visible = len(self.search_history) > 0
        self.page.update()
    
    def load_from_history(self, city: str):
        """Load weather from history selection."""
        if city:
            self.city_input.value = city
            self.page.run_task(self.get_weather)
    
    async def get_current_location_weather(self, e=None):
        """Get weather for current location using IP geolocation."""
        self.location_button.disabled = True
        self.location_button.text = "Detecting..."
        self.page.update()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get location from IP
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                city = data.get('city', '')
                
                if city:
                    self.city_input.value = city
                    await self.get_weather()
                else:
                    self.show_error("Could not detect your location")
        except Exception as e:
            self.show_error("Could not detect your location. Please enter manually.")
        finally:
            self.location_button.disabled = False
            self.location_button.text = "My Location"
            self.page.update()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        # Unit toggle button
        self.unit_button = ft.ElevatedButton(
            text="°C" if self.current_unit == "metric" else "°F",
            tooltip="Switch to Fahrenheit" if self.current_unit == "metric" else "Switch to Celsius",
            on_click=self.toggle_units,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
            ),
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
            expand=True,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # My Location button
        self.location_button = ft.ElevatedButton(
            "My Location",
            icon=ft.Icons.MY_LOCATION,
            on_click=lambda e: self.page.run_task(self.get_current_location_weather, e),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE_700,
            ),
        )
        
        # History dropdown
        self.history_dropdown = ft.Dropdown(
            label="Recent Searches",
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=lambda e: self.load_from_history(e.control.value),
            visible=len(self.search_history) > 0,
            width=300,
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        title_row = ft.Row(
            [
                self.title,
                ft.Row([self.unit_button, self.theme_button], spacing=10),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        search_row = ft.Row(
            [
                self.city_input,
                self.search_button,
                self.location_button,
            ],
            spacing=10,
        )
        
        # Info banner
        self.info_banner = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.BLUE_600, size=20),
                    ft.Text(
                        "Enter a city name or use 'My Location' to get weather information",
                        color=ft.Colors.BLACK87,
                        size=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            bgcolor=ft.Colors.BLUE_50,
            width=700,
            border_radius=10,
            padding=15,
            margin=ft.margin.only(top=10, bottom=10),
        )
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    search_row,
                    self.history_dropdown,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    self.info_banner,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll="auto",
                expand=True,
            )
        )
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.info_banner.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Store current data
            self.current_weather_data = weather_data
            
            # Add to history
            city_name = weather_data.get("name", city)
            self.add_to_history(city_name)
            
            # Display weather
            self.display_weather(weather_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    def display_weather(self, data: dict):
        """Display weather information with dynamic colors."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_celsius = data.get("main", {}).get("temp", 0)
        feels_like_celsius = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        cloudiness = data.get("clouds", {}).get("all", 0)
        
        # Convert temperatures
        temp = self.convert_temperature(temp_celsius)
        feels_like = self.convert_temperature(feels_like_celsius)
        unit_symbol = self.get_unit_symbol()
        
        # Get weather condition for coloring
        condition = self.get_weather_condition(description)
        colors = self.weather_colors.get(condition, self.weather_colors["default"])
        
        # Update container colors
        self.weather_container.bgcolor = colors["bg"]
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=colors["accent"],
                ),
                
                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                            color=colors["accent"],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}{unit_symbol}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=colors["accent"],
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}{unit_symbol}",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(),
                
                # Additional info
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            colors["accent"]
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s",
                            colors["accent"]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.COMPRESS,
                            "Pressure",
                            f"{pressure} hPa",
                            colors["accent"]
                        ),
                        self.create_info_card(
                            ft.Icons.CLOUD,
                            "Cloudiness",
                            f"{cloudiness}%",
                            colors["accent"]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()

        async def fade_in():
            await asyncio.sleep(0.1)
            self.weather_container.opacity = 1
            self.page.update()

        self.page.run_task(fade_in)

    def create_info_card(self, icon, label, value, accent_color):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=accent_color),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=accent_color,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.info_banner.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)