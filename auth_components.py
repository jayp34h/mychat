import gradio as gr
from auth import SupabaseAuth

class AuthComponents:
    def __init__(self):
        self.auth = SupabaseAuth()
        self.user_info = None
        self.is_logged_in = False
    
    def create_auth_components(self):
        # Add CSS styles directly
        gr.Markdown("""
        <style>
            .top-bar {
                position: fixed;
                top: 20px;
                right: 20px;
                display: flex;
                gap: 12px;
                z-index: 1000;
                background: rgba(255, 255, 255, 0.9);
                padding: 8px 16px;
                border-radius: 25px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }

            .auth-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                cursor: pointer;
                background-color: #1a73e8;
                color: white;
                transition: all 0.3s ease;
                font-size: 14px;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            .login-btn:hover, .signup-btn:hover {
                transform: translateY(-2px);
            }

            .auth-form {
                position: fixed;
                top: 80px;
                right: 20px;
                background: transparent;
                padding: 20px;
                border-radius: 8px;
                width: 300px;
                z-index: 1000;
            }

            .user-profile {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            }
        </style>
        """)
        
        # Hidden components to store auth state
        with gr.Row(visible=False) as hidden_row:
            user_id = gr.Textbox(visible=False, elem_id="user_id")
            user_email = gr.Textbox(visible=False, elem_id="user_email")
            auth_status = gr.Textbox(visible=False, elem_id="auth_status")
        
        # Auth UI components - positioned at top right corner
        with gr.Row() as auth_row:
            # Initial state - Login/Signup buttons (compact, modern design)
            with gr.Column(visible=True, elem_classes=["top-bar"]) as auth_buttons:
                with gr.Row():
                    login_btn = gr.Button("Login", elem_classes=["auth-btn"])
                    signup_btn = gr.Button("Signup", elem_classes=["auth-btn"])
            
            # Login form (initially hidden)
            with gr.Column(visible=False, elem_classes=["auth-form"]) as login_form:
                gr.Markdown("### Login")
                login_email = gr.Textbox(label="Email", placeholder="Enter your email")
                login_password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                with gr.Row():
                    login_submit = gr.Button("Login", elem_classes=["submit-btn"])
                    login_cancel = gr.Button("Cancel", elem_classes=["cancel-btn"])
                login_message = gr.Markdown("")
            
            # Signup form (initially hidden)
            with gr.Column(visible=False, elem_classes=["auth-form"]) as signup_form:
                gr.Markdown("### Signup")
                signup_email = gr.Textbox(label="Email", placeholder="Enter your email")
                signup_password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                signup_confirm = gr.Textbox(label="Confirm Password", placeholder="Confirm your password", type="password")
                with gr.Row():
                    signup_submit = gr.Button("Signup", elem_classes=["submit-btn"])
                    signup_cancel = gr.Button("Cancel", elem_classes=["cancel-btn"])
                signup_message = gr.Markdown("")
            
            # User profile (initially hidden - only shown after login)
            with gr.Column(visible=False, elem_classes=["user-profile"]) as user_profile:
                with gr.Row():
                    gr.Markdown(elem_id="profile_email", value="")
                    logout_btn = gr.Button("Logout", elem_classes=["logout-btn"], visible=False)
        
        # Event handlers
        def show_login_form():
            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        
        def show_signup_form():
            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
        
        def cancel_form():
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        
        def handle_login(email, password):
            if not email or not password:
                return "", "Please enter both email and password"
            
            success, message = self.auth.login(email, password)
            if success:
                user = self.auth.get_user()
                self.user_info = user
                self.is_logged_in = True
                return (
                    user.id if user else "",
                    user.email if user else "",
                    "logged_in",
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=True, value=f"### {user.email if user else 'User'}"),
                    ""
                )
                # Also update the logout button to be visible
                logout_btn.update(visible=True)
            return "", "", "", gr.update(), gr.update(), gr.update(), gr.update(), message
        
        def handle_signup(email, password, confirm_password):
            if not email or not password or not confirm_password:
                return gr.update(visible=True), "Please fill in all fields"
            
            if password != confirm_password:
                return gr.update(visible=True), "Passwords do not match"
            
            success, message = self.auth.signup(email, password)
            
            if success:
                # Show success message and hide the form
                return gr.update(visible=False), "✅ Email verification sent! Please check your inbox to confirm your account."
            else:
                # Show error message
                return gr.update(visible=True), message
        
        def handle_logout():
            success, message = self.auth.logout()
            self.user_info = None
            self.is_logged_in = False
            return "", "", "", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        
        # Connect event handlers
        login_btn.click(show_login_form, outputs=[auth_buttons, login_form, signup_form, user_profile])
        signup_btn.click(show_signup_form, outputs=[auth_buttons, login_form, signup_form, user_profile])
        
        login_cancel.click(cancel_form, outputs=[auth_buttons, login_form, signup_form, user_profile])
        signup_cancel.click(cancel_form, outputs=[auth_buttons, login_form, signup_form, user_profile])
        
        login_submit.click(
            handle_login,
            inputs=[login_email, login_password],
            outputs=[user_id, user_email, auth_status, auth_buttons, login_form, signup_form, user_profile, login_message]
        )
        
        signup_submit.click(
            handle_signup,
            inputs=[signup_email, signup_password, signup_confirm],
            outputs=[signup_form, signup_message]
        )
        
        logout_btn.click(
            handle_logout,
            outputs=[user_id, user_email, auth_status, auth_buttons, login_form, signup_form, user_profile]
        )
        
        return {
            "components": {
                "user_id": user_id,
                "user_email": user_email,
                "auth_status": auth_status,
                "auth_row": auth_row,
                "auth_buttons": auth_buttons,
                "login_form": login_form,
                "signup_form": signup_form,
                "user_profile": user_profile
            },
            "handlers": {
                "show_login": show_login_form,
                "show_signup": show_signup_form,
                "cancel": cancel_form,
                "login": handle_login,
                "signup": handle_signup,
                "logout": handle_logout
            }
        }