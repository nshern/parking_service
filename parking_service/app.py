from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
from flask_marshmallow import Marshmallow
from datetime import datetime
import requests


def get_response(registration_number):
    url = "https://v1.motorapi.dk/vehicles"

    headers = {
        "X-AUTH-TOKEN": os.environ["MOTOR_API_SERVICE"],
    }
    params = {"registration_number": registration_number}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")
        return None

    return response


def get_info(registration_number):
    r = get_response(registration_number)
    if r is not None:
        return {
            "make": r.json()[0]["make"],
            "model": r.json()[0]["model"],
            "variant": r.json()[0]["variant"],
        }


app = Flask(__name__)

# Set up databse
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "parkings.db"
)

db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Database created!")


@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Database dropped!")


@app.cli.command("db_seed")
def db_seed():
    first_parking = ParkingSpace(  # type: ignore
        registration_number="DM24392",
        time="2023-10-17T14:14:45.023502",
        email="example@example.com",
        make="test",
        model="test",
        variant="test",
    )

    db.session.add(first_parking)
    db.session.commit()
    print("Database seeded!")


class ParkingSpace(db.Model):
    __tablename__ = "parking_spaces"
    id = Column(Integer, primary_key=True)
    registration_number = Column(String)
    time = Column(String)
    email = Column(String)
    make = Column(String)
    model = Column(String)
    variant = Column(String)


class ParkingSpaceSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "registration_number",
            "time",
            "email",
            "make",
            "model",
            "variant",
        )


parking_schema = ParkingSpaceSchema()
parkings_schema = ParkingSpaceSchema(many=True)


@app.route("/")
def hello_world():
    return jsonify("Hello, World")


@app.route("/parkings", methods=["GET"])
def parkings():
    parkings_list = ParkingSpace.query.all()
    result = parkings_schema.dump(parkings_list)
    return jsonify(result)


@app.route("/register_parking", methods=["POST"])  # type: ignore
def register_parking():
    registration_number = request.form["registration_number"]
    time = datetime.now().isoformat()
    email = request.form["email"]
    if registration_number is not None:
        info = get_info(registration_number)
        make = info["make"]
        model = info["model"]
        variant = info["variant"]

    new_parking = ParkingSpace(  # type: ignore
        registration_number=registration_number,
        time=time,
        email=email,
        make=make,
        model=model,
        variant=variant,
    )
    db.session.add(new_parking)
    db.session.commit()
    return jsonify(message="You added a new parking"), 201
