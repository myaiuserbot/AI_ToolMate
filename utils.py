def get_language_prompt():
    """Return the language selection prompt."""
    return (
        "🌟 Welcome to AIToolMate! Pehle language choose karo:\n"
        "1. English\n"
        "2. Hinglish\n"
        "Reply with 'English' ya 'Hinglish' to start."
    )

def get_greeting_message(language):
    """Return the greeting message based on language."""
    if language == "hinglish":
        return (
            "Namaste! AIToolMate mein swagat hai! 😊\n"
            "Main aapko AI tools suggest karunga jo aapke business ko boost karenge! 🚀"
        )
    return (
        "Hi! Welcome to AIToolMate! 😊\n"
        "I’ll suggest AI tools to boost your business! 🚀"
    )

def get_default_response(language, category=None, error=None):
    """Return a default response for invalid queries or errors."""
    if error:
        if language == "hinglish":
            return f"Arre! Kuch toh gadbad ho gaya: {error}. 😔 Dobara try karo!"
        return f"Oops! Something went wrong: {error}. 😔 Please try again!"
    if category:
        if language == "hinglish":
            return f"Koi tools '{category}' ke liye nahi mile. 😔 Dusri category try karo, jaise 'SEO tools' ya 'Website builders'!"
        return f"No tools found for '{category}'. 😔 Try another category, like 'SEO tools' or 'Website builders'!"
    if language == "hinglish":
        return "Sorry, samajh nahi aaya! 😅 Category bolo, jaise 'SEO tools', 'Website builders'."
    return "Sorry, I didn’t understand! 😅 Please specify a category, like 'SEO tools' or 'Website builders'."

def extract_category(message):
    """Extract the category from a user message."""
    category_map = {
        "website builders": "Website Creation & Design",
        "seo tools": "SEO & Content Optimization",
        "copywriting": "Copywriting & Blogging",
        "video editing": "Video Creation & Editing",
        "image editing": "Image Generation & Graphic Design",
        "email marketing": "Email Marketing & Outreach",
        "social media": "Social Media Management",
        "text to speech": "Text-to-Speech & Voice Cloning",
        "podcast editing": "Podcast & Audio Editing",
        "resume tools": "Resume & Career Tools",
        "chatbots": "Chatbots & Virtual Assistants",
        "ecommerce": "E-commerce Support",
        "idea generation": "Idea Generation & Planning",
        "learning tools": "Learning & Tutoring",
        "code assistance": "Code Assistance",
        "cybersecurity": "Cybersecurity & Privacy",
        "music generation": "Music & Audio Generation",
        "research tools": "Research & Summarization",
        "translation": "Translation & Subtitling",
        "ads creatives": "Ads & Creatives",
        "llm agents": "LLM-based Agents",
        "meeting tools": "Meeting Tools",
        "hosting": "Hosting"
    }
    
    for key, value in category_map.items():
        if key in message:
            return value
    return None

def format_response(tools, category, language):
    """Format tool recommendations for WhatsApp response."""
    if not tools:
        return get_default_response(language, category)
    
    if language == "hinglish":
        response = f"**{category} ke liye top AI tools**:\n\n"
        for tool in tools:
            response += (
                f"🔹 *{tool.tool_name}*\n"
                f"   Kaam: {tool.use_case}\n"
                f"   Commission: {tool.affiliate_amount}\n"
                f"   Link: {tool.affiliate_link} 🚀\n\n"
            )
        response += "Aur tools chahiye? Dusri category bolo (jaise 'SEO tools', 'Website builders')! 😊"
    else:
        response = f"**Top AI Tools for {category}**:\n\n"
        for tool in tools:
            response += (
                f"🔹 *{tool.tool_name}*\n"
                f"   Use Case: {tool.use_case}\n"
                f"   Commission: {tool.affiliate_amount}\n"
                f"   Link: {tool.affiliate_link} 🚀\n\n"
            )
        response += "Need more tools? Try another category (e.g., 'SEO tools', 'Website builders')! 😊"
    
    return response
