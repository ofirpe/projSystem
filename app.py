import os

from flask import (
    Flask, render_template, request, abort,
    redirect, url_for
    )
import peewee

from models import (
    Users, Projects, ProjectInvestment,
    database, UserProject, Roles
)


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(_):
    if not database.is_closed():
        database.close()


@app.route('/allusers')
def all_users():
    users_list = [row for row in Users.select().dicts()]
    return render_template('users.j2', users=users_list)


@app.route('/projects/', methods=['GET', 'POST'])
def jsonproj():
    if request.method == 'GET':
        all_proj = [row for row in Projects.select().dicts()]
        selection = request.args.get('selection')
        return_value = Projects.select().where(
                Projects.project_id == selection)

        return render_template(
            'projects.j2', proj=return_value, all_proj=all_proj)


@app.route('/investments')
def investments():
    inv_list = [
        row for row in Projects.select(Projects, ProjectInvestment).join(
            ProjectInvestment).order_by(Projects.project_name).dicts()
    ]
    return render_template('investments.j2', inv=inv_list)


@app.route('/projects/<project_id>')
def proj_investments(project_id):
    selected_proj = [
        row for row in Projects.select(
        ).where(Projects.project_id == project_id).dicts()
    ]

    users_list = [
        row for row in Users.select(
            UserProject.user.first_name,
            UserProject.user.last_name,
            UserProject.role.title,
            ).join(UserProject).join(Roles).switch(
                UserProject).join(Projects).where(
                    Projects.project_id == project_id).dicts()
    ]

    inv_list = [
        row for row in Projects.select(
            Projects, ProjectInvestment).join(ProjectInvestment).order_by(
                Projects.project_name).where(
                    Projects.project_id == project_id).dicts()
    ]

    total = ProjectInvestment.select(peewee.fn.sum(
        ProjectInvestment.investment).alias('sum')).where(
        ProjectInvestment.project_id == project_id).scalar()

    return render_template(
        'proj_investments.j2',
        inv=inv_list,
        proj=selected_proj[0],
        users=users_list,
        total=str(total)
        )


@app.route('/newp', methods=['GET', 'POST'])
def newp():
    if request.method == 'GET':
        return render_template('newp.j2')
    new_project = Projects(**request.form)

    try:
        new_project.save()
    except peewee.IntegrityError:
        return abort(403, 'Project exists')
    return render_template('newp.j2')


@app.route('/newinv', methods=['GET', 'POST'])
def newinv():
    if request.method == 'GET':
        proj = [row for row in Projects.select().dicts()]
        return render_template('newinv.j2', proj=proj)
    new_inv = ProjectInvestment(**request.form)

    try:
        new_inv.save()
    except peewee.IntegrityError as err:
        return str(err)
    return redirect(url_for('investments'))


@app.route('/editinv/<investment_id>', methods=['GET', 'POST'])
def editinv(investment_id):
    inv = [row for row in ProjectInvestment.select(
            ProjectInvestment, Projects).join(Projects).where(
                ProjectInvestment.investment_id == investment_id).dicts()][0]
    if request.method == 'GET':
        return render_template('editinv.j2', inv=inv)
    elif 'update' in request.form:
        params = {
            'investment': request.form['investment'],
            'investment_date': request.form['investment_date'],
        }
        ProjectInvestment.update(**params).where(
            ProjectInvestment.investment_id == investment_id).execute()
        return redirect(url_for('investments'))

    elif 'delete' in request.form:
        try:
            ProjectInvestment.delete().where(
                ProjectInvestment.investment_id == investment_id).execute()
        except peewee.IntegrityError:
            return abort(403, 'cant delete thie project')
        return redirect(url_for('investments'))


@app.route('/newu', methods=['GET', 'POST'])
def newu():
    if request.method == 'GET':
        return render_template('newu.j2', )
    new_user = Users(**request.form)

    try:
        new_user.save()
    except peewee.IntegrityError:
        return abort(403, 'User exists')
    return render_template('newu.j2')


@app.route('/newr', methods=['GET', 'POST'])
def newr():
    if request.method == 'GET':
        return render_template('newr.j2')
    new_role = Roles(**request.form)

    try:
        new_role.save()
    except peewee.IntegrityError:
        return abort(403, 'Role exists')
    return render_template('newr.j2')


@app.route('/manage')
def manage():
    return render_template('manage.j2')


@app.route('/')
def index():
    return render_template('index.j2')


if __name__ == '__main__':
    app.run()
