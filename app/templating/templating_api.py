from flask import Blueprint, request
from .TemplateCase import TemplateModel
from .TaskTemplateCore import TaskModel
from . import validation_api as ApiTemplateModel
from . import common_template_core as CommonModel
from ..utils import utils

from flask_restx import Api, Resource
from ..decorators import api_required


api_templating_blueprint = Blueprint('api_templating', __name__)
api = Api(api_templating_blueprint,
        title='flowintel API', 
        description='API to manage a case management instance.', 
        version='0.1', 
        default='GenericAPI', 
        default_label='Generic flowintel API', 
        doc='/doc'
    )



@api.route('/cases')
@api.doc(description='Get all case template')
class GetCaseTemplates(Resource):
    method_decorators = [api_required]
    def get(self):
        templates = CommonModel.get_all_case_templates()
        return {"templates": [template.to_json() for template in templates]}, 200
    
@api.route('/case/<cid>')
@api.doc(description='Get a case template', params={'cid': 'id of a case template'})
class GetCaseTemplate(Resource):
    method_decorators = [api_required]
    def get(self, cid):
        case_template = CommonModel.get_case_template(cid)
        if case_template:
            loc_case = case_template.to_json()
            tasks_template = CommonModel.get_task_by_case(cid)
            loc_case["tasks"] = [task_template.to_json() for task_template in tasks_template]
            return loc_case, 200
        return {"message": "Case template not found"}, 404
    

@api.route('/case/title', methods=["POST"])
@api.doc(description='Get a case by title')
class GetCaseTitle(Resource):
    method_decorators = [api_required]
    @api.doc(params={"title": "Title of a case"})
    def post(self):
        if "title" in request.json:
            case = CommonModel.get_case_by_title(request.json["title"])
            if case:
                case_json = case.to_json()          
                return case_json, 200
            return {"message": "Case not found"}, 404
        return {"message": "Need to pass a title"}, 404


@api.route('/create_case')
@api.doc(description='Create a new case template')
class CreateCaseTemaplte(Resource):
    method_decorators = [api_required]
    @api.doc(params={
            "title": "Required. Title for the template",
            "description": "Description of the template",
            "tags": "list of tags from taxonomies",
            "clusters": "list of tags from galaxies",
            "custom_tags" : "List of custom tags created on the instance",
            "time_required": "Time required to realize the case"
        })
    def post(self):
        if request.json:
            verif_dict = ApiTemplateModel.verif_create_case_template(request.json)
            if "message" not in verif_dict:
                template = TemplateModel.create_case(verif_dict)
                return {"message": f"Template created, id: {template.id}"}, 201
            return verif_dict, 400
        return {"message": "Please give data"}, 400
    
@api.route('/edit_case/<cid>')
@api.doc(description='Edit a case template', params={'cid': 'id of a case template'})
class EditCaseTemaplte(Resource):
    method_decorators = [api_required]
    @api.doc(params={
            "title": "Title for the template",
            "description": "Description of the template",
            "tags": "list of tags from taxonomies",
            "clusters": "list of tags from galaxies",
            "custom_tags" : "List of custom tags created on the instance"
        })
    def post(self, cid):
        if request.json:
            verif_dict = ApiTemplateModel.verif_edit_case_template(request.json, cid)
            if "message" not in verif_dict:
                TemplateModel.edit(verif_dict, cid)
                return {"message": f"Template case edited"}, 200
            return verif_dict, 400
        return {"message": "Please give data"}, 400
    

@api.route('/case/<cid>/add_tasks')
@api.doc(description='Add a task template to a case template', params={'cid': 'id of a case template'})
class AddTaskCase(Resource):
    method_decorators = [api_required]
    @api.doc(params={
        "tasks": "List of id of tasks template"
        })
    def post(self, cid):
        template = CommonModel.get_case_template(cid)
        if template:
            if request.json:
                if 'tasks' in request.json:
                    form_dict = request.json
                    TemplateModel.add_task_case_template(form_dict, cid)
                    return {"message": "Tasks added"}, 200
                return {"message": "The list 'tasks' is missing"}, 400
            return {"message": "Please give data"}, 400
        return {"message": "Case template not found"}, 404
    

@api.route('/case/<cid>/remove_task/<tid>')
@api.doc(description='Delete a case template', params={'cid': 'id of a case template', 'tid': 'id of the task template'})
class RemoveTaskCaseTemplate(Resource):
    method_decorators = [api_required]
    def get(self, cid, tid):
        if CommonModel.get_case_template(cid):
            if CommonModel.get_task_template(tid):
                if TemplateModel.remove_task_case(cid, tid):
                    return {"message": "Task template removed"}, 200
                return {"message": "Error task template removed"}, 400
            return {"message": "Task template not found"}, 404
        return {"message": "Case template not found"}, 404
    

