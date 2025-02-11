from groq import Groq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from datetime import datetime

class PlantLLMInterface:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        
        # Initialize prompt templates
        self.status_template = PromptTemplate(
            input_variables=["moisture", "light", "temperature", "humidity", "time_of_day"],
            template="""
            You are a friendly house plant that can communicate with your owner. 
            Based on these current conditions:
            - Soil Moisture: {moisture}%
            - Light Level: {light}%
            - Temperature: {temperature}°C
            - Humidity: {humidity}%
            - Time: {time_of_day}

            Respond as if you are the plant, expressing your needs and feelings in a casual, 
            friendly way. Include emojis and personality. If conditions are good, express happiness. 
            If any conditions are concerning, express your needs gently but clearly.
            """
        )
        
        self.analysis_template = PromptTemplate(
            input_variables=["leaf_health", "historical_data"],
            template="""
            As a plant analyzing my own health:
            - Current Leaf Health: {leaf_health}
            - Historical Data: {historical_data}

            Provide insights about my overall health trends and any concerning patterns. 
            Speak in first person and maintain a friendly tone while explaining any issues 
            or improvements noticed.
            """
        )

    async def generate_status_message(self, sensor_data):
        """Generate a contextual message based on current sensor readings"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            
            # Create the chain
            chain = LLMChain(
                llm=self.client,
                prompt=self.status_template
            )
            
            # Generate response
            response = await chain.arun(
                moisture=sensor_data['moisture'],
                light=sensor_data['light'],
                temperature=sensor_data['temperature'],
                humidity=sensor_data['humidity'],
                time_of_day=current_time
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating status message: {e}")
            return "Hi! I'm having trouble expressing myself right now. 🌱"

    async def generate_health_analysis(self, leaf_health, historical_data):
        """Generate health analysis based on visual data and history"""
        try:
            chain = LLMChain(
                llm=self.client,
                prompt=self.analysis_template
            )
            
            response = await chain.arun(
                leaf_health=leaf_health,
                historical_data=historical_data
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating health analysis: {e}")
            return "I'm not sure about my health right now. Maybe we can check again later? 🤔"

    def get_personality_traits(self, plant_type):
        """Define personality traits based on plant type"""
        personalities = {
            "succulent": {
                "mood": "laid-back",
                "water_needs": "minimal",
                "light_preference": "bright",
                "emoji_style": "desert"
            },
            "fern": {
                "mood": "delicate",
                "water_needs": "frequent",
                "light_preference": "indirect",
                "emoji_style": "forest"
            },
            "orchid": {
                "mood": "sophisticated",
                "water_needs": "moderate",
                "light_preference": "filtered",
                "emoji_style": "elegant"
            }
        }
        return personalities.get(plant_type, {
            "mood": "friendly",
            "water_needs": "moderate",
            "light_preference": "medium",
            "emoji_style": "general"
        })

# Example usage
if __name__ == "__main__":
    import asyncio
    import os
    
    async def main():
        # Initialize with your Groq API 
        plant_llm = PlantLLMInterface(api_key="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")
        
        # Example sensor data
        sample_data = {
            "moisture": 45,
            "light": 70,
            "temperature": 24,
            "humidity": 60
        }
        
        # Generate a status message
        message = await plant_llm.generate_status_message(sample_data)
        print("Plant says:", message)
        
        # Generate a health analysis
        health_analysis = await plant_llm.generate_health_analysis(
            leaf_health="90% green leaves, some yellow spots",
            historical_data="Moisture levels have been stable, light exposure increased last week"
        )
        print("\nHealth Analysis:", health_analysis)

    asyncio.run(main())
