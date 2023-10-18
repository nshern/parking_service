from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
from flask_marshmallow import Marshmallow
from datetime import datetime
from .motor_api_service import get_info
from flask_mail import Mail, Message


app = Flask(__name__)

# Set up databse
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "parkings.db"
)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Mail configuration
mail = Mail(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "smartlearning.parkingservice@gmail.com"
app.config["MAIL_PASSWORD"] = os.environ.get("SMARTLEARNING_MAIL")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)


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

    # info, make, model, variant = ""
    info = ""
    make = ""
    model = ""
    variant = ""

    if registration_number is not None:
        info = get_info(registration_number)
        print(info)
    if info != "" and type(info) == dict:
        if "make" in info:
            make = info["make"]
        if "model" in info:
            model = info["model"]
        if "variant" in info:
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

    # Send email receipt
    msg = Message(
        "Hello",
        sender="smartlearning.parkingservice@gmail.com",
        recipients=["nashern@protonmail.com"],
    )
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    return (
        jsonify(message="You added a new parking. Receipt send to email"),
        201,
    )
