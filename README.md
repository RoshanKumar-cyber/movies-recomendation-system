# movies-recomendation-system

# 🎬 CinePick — Movie Recommendation System

**Discover your next favorite movie with CinePick!**

CinePick is a movie recommendation web application built with Python and Streamlit. It recommends movies based on similarity to a movie selected by the user and uses The Movie Database (TMDB) API to retrieve movie information and posters.

---

## ✨ Features

* 🎥 **Movie Recommendations** — Discover movies similar to your selected movie.
* 🖼️ **Movie Posters** — Display movie posters using the TMDB API.
* ⭐ **Movie Ratings** — View TMDB ratings when available.
* 📅 **Movie Information** — Explore release dates, genres, and descriptions when available.
* ⚡ **Fast Recommendations** — Uses a precomputed similarity matrix for movie recommendations.
* 🌐 **Interactive Web Interface** — Simple, user-friendly interface built with Streamlit.
* ☁️ **Cloud Deployment** — Deploy the application using Streamlit Community Cloud.

## 🛠️ Tech Stack

| Technology        | Purpose                                        |
| ----------------- | ---------------------------------------------- |
| Python            | Core programming language                      |
| Streamlit         | Web application interface                      |
| Pandas            | Data manipulation and processing               |
| Scikit-learn      | Feature extraction and similarity calculations |
| CountVectorizer   | Convert movie tags into numerical features     |
| Cosine Similarity | Measure similarity between movies              |
| TMDB API          | Retrieve movie details and poster paths        |
| Requests          | Make HTTP requests to the TMDB API             |

## 📂 Project Structure

```text
CinePick/
│
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── movie_list.pkl          # Serialized movie data
├── similarity.pkl          # Precomputed similarity matrix
├── tmdb_5000_movies.csv    # Movie dataset (if required for model building)
├── tmdb_5000_credits.csv   # Movie credits dataset (if required for model building)
└── README.md               # Project documentation
```

**Note:** The required files depend on your implementation. Include the serialized model files and datasets your application actually uses. Do not upload duplicate or unnecessary files.

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CinePick.git
```

Navigate to the project directory:

```bash
cd CinePick
```

Replace `YOUR_USERNAME` with your GitHub username and `CinePick` with your repository name if different.

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include the libraries used by your application, for example:

```text
streamlit
pandas
scikit-learn
requests
```

### 4. Configure the TMDB API key

CinePick uses the TMDB API to retrieve movie information.

Obtain an API key through your TMDB account and configure it using an environment variable rather than hardcoding it in your source code.

On Windows Command Prompt:

```cmd
set TMDB_API_KEY=your_api_key_here
```

On PowerShell:

```powershell
$env:TMDB_API_KEY="your_api_key_here"
```

Update `main.py` to read the key from the environment:

```python
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
```

Ensure that your API requests use this key.

**Security:** Never commit your API key or other credentials to a public GitHub repository.

### 5. Run the application

```bash
streamlit run main.py
```

Streamlit will provide a local URL, typically:

```text
http://localhost:8501
```

Open the URL in your browser to use CinePick.

## 🧠 How It Works

CinePick uses content-based filtering to recommend movies.

1. **Load movie data:** Read the movie dataset and relevant movie information.
2. **Prepare movie features:** Combine relevant movie attributes into descriptive tags.
3. **Vectorize the tags:** Use `CountVectorizer` to convert text into numerical features.
4. **Calculate similarity:** Use cosine similarity to compare movies.
5. **Generate recommendations:** Identify movies with similar feature representations.
6. **Fetch movie details:** Use the TMDB API to retrieve available movie information and poster paths.
7. **Display results:** Present recommendations through the Streamlit interface.

## 🚀 Deployment

### Deploy using Streamlit Community Cloud

1. Push your project to a GitHub repository.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Sign in and connect your GitHub account.
4. Select your CinePick repository.
5. Choose `main.py` as the application entry point.
6. Add `TMDB_API_KEY` under the app's secrets settings.
7. Deploy your application.

If your application requires large datasets or serialized model files, ensure they are available in the deployment environment and fit within its resource limits.

### Streamlit secrets

For deployment, you can store your API key in Streamlit secrets:

```toml
TMDB_API_KEY = "your_api_key_here"
```

Save this in the deployment platform's secrets configuration. Your Python code can read it using:

```python
import streamlit as st

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
```

Use the environment-variable approach, the Streamlit secrets approach, or a carefully designed combination of both. Keep credentials private.

## ⚠️ Limitations

* Recommendations depend on the movie data and similarity model.
* Movie details and posters depend on TMDB API availability.
* Some movies may not have poster images or complete metadata.
* Performance depends on dataset size, similarity matrix size, and available memory.
* Cloud hosting platforms may impose resource and usage limits.

## 🔮 Future Improvements

Potential enhancements include:

* 🔍 Movie search and filtering
* 🎭 Recommendations by genre, cast, or director
* ⭐ Personalized recommendations
* ❤️ Favorite movies and watchlists
* 📊 Improved recommendation algorithms
* 🎨 Enhanced movie cards and responsive UI
* 📈 Recommendation analytics
* 🚀 Improved model performance for larger datasets

## 🙏 Acknowledgements

* **[The Movie Database (TMDB)](https://www.themoviedb.org/)** — Movie metadata and poster images.
* **[Streamlit](https://streamlit.io/)** — Interactive web application framework.
* **[Scikit-learn](https://scikit-learn.org/)** — Machine-learning utilities.

Movie metadata and images are provided by TMDB. This project is not endorsed or certified by TMDB unless explicitly stated.

## 📄 License

Choose a license before distributing this project publicly. If you intend to make the source code open source, consider adding an appropriate `LICENSE` file to the repository.

---

**Built with Python, Streamlit, and a love for movies. 🍿**
