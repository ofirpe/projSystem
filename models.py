import datetime
import os

from peewee import (
    DateField, FloatField, ForeignKeyField, CharField,
    Model, TextField, AutoField,
)

from playhouse.db_url import connect


database = connect(os.environ.get('DATABASE_URL'))


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class Users(BaseModel):
    username = CharField(unique=True)
    first_name = TextField(null=True)
    last_name = TextField(null=True)

    class Meta:
        table_name = 'users'


class Projects(BaseModel):
    project_id = AutoField()
    budget = FloatField(null=True)
    comments = TextField(null=True)
    completion = DateField(null=True)
    forcast = FloatField(null=True)
    project_name = TextField(unique=True)

    class Meta:
        table_name = 'projects'


class Roles(BaseModel):
    role_id = AutoField()
    title = TextField()

    class Meta:
        table_name = 'roles'


class UserProject(BaseModel):
    user = ForeignKeyField(Users, backref='userproject')
    project_id = ForeignKeyField(Projects, backref='userproject')
    role = ForeignKeyField(Roles, backref='userproject')

    class Meta:
        table_name = 'userproject'


class ProjectInvestment(BaseModel):
    investment_id = AutoField()
    investment = FloatField()
    investment_date = DateField(default=datetime.date.today)
    project_id = ForeignKeyField(Projects, backref='investment')

    class Meta:
        table_name = 'project_investment'


def create_db():
    TABLES = [Users, ProjectInvestment, Projects, Roles, UserProject]

    with database.connection_context():
        database.create_tables(TABLES, safe=True)
        database.commit()

    Users.create(
        username='ofirpe',
        first_name='ofir',
        last_name='pesah',
    )
    Users.create(
        username='ronenam',
        first_name='ronen',
        last_name='amitay',
    )
    Users.create(
        username='benal',
        first_name='ben',
        last_name='almog',
    )
    Projects.create(
        budget=1000,
        comments='started on 2019',
        completion=datetime.date(2021, 10, 30),
        forcast=1100,
        project_name='marin',
    )
    Projects.create(
        budget=1030,
        comments='started on 2018',
        completion=datetime.date(2021, 11, 30),
        forcast=2200,
        project_name='fire',
    )
    ProjectInvestment.create(
        investment=100,
        project_id=1
    )
    ProjectInvestment.create(
        investment=135,
        project_id=1
    )
    ProjectInvestment.create(
        investment=143,
        project_id=2
    )
    ProjectInvestment.create(
        investment=1355,
        project_id=2
    )
    Roles.create(
        title='Project manager'
    )
    Roles.create(
        title='Finance BP'
    )
    UserProject.create(
        user=3,
        project_id=1,
        role=1
    )
    UserProject.create(
        user=1,
        project_id=1,
        role=2
    )
    UserProject.create(
        user=3,
        project_id=2,
        role=1
    )
    UserProject.create(
        user=2,
        project_id=2,
        role=2
    )


if __name__ == "__main__":
    create_db()
