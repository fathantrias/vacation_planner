"""
Autonomous Vacation Planner - Streamlit Application
"""

import os
import streamlit as st
from dotenv import load_dotenv
from agent.planner_agent import create_vacation_planner_agent, invoke_agent
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Autonomous Vacation Planner",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = None

if "payment_configured" not in st.session_state:
    st.session_state.payment_configured = False

if "payment_info" not in st.session_state:
    st.session_state.payment_info = {}

if "bookings" not in st.session_state:
    st.session_state.bookings = []


def initialize_agent():
    """Initialize the LangGraph agent."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    if not groq_api_key:
        st.error("⚠️ GROQ_API_KEY not found. Please set it in .env file or Streamlit secrets.")
        st.stop()
    
    agent, system_prompt = create_vacation_planner_agent(groq_api_key, model)
    st.session_state.system_prompt = system_prompt
    return agent


def render_payment_sidebar():
    """Render payment configuration in sidebar."""
    with st.sidebar:
        st.header("💳 Payment Configuration")
        
        if not st.session_state.payment_configured:
            st.info("Please configure payment to enable bookings")
            
            with st.form("payment_form"):
                card_number = st.text_input(
                    "Card Number",
                    placeholder="1234 5678 9012 3456",
                    max_chars=16
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    expiry = st.text_input("Expiry", placeholder="MM/YY")
                with col2:
                    cvv = st.text_input("CVV", type="password", max_chars=3)
                
                cardholder = st.text_input("Cardholder Name")
                
                authorize = st.checkbox(
                    "✅ I authorize this chatbot to make bookings",
                    help="This grants permission for the agent to book flights and hotels"
                )
                
                submit = st.form_submit_button("💾 Save Payment Info", use_container_width=True)
                
                if submit:
                    if card_number and expiry and cvv and cardholder and authorize:
                        st.session_state.payment_configured = True
                        st.session_state.payment_info = {
                            "card_last4": card_number[-4:] if len(card_number) >= 4 else "****",
                            "cardholder": cardholder,
                            "authorized": True
                        }
                        # Set environment variable for cross-thread access (PoC/single-user deployment)
                        os.environ['PAYMENT_AUTHORIZED'] = 'true'
                        st.success("✅ Payment configured successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill all fields and check the authorization box")
        else:
            st.success("✅ Payment Configured")
            st.write(f"**Card:** •••• {st.session_state.payment_info['card_last4']}")
            st.write(f"**Name:** {st.session_state.payment_info['cardholder']}")
            
            if st.button("🔄 Update Payment Info", use_container_width=True):
                st.session_state.payment_configured = False
                st.session_state.payment_info = {}
                # Clear environment variable
                os.environ.pop('PAYMENT_AUTHORIZED', None)
                st.rerun()
        
        st.divider()
        
        # Display bookings summary
        st.header("📋 Bookings Summary")
        if st.session_state.bookings:
            total = sum(b.get("amount", 0) for b in st.session_state.bookings)
            st.metric("Total Bookings", len(st.session_state.bookings))
            st.metric("Total Spent", f"${total:.2f}")
            
            with st.expander("View Details"):
                for i, booking in enumerate(st.session_state.bookings, 1):
                    st.write(f"**{i}. {booking['type']}**")
                    st.write(f"Ref: {booking['reference']}")
                    st.write(f"Amount: ${booking['amount']:.2f}")
                    st.divider()
        else:
            st.info("No bookings yet")


def render_chat_interface():
    """Render the main chat interface."""
    st.title("🏖️ Autonomous Vacation Planner")
    st.caption("Powered by LangGraph + Groq + Streamlit")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Tell me about your dream vacation..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Planning your vacation..."):
                try:
                    # Prepare chat history for agent with system prompt at the beginning
                    chat_history = []
                    
                    # Add system message only on first interaction
                    if len(st.session_state.messages) == 1:  # Only the current user message
                        from langchain_core.messages import SystemMessage
                        chat_history.append(SystemMessage(content=st.session_state.system_prompt))
                    
                    # Add previous messages
                    for msg in st.session_state.messages[:-1]:  # Exclude current message
                        if msg["role"] == "user":
                            chat_history.append(HumanMessage(content=msg["content"]))
                        else:
                            chat_history.append(AIMessage(content=msg["content"]))
                    
                    # Invoke agent
                    response = invoke_agent(
                        st.session_state.agent,
                        prompt,
                        chat_history
                    )
                    
                    # Extract assistant message
                    assistant_message = ""
                    if "messages" in response:
                        for msg in response["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                if isinstance(msg, AIMessage):
                                    assistant_message = msg.content
                    
                    if not assistant_message:
                        assistant_message = "I apologize, but I couldn't process your request. Please try rephrasing."
                    
                    st.markdown(assistant_message)
                    
                    # Check for booking confirmations in response
                    if "✅" in assistant_message and ("booked" in assistant_message.lower() or "confirmation" in assistant_message.lower()):
                        # Extract booking reference if present
                        if "BK-" in assistant_message:
                            import re
                            ref_match = re.search(r'BK-[A-Z0-9-]+', assistant_message)
                            if ref_match:
                                booking_ref = ref_match.group(0)
                                booking_type = "Flight" if "FL" in booking_ref else "Hotel" if "HTL" in booking_ref else "Booking"
                                
                                # Try to extract amount
                                amount_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', assistant_message)
                                amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0
                                
                                st.session_state.bookings.append({
                                    "type": booking_type,
                                    "reference": booking_ref,
                                    "amount": amount
                                })
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                except Exception as e:
                    error_msg = f"❌ An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })


def main():
    """Main application entry point."""
    # Initialize agent if not already done
    if st.session_state.agent is None:
        with st.spinner("Initializing vacation planner agent..."):
            st.session_state.agent = initialize_agent()
    
    # Render UI
    render_payment_sidebar()
    render_chat_interface()
    
    # Add clear chat button in sidebar
    with st.sidebar:
        st.divider()
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.bookings = []
            st.rerun()


if __name__ == "__main__":
    main()
