from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime
import operator

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    
    # store user's current account balance and initialize total account value
    balance = db.execute("SELECT cash FROM users WHERE id = :user", user=session["user_id"])[0]["cash"]
    account_value = balance

    # extract all records for user from holdings table
    holdings_records = db.execute("SELECT * FROM holdings WHERE user_id = :user", \
        user=session["user_id"])
    
    # strip out records with current holdings of 0 shares
    current_holdings = [holding for holding in holdings_records if holding["no_shares"]]
    
    # add current price and holding value to each held stock
    # update account value with value of each stock
    # format value and price to USD standards
    for holding in current_holdings:
        holding.update({"price": lookup(holding["symbol"])["price"]})
        holding.update({"value": holding["price"] * holding["no_shares"]})
        account_value += holding["value"]
        holding.update({"value": usd(holding["value"])})
        holding.update({"price": usd(holding["price"])})
    
    # sort by symbol
    # code from https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
    current_holdings.sort(key = operator.itemgetter('symbol'))
    
    return render_template("index.html", stocks=current_holdings, balance=usd(balance), account_value=usd(account_value))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # confirm user entered a stock symbol and purchase quantity
        if not request.form.get("symbol") or not request.form.get("no_shares"):
            return apology("All fields required")
        
        # store entered symbol and number of shares (as float for cost math)
        symbol = request.form.get("symbol").upper()
        try:
            no_shares = int(request.form.get("no_shares"))
        except ValueError:
            return apology("Must enter a number")
            
        # confirm user entered a purchase quantity > 0
        if int(request.form.get("no_shares")) <= 0:
            return apology("Must purchase at least 1 share, you goof")
        
        # lookup stock's info
        quote = lookup(symbol)
        
        # if symbol incorrect, display error message
        if quote is None:
            return apology("Symbol does not exist")
        else:
            # store current date and cost of proposed purchase
            date = datetime.datetime.now()
            cost = no_shares * quote["price"]
            # fetch user's current balance
            balance = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])
            # if user has adequate funds, add transaction to database and reduce user's total funds
            if balance[0]["cash"] >= cost:
                db.execute("INSERT INTO transactions \
                    (user_id, transaction_type_id, symbol, no_shares, price_per_share, total, datetime) \
                    VALUES (:user, :tran_type, :symbol, :no_shares, :price, :total, :datetime)", \
                    user=session["user_id"], \
                    tran_type="b", \
                    symbol=symbol, \
                    no_shares=no_shares, \
                    price=quote["price"], \
                    total=cost, \
                    datetime=str(date.strftime("%b %m %Y - %I:%M:%S %p")))
                db.execute("UPDATE users SET cash = cash - :cost WHERE id = :user", \
                    cost=cost, \
                    user=session["user_id"])
                
                # determine if user already owns shares in this stock
                already_owned = db.execute( \
                    "SELECT no_shares FROM holdings WHERE user_id = :user AND symbol = :symbol", \
                    user=session["user_id"], \
                    symbol=symbol)

                # if user already owns shares or has in the past, update number of shares owned
                if len(already_owned):
                    db.execute( \
                        "UPDATE holdings SET no_shares = no_shares + :no_shares \
                        WHERE user_id = :user AND symbol = :symbol", \
                        no_shares=no_shares, \
                        user=session["user_id"], \
                        symbol=symbol)
                # else create record for new share holdings
                else:
                    db.execute( \
                        "INSERT INTO holdings (user_id, symbol, no_shares) \
                        VALUES(:user, :symbol, :no_shares)", \
                        user=session["user_id"], \
                        symbol=symbol, \
                        no_shares=no_shares)
            # if user has inadequate funds, display message
            else:
                return apology("Insufficient funds to complete transaction")
        
        # return user to index page after transaction
        return redirect(url_for("index"))
    
    # else if user reached route via GET (as by clicking a link or via redirect)      
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    
    # get all of user's transactions from the database
    transactions = db.execute(" \
        SELECT ttc.literal, t.symbol, t.no_shares, t.price_per_share, t.total, t.datetime \
        FROM transactions t \
        JOIN transaction_type_cd ttc ON ttc.id = t.transaction_type_id \
        WHERE user_id = :user", user=session["user_id"])
    
    # capitalize transaction type code
    # apply USD formatting to all money values
    for trans in transactions:
        trans.update({"literal": trans["literal"].capitalize()})
        trans.update({"price_per_share": usd(trans["price_per_share"])})
        trans.update({"total": usd(trans["total"])})
    
    return render_template("history.html", history=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))
    
