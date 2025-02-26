import streamlit as st
import requests
import openai
import google.generativeai as genai
import json

st.set_page_config(
    page_title="Golf Tournament Recap Generator",
    page_icon="⛳",
    layout="wide",
)

# Custom CSS for orange theme
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton button {
        background-color: #ff6633;
        color: white;
    }
    .stButton button:hover {
        background-color: #e55a2d;
    }
    .reportview-container .main .block-container {
        max-width: 1000px;
    }
    h1, h2, h3 {
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("⛳ Golf Tournament Recap Generator")
st.markdown("Generate professional tournament recaps using AI")

# Initialize session state for storing selections
if 'selected_season' not in st.session_state:
    st.session_state.selected_season = None
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None
if 'selected_round' not in st.session_state:
    st.session_state.selected_round = None
if 'selected_tournament' not in st.session_state:
    st.session_state.selected_tournament = None
if 'tournament_results' not in st.session_state:
    st.session_state.tournament_results = None
if 'recap' not in st.session_state:
    st.session_state.recap = None
if 'selections_made' not in st.session_state:
    st.session_state.selections_made = False
if 'seasonal_data' not in st.session_state:
    st.session_state.seasonal_data = {}

# Create tabs for setup and results
tab1, tab2 = st.tabs(["Setup", "Results"])

with tab1:
    # API Settings
    st.header("API Settings")
    
    # Golf Genius API Key
    golf_api_key = st.text_input("Golf Genius API Key", type="password")
    
    # LLM Selection
    llm_choice = st.radio("Select AI Model:", ["OpenAI", "Google Gemini"], horizontal=True)
    
    # API Key based on selection
    if llm_choice == "OpenAI":
        llm_api_key = st.text_input("OpenAI API Key", type="password")
    else:
        llm_api_key = st.text_input("Google Gemini API Key", type="password")
    
    # Score Type Selection
    score_type = st.radio("Score Type:", ["Gross", "Net"], horizontal=True)
    
    # Functions for API calls
    def get_seasons(api_key):
        base_url = "https://www.golfgenius.com/api_v2"
        endpoint = f"{base_url}/{api_key}/seasons"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching seasons: {e}")
            return None

    def get_events(api_key, season_id):
        base_url = "https://www.golfgenius.com/api_v2"
        endpoint = f"{base_url}/{api_key}/events"
        params = {
            "page": 1,
            "season": season_id,
            "category": "",
            "directory": "",
            "archived": "",
        }
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching events: {e}")
            return None

    def get_rounds(api_key, event_id):
        base_url = "https://www.golfgenius.com/api_v2"
        endpoint = f"{base_url}/{api_key}/events/{event_id}/rounds"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching rounds: {e}")
            return None

    def get_tournaments(api_key, event_id, round_id):
        base_url = "https://www.golfgenius.com/api_v2"
        path = f"events/{event_id}/rounds/{round_id}/tournaments"
        url = f"{base_url}/{api_key}/{path}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching tournaments: {e}")
            return None

    def get_tournament_results(api_key, event_id, round_id, tournament_id):
        base_url = "https://www.golfgenius.com/api_v2"
        path = f"events/{event_id}/rounds/{round_id}"
        path2 = f"tournaments/{tournament_id}.json"
        endpoint = f"{base_url}/{api_key}/{path}/{path2}"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching tournament results: {e}")
            return None

    # Data Selection Section
    st.header("Tournament Selection")
    
    # Fetching seasons
    if st.button("Fetch Seasons") and golf_api_key:
        with st.spinner("Fetching seasons..."):
            seasons = get_seasons(golf_api_key)
            if seasons:
                season_options = {}
                for item in seasons:
                    season = item["season"]
                    name = season.get("name", "No Name Available")
                    season_id = season.get("id")
                    season_options[name] = season_id
                st.session_state.seasonal_data['seasons'] = season_options
                st.success("Seasons fetched successfully!")
            else:
                st.error("Failed to fetch seasons.")
    
    # Season selection dropdown
    if 'seasons' in st.session_state.seasonal_data:
        season_name = st.selectbox(
            "Select Season:",
            options=list(st.session_state.seasonal_data['seasons'].keys()),
            key="season_selector"
        )
        st.session_state.selected_season = st.session_state.seasonal_data['seasons'][season_name]
        
        # Fetch events for selected season
        if st.button("Fetch Events") and st.session_state.selected_season:
            with st.spinner("Fetching events..."):
                events = get_events(golf_api_key, st.session_state.selected_season)
                if events:
                    event_options = {}
                    for item in events:
                        event = item["event"]
                        name = event.get("name", "No Name Available")
                        event_id = event.get("id")
                        event_options[name] = event_id
                    st.session_state.seasonal_data['events'] = event_options
                    st.success("Events fetched successfully!")
                else:
                    st.error("Failed to fetch events.")
    
    # Event selection dropdown
    if 'events' in st.session_state.seasonal_data:
        event_name = st.selectbox(
            "Select Event:",
            options=list(st.session_state.seasonal_data['events'].keys()),
            key="event_selector"
        )
        st.session_state.selected_event = st.session_state.seasonal_data['events'][event_name]
        
        # Fetch rounds for selected event
        if st.button("Fetch Rounds") and st.session_state.selected_event:
            with st.spinner("Fetching rounds..."):
                rounds = get_rounds(golf_api_key, st.session_state.selected_event)
                if rounds:
                    round_options = {}
                    for item in rounds:
                        round_data = item["round"]
                        name = round_data.get("name", "No Name Available")
                        round_id = round_data.get("id")
                        round_options[name] = round_id
                    st.session_state.seasonal_data['rounds'] = round_options
                    st.success("Rounds fetched successfully!")
                else:
                    st.error("Failed to fetch rounds.")
    
    # Round selection dropdown
    if 'rounds' in st.session_state.seasonal_data:
        round_name = st.selectbox(
            "Select Round:",
            options=list(st.session_state.seasonal_data['rounds'].keys()),
            key="round_selector"
        )
        st.session_state.selected_round = st.session_state.seasonal_data['rounds'][round_name]
        
        # Fetch tournaments for selected round
        if st.button("Fetch Tournaments") and st.session_state.selected_round:
            with st.spinner("Fetching tournaments..."):
                tournaments = get_tournaments(golf_api_key, st.session_state.selected_event, st.session_state.selected_round)
                if tournaments:
                    tournament_options = {}
                    for item in tournaments:
                        tournament = item["event"]
                        name = tournament.get("name", "No Name Available")
                        tournament_id = tournament.get("id")
                        tournament_options[name] = tournament_id
                    st.session_state.seasonal_data['tournaments'] = tournament_options
                    st.success("Tournaments fetched successfully!")
                else:
                    st.error("Failed to fetch tournaments.")
    
    # Tournament selection dropdown
    if 'tournaments' in st.session_state.seasonal_data:
        tournament_name = st.selectbox(
            "Select Tournament:",
            options=list(st.session_state.seasonal_data['tournaments'].keys()),
            key="tournament_selector"
        )
        st.session_state.selected_tournament = st.session_state.seasonal_data['tournaments'][tournament_name]
        st.session_state.selections_made = True

