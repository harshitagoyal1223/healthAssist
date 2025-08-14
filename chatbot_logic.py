import re

def get_bot_response(user_input):
    user_input = user_input.lower()

    # 1. Greetings
    if re.search(r'\b(hi|hello|hey|good morning|good evening)\b', user_input):
        return "Hello! How can I assist you with your health today?"

    # 2. Appointment
    elif "book" in user_input and "appointment" in user_input:
        return "Sure, I can help you with that. What is your preferred date and time?"

    elif "cancel" in user_input and "appointment" in user_input:
        return "Please provide your appointment ID or name and date."

    # 3. Symptoms check
    elif any(symptom in user_input for symptom in ["fever", "cough", "cold", "headache", "nausea", "pain", "vomit"]):
        return "I'm sorry you're experiencing that. How long have you had these symptoms?"

    # 4. Specialist suggestion
    elif "which doctor" in user_input or "see a doctor" in user_input:
        return "Please tell me your symptoms, and I will recommend a specialist."

    # 5. COVID-related
    elif "covid" in user_input or "corona" in user_input:
        return "If you suspect COVID-19, please isolate and get tested. You can book a test through our platform."

    # 6. Prescription
    elif "prescription" in user_input:
        return "To issue a prescription, I need your symptoms and doctor’s recommendation."

    # 7. Emergency
    elif "emergency" in user_input or "urgent" in user_input:
        return "In case of emergency, please call 108 or visit the nearest hospital immediately."

    # 8. Diet / Nutrition
    elif "diet" in user_input or "nutrition" in user_input:
        return "Balanced diets depend on age and health. Would you like general tips or a custom plan?"

    # 9. Mental health
    elif "stress" in user_input or "anxiety" in user_input or "depression" in user_input:
        return "Mental health matters. I recommend talking to our licensed counselors. Shall I schedule a session?"

    # 10. Vaccination
    elif "vaccine" in user_input:
        return "Are you asking about COVID vaccine, flu shots, or child immunization?"

    # 11. Default fallback
    else:
        return "I'm not sure how to help with that. Can you please elaborate or try rephrasing?"