@api.route('/delete_case/<cid>')
@api.doc(description='Delete a case template', params={'cid': 'id of a case template'})
class DeleteCaseTemplate(Resource):
    method_decorators = [api_required]
    def get(self, cid):
        if CommonModel.get_case_template(cid):
            if TemplateModel.delete_case(cid):
                return {"message": "Case template deleted"}, 200
            return {"message": "Error case template deleted"}, 400
        return {"message": "Template not found"}, 404
    

@api.route('/create_case_from_template/<cid>')
@api.doc(description='Create a case from a case template', params={'cid': 'id of a case template'})
class CreateCaseFromTemplate(Resource):
    method_decorators = [api_required]
    @api.doc(params={
        "title": "Title of the case to create"
        })
    def post(self, cid):
        template = CommonModel.get_case_template(cid)
        if template:
            if request.json:
                if "title" in request.json:
                    new_case = TemplateModel.create_case_from_template(cid, request.json["title"], utils.get_user_api(request.headers["X-API-KEY"]))
                    if type(new_case) == dict:
                        return new_case
                    return {"message": f"New case created, id: {new_case.id}"}, 201
                return {"message": "The field 'title' is missing"}, 400
            return {"message": "Please give data"}, 400
        return {"message": "Case template not found"}, 404
    

@api.route('/get_taxonomies_case/<cid>', methods=["GET"])
@api.doc(description='Get Taxonomies of a case', params={'cid': 'id of a case template'})
class GetTaxonomiesCase(Resource):
    method_decorators = [api_required]
    def get(self, cid):
        case = CommonModel.get_case_template(cid)
        if case:
            tags = CommonModel.get_case_template_tags(case.id)
            taxonomies = []
            if tags:
                taxonomies = [tag.split(":")[0] for tag in tags]
            return {"tags": tags, "taxonomies": taxonomies}
        return {"message": "Case Not found"}, 404
    

@api.route('/get_galaxies_case/<cid>', methods=["GET"])
@api.doc(description='Get Galaxies of a case', params={'cid': 'id of a case template'})
class GetGalaxiesCase(Resource):
    method_decorators = [api_required]
    def get(self, cid):
        case = CommonModel.get_case_template(cid)
        if case:
            clusters = CommonModel.get_case_clusters(case.id)
            galaxies = []
            if clusters:
                for cluster in clusters:
                    loc_g = CommonModel.get_galaxy(cluster.galaxy_id)
                    if not loc_g.name in galaxies:
                        galaxies.append(loc_g.name)
                    index = clusters.index(cluster)
                    clusters[index] = cluster.tag
            return {"clusters": clusters, "galaxies": galaxies}
        return {"message": "Case Not found"}, 404

##########
## Task ##
##########


@api.route('/tasks')
@api.doc(description='Get all task template')
class GetTaskTemplates(Resource):
    method_decorators = [api_required]
    def get(self):
        templates = CommonModel.get_all_task_templates()
        return {"templates": [template.to_json() for template in templates]}, 200
    
@api.route('/task/<tid>')
@api.doc(description='Get a task template', params={'tid': 'id of a task template'})
class GetTaskTemplate(Resource):
    method_decorators = [api_required]
    def get(self, tid):
        template = CommonModel.get_task_template(tid)
        if template:
            return template.to_json(), 200
        return {"message": "Task template not found"}, 404
    
@api.route('/case/<cid>/task/<tid>')
@api.doc(description='Get a task template by case', params={'cid': 'id of a case template', 'tid': 'id of a task template'})
class GetTaskTemplateByCase(Resource):
    method_decorators = [api_required]
    def get(self, cid, tid):
        case = CommonModel.get_case_template(cid)
        if case:
            template = CommonModel.get_task_template(tid)
            if template:
                loc = CommonModel.get_task_by_case_class(cid, tid)
                if loc:
                    loc_template = template.to_json()
                    loc_template["case_order_id"] = loc.case_order_id
                    return loc_template, 200
                return {"message": "Task template not in this case template"}, 404
            return {"message": "Task template not found"}, 404
        return {"message": "Case template not found"}, 404

@api.route('/create_task')
@api.doc(description='Create new task template')
class CreateTaskTemaplte(Resource):
    method_decorators = [api_required]
    @api.doc(params={
            "title": "Required. Title for the template",
            "description": "Description of the template",
            "tags": "list of tags from taxonomies",
            "clusters": "list of tags from galaxies",
            "custom_tags" : "List of custom tags created on the instance",
            "time_required": "Time required to realize the task"
        })
    def post(self):
        if request.json:
            verif_dict = ApiTemplateModel.verif_add_task_template(request.json)
            if "message" not in verif_dict:
                template = TaskModel.add_task_template_core(verif_dict)
                return {"message": f"Template created, id: {template.id}"}, 201
            return verif_dict, 400
        return {"message": "Please give data"}, 400
    