# Process tournament data and generate recap
def parse_json_results(json_data):
    event = json_data.get("event", {})
    scopes = event.get("scopes", [{}])
    aggregates = scopes[0].get("aggregates", [])
    players = []
    for agg in aggregates:
        rank = agg.get("rank", "0")
        name = agg.get("name", "Unknown")
        score = agg.get("score", "N/A")
        total = agg.get("total", "N/A")
        to_par_net = agg.get("to_par_net", 0)
        to_par_gross = agg.get("to_par_gross", 0)
        players.append(
            {
                "rank": rank,
                "name": name,
                "score": score,
                "total": total,
                "to_par_net": to_par_net,
                "to_par_gross": to_par_gross,
            }
        )
    players.sort(key=lambda x: int(x["rank"]))
    top_three = players[:3]

    # Extract event name and format
    event_name = event.get("name", "[Event Name Not Found]")
    format_name = event.get("format", "Best Ball")

    return top_three, event_name, format_name

def get_llm_response(llm_api_key, json_data, score_type, llm_choice):
    top_players, event_name, format_name = parse_json_results(json_data)
    message = f"Tournament: {event_name}, Format: {format_name}:\n"

    for player in top_players:
        rank = f"Rank {player['rank']}: {player['name']}"
        par = f"To Par: {player['score']}"
        total = f"Total Gross: {player['total']}"
        message += f"{rank}, {par}, {total}\n"

        par_field = "to_par_gross" if score_type.lower() == "gross" else "to_par_net"
        par_value = player[par_field]
        par_note = "(-2=under, +2=over)"
        message += f"To Par {score_type}: {par_value} {par_note}\n"

    try:
        if llm_choice == "OpenAI":
            client = openai.OpenAI(api_key=llm_api_key)
            template = "Golf recap: {}. Intro, Players, Conclusion."
            sys_msg = template.format(score_type)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
                max_tokens=1000,
                presence_penalty=0.6,
                frequency_penalty=0.2,
            )
            content = response.choices[0].message.content
        elif llm_choice == "Google Gemini":
            genai.configure(api_key=llm_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            template = "Golf recap: {}. Intro, Players, Conclusion.\n\n"
            prompt = template.format(score_type) + message

            response = model.generate_content(prompt)
            content = response.text

        return content
    except Exception as e:
        st.error(f"Error getting {llm_choice} response: {str(e)}")
        return None

# Generate button in main area
if st.session_state.selections_made:
    if st.button("Generate Tournament Recap"):
        if not golf_api_key or not llm_api_key:
            st.error("Please enter all required API keys.")
        else:
            with st.spinner("Fetching tournament results..."):
                results = get_tournament_results(
                    golf_api_key, 
                    st.session_state.selected_event, 
                    st.session_state.selected_round, 
                    st.session_state.selected_tournament
                )
                
                if results:
                    st.session_state.tournament_results = results
                    with st.spinner("Generating recap..."):
                        recap = get_llm_response(
                            llm_api_key, 
                            results, 
                            score_type, 
                            llm_choice
                        )
                        
                        if recap:
                            st.session_state.recap = recap
                            st.success("Recap generated successfully!")
                else:
                    st.error("Failed to fetch tournament results.")

# Results tab
with tab2:
    st.header("Tournament Recap")
    
    if st.session_state.recap:
        st.markdown(st.session_state.recap)
        
        # Export options
        st.download_button(
            label="Download Recap as Text",
            data=st.session_state.recap,
            file_name="tournament_recap.txt",
            mime="text/plain"
        )
        
        # Display raw tournament data (collapsible)
        with st.expander("View Raw Tournament Data"):
            if st.session_state.tournament_results:
                st.json(st.session_state.tournament_results)
    else:
        st.info("Generate a recap to see results here.")
