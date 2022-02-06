import csv

from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import admin_only, get_user_info, login_required
from owncloud.models.users import UserStatus
from owncloud.models import user_model

from bottle import Bottle, request, HTTPResponse, static_file

app = Bottle()


templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "templates")
env = j.tools.jinja2.get_env(templates_path)

DEPLOYMENT_QUEUE = "DEPLOYMENT_QUEUE"

@app.route("/api/requests", method=["GET"])
@login_required
@admin_only
def list_users():
    """List all users for admin
    """
    users = []
    for user_name in user_model.list_all():
        user = user_model.get(user_name)
        users.append(user.to_dict())
    return HTTPResponse(
        j.data.serializers.json.dumps(users),
        status=200,
        headers={"Content-Type": "application/json"},
    )


@app.route("/api/requests", method=["POST"])
@login_required
def create_user():
    """Create new instance for user if new
    - return 409 if user has registered before
    """
    user_info = j.data.serializers.json.loads(get_user_info())
    username = j.data.text.removesuffix(user_info.get("username"), ".3bot")

    data = j.data.serializers.json.loads(request.body.read())
    email = data.get("email")
    if email == "":
        email = user_info.get("email")

    if username in user_model.list_all():
        return HTTPResponse(
            f"user {username} has already submitted a request. please be patient while we prepare your deployment",
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
        f"Your request will be processed soon. You'll receive your deployment information at {user.email}",
        status=201,
        headers={"Content-Type": "application/json"},
    )


@app.route("/api/deployment", method=["POST"])
@login_required
@admin_only
def deploy_instances():
    """get json file for approved users and generate terraform files for them
    """
    balance = j.tools.http.get("http://localhost:3001/balance").json().get("balance")
    if float(balance) < 1000:
        return HTTPResponse(
        f"Wallet balance is less than 1000 TFT please add more TFTs in the wallet and re-deploy",
        status=403,
        headers={"Content-Type": "application/json"},
    )
    users = j.data.serializers.json.loads(request.body.read())
    
    for username in users:
        user = user_model.get(username)
        if user.status in [UserStatus.APPLY_FAILURE, UserStatus.NEW]:
            user.status = UserStatus.PENDING
            user.save()
            j.core.db.rpush(DEPLOYMENT_QUEUE, j.data.serializers.json.dumps(username))

    return HTTPResponse(
        {"success": True},
        status=200,
        headers={"Content-Type": "application/json"},
    )

@app.route("/api/balance", method=["GET"])
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