@api.route('/edit_task/<tid>')
@api.doc(description='Edit new case template', params={'tid': 'id of a task template'})
class EditCaseTemaplte(Resource):
    method_decorators = [api_required]
    @api.doc(params={
            "title": "Title for the template",
            "description": "Description of the template",
            "url": "Link to a tool or a ressource",
            "tags": "list of tags from taxonomies",
            "clusters": "list of tags from galaxies",
            "custom_tags" : "List of custom tags created on the instance"
        })
    def post(self, tid):
        if request.json:
            verif_dict = ApiTemplateModel.verif_edit_task_template(request.json, tid)
            if "message" not in verif_dict:
                TaskModel.edit_task_template(verif_dict, tid)
                return {"message": f"Template edited"}, 200
            return verif_dict, 400
        return {"message": "Please give data"}, 400
    

@api.route('/delete_task/<tid>')
@api.doc(description='Delete a task template')
class DeleteTaskTemplate(Resource):
    method_decorators = [api_required]
    def get(self, tid):
        if CommonModel.get_task_template(tid):
            if TaskModel.delete_task_template(tid):
                return {"message": "Task template deleted"}, 200
            return {"message": "Error task template deleted"}, 400
        return {"message": "Template not found"}, 404
    

@api.route('/get_taxonomies_task/<tid>', methods=["GET"])
@api.doc(description='Get Taxonomies of a task', params={'tid': 'id of a task template'})
class GetTaxonomiesTask(Resource):
    method_decorators = [api_required]
    def get(self, tid):
        task = CommonModel.get_task_template(tid)
        if task:
            tags = CommonModel.get_task_template_tags(task.id)
            taxonomies = []
            if tags:
                taxonomies = [tag.split(":")[0] for tag in tags]
            return {"tags": tags, "taxonomies": taxonomies}
        return {"message": "Task Not found"}, 404
    
@api.route('/get_galaxies_task/<tid>', methods=["GET"])
@api.doc(description='Get Galaxies of a task', params={'tid': 'id of a task template'})
class GetGalaxiesTask(Resource):
    method_decorators = [api_required]
    def get(self, tid):
        task = CommonModel.get_task_template(tid)
        if task:
            clusters = CommonModel.get_task_clusters(task.id)
            galaxies = []
            if clusters:
                for cluster in clusters:
                    loc_g = CommonModel.get_galaxy(cluster.galaxy_id)
                    if not loc_g.name in galaxies:
                        galaxies.append(loc_g.name)
                    index = clusters.index(cluster)
                    clusters[index] = cluster.tag
            return {"clusters": clusters, "galaxies": galaxies}
        return {"message": "Case Not found"}, 404

@api.route('/case/<cid>/move_task_up/<tid>', methods=["GET"])
@api.doc(description='Move the task up', params={"cid": "id of a case", "tid": "id of a task"})
class MoveTaskUp(Resource):
    method_decorators = [api_required]
    def get(self, cid, tid):
        case = CommonModel.get_case_template(cid)
        if case:
            task = CommonModel.get_task_template(tid)
            if task:
                TaskModel.change_order(case, task, "true")
                return {"message": "Order changed"}, 200
            return {"message": "Task Not found"}, 404
        return {"message": "Case Not found"}, 404

@api.route('/case/<cid>/move_task_down/<tid>', methods=["GET"])
@api.doc(description='Move the task down', params={"cid": "id of a case", "tid": "id of a task"})
class MoveTaskDown(Resource):
    method_decorators = [api_required]
    def get(self, cid, tid):
        case = CommonModel.get_case_template(cid)
        if case:
            task = CommonModel.get_task_template(tid)
            if task:
                TaskModel.change_order(case, task, "false")
                return {"message": "Order changed"}, 200
            return {"message": "Task Not found"}, 404
        return {"message": "Case Not found"}, 404


###########
# Subtask #
###########

@api.route('/task/<tid>/create_subtask', methods=['POST'])
@api.doc(description='Create a subtask')
class CreateSubtask(Resource):
    method_decorators = [api_required]
    @api.doc(params={
        'description': 'Required. Description of the subtask'
    })
    def post(self, tid):
        task = CommonModel.get_task_template(tid)
        if task:
            if "description" in request.json:
                subtask = TaskModel.create_subtask(tid, request.json["description"])
                if subtask:
                    return {"message": f"Subtask created, id: {subtask.id}", "subtask_id": subtask.id}, 201 
            return {"message": "Need to pass 'description'"}, 400
        return {"message": "Task Not found"}, 404
    
