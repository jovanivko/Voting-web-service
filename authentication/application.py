import re

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, UserRole
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from admin.decorator import role_check

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/register", methods=["POST"])
def register():
    jmbg = request.json.get("jmbg", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    jmbgEmpty = len(jmbg) == 0
    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if jmbgEmpty:
        return jsonify(message="Field jmbg is missing."), 400
    if forenameEmpty:
        return jsonify(message="Field forename is missing."), 400
    if surnameEmpty:
        return jsonify(message="Field surname is missing."), 400
    if emailEmpty:
        return jsonify(message="Field email is missing."), 400
    if passwordEmpty:
        return jsonify(message="Field password is missing."), 400

    m = 11 - ((7 * (int(jmbg[0]) + int(jmbg[6])) + 6 * (int(jmbg[1]) + int(jmbg[7])) + 5 * (
            int(jmbg[2]) + int(jmbg[8])) + 4 * (int(jmbg[3]) + int(jmbg[9])) + 3 * (
                       int(jmbg[4]) + int(jmbg[10])) + 2 * (int(jmbg[5]) + int(jmbg[11]))) % 11)
    if m >= 10:
        m = 0

    if (len(jmbg) != 13 or ((re.compile('^[0-9]{13}$')).fullmatch(jmbg) is None) or (int(jmbg[0:2]) not in range(1, 32)) or (int(jmbg[2:4]) not in range(1, 13)) or (int(jmbg[4:7]) not in range(0, 1000)) or (int(jmbg[7:9]) not in range(70, 100)) or (int(jmbg[9:12]) not in range(0, 1000)) or (int(jmbg[-1]) != m)):
        return jsonify(message="Invalid jmbg."), 400

    result = parseaddr(email)
    if len(result[1]) == 0:
        return jsonify(message="Invalid email."), 400

    if (len(password) < 8 or ((re.compile('[0-9]+')).search(password) is None) or ((re.compile('[a-z]+')).search(password) is None) or ((re.compile('[A-Z]+')).search(password) is None)):
        return jsonify(message="Invalid password."), 400

    user = User.query.filter(User.email == email).first();
    if user:
        return jsonify(message="Email already exists"), 400

    user = User(jmbg=jmbg, email=email, forename=forename, surname=surname, password=password)
    database.session.add(user)
    database.session.commit()

    userRole = UserRole(userId=user.id, roleId=2);
    database.session.add(userRole);
    database.session.commit();

    return Response(status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "");
    password = request.json.get("password", "");

    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;

    if emailEmpty:
        return jsonify(message="Field email is missing"), 400

    if passwordEmpty:
        return jsonify(message="Field password is missing"), 400

    result = parseaddr(email)
    if len(result[1]) == 0:
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first();

    if not user:
        return jsonify(message="Invalid credentials."), 400

    additionalClaims = {
        "jmbg": user.jmbg,
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);

    return jsonify(accessToken=accessToken, refreshToken=refreshToken);


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    additionalClaims = {
        "jmbg": refreshClaims.jmbg,
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    };

    return Response(create_access_token(identity=identity, additional_claims=additionalClaims), status=200);


@application.route("/delete", methods=["POST"])
@jwt_required()
@role_check(role= "admin")
def delete():
    email = request.json.get("email", "");
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    result = parseaddr(email)
    if (len(result[1]) == 0):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify(message="Unknown user."), 400

    userRole = UserRole.query.filter(UserRole.userId == user.id).all()

    for userrole in userRole:
        database.session.delete(userrole)
        database.session.commit()

    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


@application.route("/", methods=["GET"])
def index():
    return "Hello world!";


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug=True, host="0.0.0.0", port=5000);
