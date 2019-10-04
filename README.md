# E-store

Simple e-store.

## :camera: Example

<img src="/static/imgs/homepage.png" width="55%"></img>

## To get up and running:

-   If you don't have pipenv, install it with `brew install pipenv`.
-   Clone the directory, `cd` into it, and then run `pipenv shell` followed by `pipenv install`
-   Set your environment variables: `export FLASK_ENV=development`
-   Run the command `flask run` or `python3 store.py` and everything should work!

## Optional:

If you want to use the email functionality on your local machine set envoirment variables `export email:yourgmailacocunt` `export email_password=yourgmailpassword`. After your enviornment variables are set allow applications to connect to gmails smtp server using your credentials by going to `https://myaccount.google.com/lesssecureapps` and allowing less secure apps to connect.
<img src="/static/imgs/mail.png" width="55%"></img>
