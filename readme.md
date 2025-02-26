# Golf Tournament Recap Generator

A Streamlit web application that generates professional tournament recaps using AI (OpenAI or Google Gemini). This application connects to Golf Genius API to fetch tournament data and uses AI to create engaging and informative recaps.

## Features

- Connects to Golf Genius API to fetch tournament data
- Supports both OpenAI and Google Gemini for generating recaps
- Allows selection of gross or net scores
- Provides a step-by-step process for selecting seasons, events, rounds, and tournaments
- Generates professional recaps with intro, player details, and conclusion
- Enables downloading recap as text

## Setup Instructions

### Prerequisites

- Python 3.8+
- Golf Genius API Key
- OpenAI API Key or Google Gemini API Key

### Local Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/golf-tournament-recap.git
   cd golf-tournament-recap
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. Fork this repository to your GitHub account
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your forked repository
4. Deploy the app

## Usage

1. Enter your Golf Genius API Key and choice of AI model (OpenAI or Google Gemini)
2. Enter the corresponding API key for your selected AI model
3. Select score type (Gross or Net)
4. Follow the step-by-step process to select season, event, round, and tournament
5. Click "Generate Tournament Recap" to generate the recap
6. View and download the generated recap from the Results tab

## Security Notes

- API keys are not stored in the application
- All API keys are entered for each session
- Consider setting environment variables for API keys in production

## License

[MIT License](LICENSE)

## Acknowledgements

- [Golf Genius API](https://www.golfgenius.com/api_v2)
- [OpenAI API](https://openai.com/blog/openai-api)
- [Google Gemini API](https://ai.google.dev/)
- [Streamlit](https://streamlit.io/)
