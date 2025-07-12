# Skill Swap Platform

The Skill Swap Platform is a web application that allows users to exchange skills with one another. Users can create profiles, list skills they offer and want to learn, browse other users' skills, request skill swaps, provide feedback, and manage their profiles. Administrators have additional controls to manage users, skills, and platform-wide messages. The application features a clean, professional design with a blue (#1E3A8A, #3B82F6) and white (#FFFFFF) color theme.

## Features

- **User Authentication**: Sign up, log in, and log out securely.
- **Profile Management**: Update personal details, set availability, and toggle profile visibility (public/private).
- **Skill Management**: Add, delete, and categorize skills as "offered" or "wanted."
- **Skill Browsing**: Search and browse public user profiles and their offered/wanted skills.
- **Swap Requests**: Request skill swaps, accept/reject requests, and delete pending requests.
- **Feedback System**: Provide ratings (1-5) and comments for completed swaps.
- **Admin Dashboard**: Manage users (ban), reject skills, send platform-wide messages, and download usage reports.
- **Error Handling**: Input validation, confirmation prompts for critical actions, and user-friendly error messages.
- **Responsive Design**: Built with Tailwind CSS for a mobile-friendly, visually appealing interface.

## Technology Stack

- **Backend**: Flask (Python) for routing, session management, and API endpoints.
- **Database**: SQLite for storing user, skill, swap, and message data.
- **Frontend**: HTML templates with Tailwind CSS (via CDN) for styling and vanilla JavaScript for interactivity.
- **Styling**: Custom CSS (`style.css`) for additional styling, with a blue and white color theme.
- **Session Management**: Flask's session for caching user data (e.g., `user_id`, `is_admin`).

## File Structure

```
skill_swap_platform/
├── app.py                  # Main Flask application
├── config.py               # Flask configuration file
├── schema.sql              # SQLite database schema
├── static/                 # Static files (CSS and JavaScript)
│   ├── style.css           # Custom CSS for additional styling
│   └── script.js           # JavaScript for client-side functionality
├── templates/              # HTML templates for frontend
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   ├── profile.html        # User profile page
│   ├── browse.html         # Browse skills page
│   ├── requests.html       # Swap requests page
│   └── admin.html          # Admin dashboard page
├── skill_swap.db           # SQLite database file (created after running schema.sql)
└── README.md               # Project documentation
```

## Setup Instructions

1. **Prerequisites**:
   - Python 3.6+ installed.
   - SQLite installed (usually included with Python).
   - A modern web browser (e.g., Chrome, Firefox).

2. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd skill_swap_platform
   ```

3. **Install Dependencies**:
   Install Flask using pip:
   ```bash
   pip install flask
   ```

4. **Initialize the Database**:
   Create the SQLite database by running the schema:
   ```bash
   sqlite3 skill_swap.db < schema.sql
   ```

5. **Run the Application**:
   Start the Flask server:
   ```bash
   python app.py
   ```

6. **Access the Platform**:
   Open a browser and navigate to `http://localhost:5000`.

## Usage

1. **Sign Up**: Create an account via the **Signup** page (`/signup`).
2. **Log In**: Access your account via the **Login** page (`/login`).
3. **Profile Management**:
   - Update your name, location, availability, and profile visibility on the **Profile** page (`/profile`).
   - Add or delete skills (offered or wanted).
4. **Browse Skills**: Search for skills or users on the **Browse** page (`/browse`) and request swaps.
5. **Manage Swap Requests**:
   - On the **Requests** page (`/requests`), view pending requests and accept/reject them (as the receiver) or delete your own requests (as the requester).
   - Provide feedback for accepted swaps.
6. **Admin Functions** (for admin users):
   - Access the **Admin Dashboard** (`/admin`) to ban users, reject skills, send messages, or download usage reports.
7. **Log Out**: Use the **Logout** link to end your session.

## Notes

- **Admin Access**: To test admin features, manually set `is_admin = 1` for a user in the `users` table of `skill_swap.db`.
- **Error Handling**: The platform includes input validation, confirmation prompts for critical actions (e.g., deleting skills, accepting/rejecting swaps), and clear error messages.
- **Styling**: Tailwind CSS is used via CDN for rapid development and responsiveness. Custom styles in `style.css` enhance the blue and white theme.
- **Database**: The SQLite database (`skill_swap.db`) is lightweight and suitable for development. For production, consider a more robust database like PostgreSQL.
- **Security**: Passwords are hashed using Werkzeug's `generate_password_hash`. Ensure `SECRET_KEY` in `config.py` is secure for production.

## Troubleshooting

- **No Skills in Swap Modal**: Ensure you have added "offered" skills in your profile (`/profile`). The modal fetches skills via `/api/skills/offered`.
- **Accept/Reject Buttons Missing**: Verify you’re logged in as the receiver of a swap request on the **Requests** page. Only receivers see these buttons.
- **Database Errors**: Ensure `schema.sql` was run correctly to create `skill_swap.db`. Check for typos in the schema.
- **Flask Errors**: Confirm Flask is installed (`pip show flask`) and the server is running (`python app.py`).

## Future Improvements

- Add email notifications for swap requests and acceptances.
- Implement a messaging system for direct user communication.
- Enhance search with filters (e.g., location, skill type).
- Add user ratings aggregation for profile trustworthiness.

## License

This project is licensed under the MIT License.
