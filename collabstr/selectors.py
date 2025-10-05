# Central place to tweak DOM selectors
LISTING_ITEM = "div.profile-listing-holder"
PROFILE_LINK_REL = "a[href^='/'']".replace("''","'")  # ensure raw single quote in file
NAME_ON_PROFILE = "span.profile-name-desktop"
INSTAGRAM_LINK = "a[data-platform='instagram']"

USERNAME_INPUT = "input[name='email'], input[type='email'], input#email"
PASSWORD_INPUT = "input[name='password'], input[type='password'], input#password"
LOGIN_BUTTON   = "button[type='submit'], button:has-text('Login'), button:has-text('Sign in')"
