import csv

from jumpscale.core.base import StoredFactory
from jumpscale.loader import j
from jumpscale.packages.auth.bottle.auth import admin_only, get_user_info, login_required
from faucet.models.users import UserModel

from bottle import Bottle, HTTPResponse, static_file

app = Bottle()
user_model = StoredFactory(UserModel)
user_model.always_reload = True

templates_path = j.sals.fs.join_paths(j.sals.fs.dirname(__file__), "templates")
env = j.tools.jinja2.get_env(templates_path)


@app.route("/api/result/get")
@login_required
@admin_only
def history():
    users = []
    for user_name in user_model.list_all():
        user = user_model.get(user_name)
        users.append(user)
    return env.get_template("requests_history.html").render(users=users)


@app.route("/api/result/export")
@login_required
@admin_only
def export():
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


@app.route("/api/submit")
@login_required
def names():
    user_info = j.data.serializers.json.loads(get_user_info())
    username = j.data.text.removesuffix(user_info.get("username"), ".3bot")
    wallet_address = user_info.get("walletAddress")
    email = user_info.get("email")

    if username in user_model.list_all():
        return HTTPResponse(
            f"user {username} has already submitted request before",
            status=409,
            headers={"Content-Type": "application/json"},
        )

    user = user_model.get(username)
    user.tname = username
    user.wallet_address = wallet_address
    user.time = j.data.time.utcnow().timestamp
    user.status = "pending"
    user.email = email
    user.save()
    return HTTPResponse(
        f"Thanks for submission, Request will be processed soon.",
        status=200,
        headers={"Content-Type": "application/json"},
    )

