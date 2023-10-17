from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
from flask_marshmallow import Marshmallow

# from motor_api_service import get_info


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
        time="16:44",
        email="example@example.com",
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


class ParkingSpaceSchema(ma.Schema):
    class Meta:
        fields = ("id", "registration_number", "time", "email")


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
    test = ParkingSpace.query.filter_by(
        registration_number=registration_number
    ).first()
    if test:
        return jsonify("There is already a registration by that name")
    else:
        time = request.form["time"]
        email = request.form["email"]

        new_parking = ParkingSpace(  # type: ignore
            registration_number=registration_number, time=time, email=email
        )
        db.session.add(new_parking)
        db.session.commit()
        return jsonify(message="You added a new parking"), 201
