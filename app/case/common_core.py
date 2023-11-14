import os
import shutil
import datetime
from .. import db
from ..db_class.db import *
from ..utils.utils import isUUID, create_specific_dir
from sqlalchemy import desc, func
from ..notification import notification_core as NotifModel


UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
TEMP_FOLDER = os.path.join(os.getcwd(), "temp")
HISTORY_FOLDER = os.path.join(os.getcwd(), "history")


def get_case(cid):
    """Return a case by is id"""
    if isUUID(cid):
        case = Case.query.filter_by(uuid=cid).first()
    elif str(cid).isdigit():
        case = Case.query.get(cid)
    else:
        case = None
    return case

def get_task(tid):
    """Return a task by is id"""
    if isUUID(tid):
        case = Task.query.filter_by(uuid=tid).first()
    elif str(tid).isdigit():
        case = Task.query.get(tid)
    else:
        case = None
    return case

def get_all_cases():
    """Return all cases"""
    return Case.query.filter_by(completed=False).order_by(desc(Case.last_modif))

def get_case_by_completed(completed):
    return Case.query.filter_by(completed=completed)

def get_case_by_title(title):
    return Case.query.where(func.lower(Case.title)==func.lower(title)).first()

def get_case_template_by_title(title):
    return Case_Template.query.filter_by(title=title).first()

def search(text):
    """Return cases containing text"""
    return Case.query.where(Case.title.contains(text), Case.completed==False).paginate(page=1, per_page=30, max_per_page=50)


def get_all_users_core(case):
    return Org.query.join(Case_Org, Case_Org.case_id==case.id).where(Case_Org.org_id==Org.id).all()


def get_role(user):
    """Return role for the current user"""
    return Role.query.get(user.role_id)


def get_org(oid):
    """Return an org by is id"""
    return Org.query.get(oid)

def get_org_by_name(name):
    """Return an org by is name"""
    return Org.query.filter_by(name=name).first()

def get_org_order_by_name():
    """Return all orgs order by name"""
    return Org.query.order_by("name")

def get_org_in_case(org_id, case_id):
    return Case_Org.query.filter_by(case_id=case_id, org_id=org_id).first()

def get_org_in_case_by_case_id(case_id):
    return Case_Org.query.filter_by(case_id=case_id).all()

def get_orgs_in_case(case_id):
    """Return orgs present in a case"""
    case_org = Case_Org.query.filter_by(case_id=case_id).all()
    return [Org.query.get(c_o.org_id) for c_o in case_org ]


def get_file(fid):
    return File.query.get(fid)

def get_all_status():
    return Status.query.all()

def get_status(sid):
    return Status.query.get(sid).first()


def get_recu_notif_user(case_id, user_id):
    return Recurring_Notification.query.filter_by(case_id=case_id, user_id=user_id).first()


def get_taxonomies():
    return [taxo.to_json() for taxo in Taxonomy.query.filter_by(exclude=False).all()]

def get_tags(taxos):
    out = dict()
    for taxo in taxos:
        out[taxo] = [tag.to_json() for tag in Taxonomy.query.filter_by(name=taxo).first().tags if not tag.exclude]
    return out

def get_tag(tag):
    return Tags.query.filter_by(name=tag).first()


def get_case_tags(cid):
    return [tag.name for tag in Tags.query.join(Case_Tags, Case_Tags.tag_id==Tags.id).filter_by(case_id=cid).all()]

def get_task_tags(tid):
    return [tag.name for tag in Tags.query.join(Task_Tags, Task_Tags.tag_id==Tags.id).filter_by(task_id=tid).all()]

def get_history(case_uuid):
    try:
        path_history = os.path.join(HISTORY_FOLDER, str(case_uuid))
        with open(path_history, "r") as read_file:
            loc_file = read_file.read().splitlines()
        return loc_file
    except:
        return False
    
def save_history(case_uuid, current_user, message):
    create_specific_dir(HISTORY_FOLDER)
    path_history = os.path.join(HISTORY_FOLDER, str(case_uuid))
    with open(path_history, "a") as write_history:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        write_history.write(f"[{now}]({current_user.first_name} {current_user.last_name}): {message}\n")


def update_last_modif(case_id):
    """Update 'last_modif' of a case"""
    case = Case.query.get(case_id)
    case.last_modif = datetime.datetime.now(tz=datetime.timezone.utc)
    db.session.commit()


def update_last_modif_task(task_id):
    """Update 'last_modif' of a task"""
    if task_id:
        task = Task.query.get(task_id)
        task.last_modif = datetime.datetime.now(tz=datetime.timezone.utc)
        db.session.commit()


def deadline_check(date, time):
    """Combine the date and the time if time exist"""
    deadline = None
    if date and time:
        deadline = datetime.datetime.combine(date, time)
    elif date:
        deadline = date
    
    return deadline


def delete_temp_folder():
    shutil.rmtree(TEMP_FOLDER)