@app.route("/reset", methods=["GET", "POST"])
@login_required
def reset():
    """Reset password"""
    
    if request.method == "POST":
        
        # store form entries and current user ID
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        new_password_conf = request.form.get("new_password_confirm")
        user_id = session["user_id"]
        
        # confirm user entered data in all fields
        if not current_password or not new_password or not new_password_conf:
            return apology("All fields are required")
        elif not new_password == new_password_conf:
            return apology("New password and confirmation did not match")
        

        # compare current password entered on form to current password in database
        db_hash = db.execute("SELECT hash FROM users WHERE id = :user", user=user_id)
        if not pwd_context.verify(current_password, db_hash[0]["hash"]):
            return apology("Incorrect current password entered")
        else:
            db.execute("UPDATE users SET hash = :pwd WHERE id = :user", \
                pwd=pwd_context.hash(new_password), \
                user=user_id)
            return redirect(url_for("index"))
        
    else:
        return render_template("reset.html")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # store symbol
        symbol = request.form.get("symbol")
        
        # get quote
        quote = lookup(symbol)
        
        # return apology if symbol does not exist
        if quote is None:
            return apology("Symbol does not exist")
        # else reload page with data for entered symbol
        else:
            return render_template("quote.html", name=quote["name"], symbol=quote["symbol"], price=usd(quote["price"]))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    
    # clear any current user ID
    session.clear()
    
    # if user accessed via POST
    if request.method == "POST":
        
        # ensure username entered
        if not request.form.get("username"):
            return apology("Username required")
            
        # ensure password fields are not blank
        elif not request.form.get("password") or not request.form.get("password2"):
            return apology("Password required")
            
        # ensure passwords match
        elif not request.form.get("password") == request.form.get("password2"):
            return apology("Passwords did not match")
            
        # check database to see if user exists and print message if so, otherwise register user
        id_exists = db.execute("SELECT id FROM users WHERE username = :username", username=request.form.get("username"))
        if len(id_exists) != 0:
            return apology("Username already exists")
        else:
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :pwd)", username=request.form.get("username"), pwd=pwd_context.hash(request.form.get("password")))
            
       # automatically log in user
        result = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        session["user_id"] = result[0]["id"]
        
        # return user to homepage
        return redirect(url_for("index"))
    
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    
    # if user accessed via POST
    if request.method == "POST":
        
        # confirm user entered symbol and number of shares to sell
        if not request.form.get("symbol") or not request.form.get("no_shares"):
            return apology("All fields required")
            
        # get symbol and number of stocks entered on form
        symbol = request.form.get("symbol").upper()
        try:
            no_shares = int(request.form.get("no_shares"))
        except ValueError:
            return apology("You must enter a number")
            
        # confirm stock symbol is real
        stock = lookup(symbol)
        if stock is None:
            return apology("Symbol does not exist")
        
        # confirm user did not enter 0 shares
        if no_shares == 0:
            return apology("Cannot sell 0 shares, you goof")
            
        # confirm user did not enter negative shares
        if no_shares < 0:
            return apology("Must enter positive number of shares")

        # confirm user has shares to sell
        current_holding = db.execute("SELECT no_shares FROM holdings \
            WHERE user_id = :user AND symbol = :symbol", \
            user=session["user_id"], 
            symbol=symbol)
       
        if current_holding is None or current_holding[0]["no_shares"] == 0:
            return apology("You do not have shares to sell")
        
        # confirm number entered is not greater than holding
        if no_shares > current_holding[0]["no_shares"]:
            return apology("You only own " + str(current_holding[0]["no_shares"]) + " shares")
        
        # calculate total of sale
        sale_total = no_shares * stock["price"]
        
        # store time of transaction
        date = datetime.datetime.now()
        
        # log transaction
        db.execute("INSERT INTO transactions \
            (user_id, transaction_type_id, symbol, no_shares, price_per_share, total, datetime) \
            VALUES (:user, :tran_type, :symbol, :no_shares, :price, :total, :datetime)", \
            user=session["user_id"], \
            tran_type="s", \
            symbol=symbol, \
            no_shares=no_shares, \
            price=stock["price"], \
            total=sale_total, \
            datetime=str(date.strftime("%b %m %Y - %I:%M:%S %p")))
        
        # update user's cash balance
        db.execute("UPDATE users SET cash = cash + :total WHERE id = :user", \
            total=sale_total, \
            user=session["user_id"])
        
        # update user's holdings
        db.execute("UPDATE holdings SET no_shares = no_shares - :no_shares \
            WHERE user_id = :user AND symbol = :symbol", \
            no_shares=no_shares, \
            user=session["user_id"], \
            symbol=symbol)
        
        return redirect(url_for("index"))
        
    else: 
        return render_template("sell.html")