@api.route('/task/<tid>/edit_subtask/<sid>', methods=['POST'])
@api.doc(description='Edit a subtask')
class EditSubtask(Resource):
    method_decorators = [api_required]
    @api.doc(params={
        'description': 'Required. Description of the subtask'
    })
    def post(self, tid, sid):
        task = CommonModel.get_task_template(tid)
        if task:
            if "description" in request.json:
                subtask = TaskModel.edit_subtask(tid, sid, request.json["description"])
                if subtask:
                    return {"message": f"Subtask edited"}, 200 
            return {"message": "Need to pass 'description'"}, 400
        return {"message": "Task Not found"}, 404
    
@api.route('/task/<tid>/list_subtasks', methods=['GET'])
@api.doc(description='List subtasks of a task')
class ListSubtask(Resource):
    method_decorators = [api_required]
    def get(self, tid):
        task = CommonModel.get_task_template(tid)
        if task:
            return {"subtasks": [subtask.to_json() for subtask in task.subtasks]}, 200
        return {"message": "task Not found"}, 404
    
@api.route('/task/<tid>/subtask/<sid>', methods=['GET'])
@api.doc(description='Get a subtask of a task')
class GetSubtask(Resource):
    method_decorators = [api_required]
    def get(self, tid, sid):
        task = CommonModel.get_task_template(tid)
        if task:
            subtask = CommonModel.get_subtask_template(sid)
            if subtask:
                return subtask.to_json()
        return {"message": "task Not found"}, 404
    
@api.route('/task/<tid>/delete_subtask/<sid>', methods=['GET'])
@api.doc(description='Delete a subtask')
class DeleteSubtask(Resource):
    method_decorators = [api_required]
    def get(self, tid, sid):
        task = CommonModel.get_task_template(tid)
        if task:
            if TaskModel.delete_subtask(tid, sid):
                return {"message": "Subtask deleted"}, 200
            return {"message": "Subtask not found"}, 404
        return {"message": "task Not found"}, 404
    


##############
# Urls/Tools #
##############

@api.route('/task/<tid>/create_url_tool', methods=['POST'])
@api.doc(description='Create a Url/Tool')
class CreateUrlTool(Resource):
    method_decorators = [api_required]
    @api.doc(params={
        'name': 'Required. name of the url or tool'
    })
    def post(self, tid):
        task = CommonModel.get_task_template(tid)
        if task:
            if "name" in request.json:
                url_tool = TaskModel.create_url_tool(tid, request.json["name"])
                if url_tool:
                    return {"message": f"Url/Tool created, id: {url_tool.id}", "url_tool_id": url_tool.id}, 201 
            return {"message": "Need to pass 'name'"}, 400
        return {"message": "Task Not found"}, 404
    
@api.route('/<tid>/edit_url_tool/<sid>', methods=['POST'])
@api.doc(description='Edit a Url/Tool')
class EditUrlTool(Resource):
    method_decorators = [api_required]
    @api.doc(params={
        'name': 'Required. name of the url or tool'
    })
    def post(self, tid, sid):
        task = CommonModel.get_task_template(tid)
        if task:
            if "name" in request.json:
                url_tool = TaskModel.edit_url_tool(tid, sid, request.json["name"])
                if url_tool:
                    return {"message": f"Url/Tool edited"}, 200 
            return {"message": "Need to pass 'name'"}, 400
        return {"message": "Task Not found"}, 404
    
@api.route('/<tid>/list_urls_tools', methods=['GET'])
@api.doc(description='List Urls/Tools of a task')
class ListUrlsTools(Resource):
    method_decorators = [api_required]
    def get(self, tid):
        task = CommonModel.get_task_template(tid)
        if task:
            return {"urls_tools": [url_tool.to_json() for url_tool in task.urls_tools]}, 200
        return {"message": "task Not found"}, 404
    
@api.route('/<tid>/url_tool/<utid>', methods=['GET'])
@api.doc(description='Get a Url/Tool of a task')
class GetUrlTool(Resource):
    method_decorators = [api_required]
    def get(self, tid, utid):
        task = CommonModel.get_task_template(tid)
        if task:
            url_tool = TaskModel.get_url_tool_template(utid)
            if url_tool:
                return url_tool.to_json()
        return {"message": "task Not found"}, 404
    
@api.route('/<tid>/delete_url_tool/<utid>', methods=['GET'])
@api.doc(description='Delete a Url/Tool')
class DeleteUrlTool(Resource):
    method_decorators = [api_required]
    def get(self, tid, utid):
        task = CommonModel.get_task_template(tid)
        if task:
            if TaskModel.delete_url_tool(tid, utid):
                return {"message": "Url/Tool deleted"}, 200
            return {"message": "Url/Tool not found"}, 404
        return {"message": "task Not found"}, 404
    