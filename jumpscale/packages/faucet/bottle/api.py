import csv

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import admin_only, get_user_info, login_required
from faucet.models.users import UserModel, UserStatus

from bottle import Bottle, request, HTTPResponse, static_file

app = Bottle()
user_model = StoredFactory(UserModel)
user_model.always_reload = True

templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "templates")
env = j.tools.jinja2.get_env(templates_path)


@app.route("/api/requests", methods=["GET"])
@login_required
@admin_only
def list_users():
    """List all users for admin
    """
    users = []
    for user_name in user_model.list_all():
        user = user_model.get(user_name)
        users.append(user)
    return HTTPResponse(
        users,
        status=200,
        headers={"Content-Type": "application/json"},
    )


@app.route("/api/requests", methods=["POST"])
@login_required
def create_user():
    """Create new instance for user if new
    - return 409 if user has registered before
    """
    user_info = j.data.serializers.json.loads(get_user_info())
    username = j.data.text.removesuffix(user_info.get("username"), ".3bot")

    data = j.data.serializers.json.loads(request.body.read())
    email = data.get("email", user_info.get("email"))

    if username in user_model.list_all():
        return HTTPResponse(
            f"user {username} has already submitted request before",
            status=409,
            headers={"Content-Type": "application/json"},
        )

    user = user_model.get(username)
    user.tname = username
    user.email = email
    user.status = UserStatus.NEW
    user.time = j.data.time.utcnow().timestamp
    user.save()
    return HTTPResponse(
        f"Thanks for submission, Request will be processed soon.",
        status=200,
        headers={"Content-Type": "application/json"},
    )


@app.route("/api/deployment", methods=["POST"])
@login_required
@admin_only
def deploy_instances():
    """get json file for approved users and generate terraform files for them
    """
    balance = j.tools.http.get("http://localhost:3001/balance").json().get("balance")
    if balance < 1000:
        return HTTPResponse(
        f"Wallet balance is less than 1000 TFT please add more TFTs in the wallet and re-deploy",
        status=403,
        headers={"Content-Type": "application/json"},
    )
    users = j.data.serializers.json.loads(request.body.read())
    for username in users:
        user = user_model.get(username)
        user.status = UserStatus.DONE
        user.save()

    return HTTPResponse(
        {"success": True},
        status=201,
        headers={"Content-Type": "application/json"},
    )

@app.route("/api/balance", methods=["GET"])
@login_required
@admin_only
def get_balance():
    """get the main wallet current balance
    """
    balance = j.tools.http.get("http://localhost:3001/balance").json()
    return HTTPResponse(
        balance,
        status=200,
        headers={"Content-Type": "application/json"},
    )

@app.route("/api/requests/export")
@login_required
@admin_only
def export():
    """Export saved users as csv 
    """
    users = []
    for user_name in user_model.list_all():
        order = user_model.get(user_name)
        users.append(order.to_dict())

    if not users:
        return {"Error": "File not found"}

    path = j.sals.fs.join_paths(j.core.dirs.BASEDIR, "exports")
    j.sals.fs.mkdirs(path)
    time_now = j.data.time.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"export_{time_now}.csv"
    filepath = j.sals.fs.join_paths(path, filename)
    keys = list(users[0].keys())
    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(keys)
        for user in users:
            writer.writerow(user[k] for k in keys)

    return static_file(filename, root=path, download=filename)
