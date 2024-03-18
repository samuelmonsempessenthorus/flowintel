from flask import url_for

API_KEY = "admin_api_key"

def test_create_case_no_api(client):
    response = client.post("/api/case/create", data={
        'title': "Test Case admin"
    })
    # response = client.get(url_for("account.login"))
    assert response.status_code == 403

def test_create_case(client):
    # response = client.post(url_for("api_case.add_case/"), data={
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test Case admin"}
                        )
    assert response.status_code == 201 and b"Case created, id: 1" in response.data

def test_create_case_empty_title(client):
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": ""}
                        )
    assert response.status_code == 400 and b"Please give a title" in response.data

def test_create_case_no_data(client):
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={}
                        )
    assert response.status_code == 400 and b"Please give data" in response.data

def test_create_case_deadline(client):
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test Case admin", "description": "Test case", "deadline_date": "2023-09-30"}
                        )
    assert response.status_code == 201 and b"Case created, id: 1" in response.data

def test_create_case_wrong_deadline(client):
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test Case admin", "description": "Test case", "deadline_date": "2023/09/30"}
                        )
    assert response.status_code == 400 and b"deadline_date bad format" in response.data

def test_create_case_existing_title(client):
    test_create_case(client)
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test Case admin"}
                        )
    assert response.status_code == 400 and b"Title already exist" in response.data
    

def test_get_all_cases(client):
    response = client.get("/api/case/all", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200

def test_get_case(client):
    test_create_case(client)
    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200

def test_complete_case(client):
    test_create_case(client)
    response = client.get("/api/case/1/complete", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Case 1 completed" in response.data

def test_create_template(client):
    test_create_case(client)
    response = client.post("/api/case/1/create_template", headers={"X-API-KEY": API_KEY},
                           json={"title_template": "Template from case 1 admin"})
    assert response.status_code == 201 and response.json["template_id"] == 1


def test_case_recurring_once(client):
    test_create_case(client)
    response = client.post("/api/case/1/recurring", headers={"X-API-KEY": API_KEY},
                           json={"once": "2023-09-11"})
    assert response.status_code == 200 and b'Recurring changed' in response.data
    
    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["recurring_type"] and response.json["recurring_date"]

def test_case_recurring_daily(client):
    test_create_case(client)
    response = client.post("/api/case/1/recurring", headers={"X-API-KEY": API_KEY},
                           json={"daily": "True"})
    assert response.status_code == 200 and b'Recurring changed' in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["recurring_type"]

def test_case_recurring_weekly(client):
    test_create_case(client)
    response = client.post("/api/case/1/recurring", headers={"X-API-KEY": API_KEY},
                           json={"weekly": "2023-09-09"})
    assert response.status_code == 200 and b'Recurring changed' in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["recurring_type"] and response.json["recurring_date"]

def test_case_recurring_monthly(client):
    test_create_case(client)
    response = client.post("/api/case/1/recurring", headers={"X-API-KEY": API_KEY},
                           json={"monthly": "2023-09-09"})
    assert response.status_code == 200 and b'Recurring changed' in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["recurring_type"] and response.json["recurring_date"]

def test_case_recurring_remove(client):
    test_create_case(client)
    client.post("/api/case/1/recurring", headers={"X-API-KEY": API_KEY},
                           json={"monthly": "2023-09-09"})
    response = client.post("/api/case/1/recurring", headers={"X-API-KEY": API_KEY},
                           json={"remove": "True"})
    assert response.status_code == 200 and b'Recurring changed' in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and not response.json["recurring_type"] and not response.json["recurring_date"]


def test_edit_case(client):
    test_create_case(client)
    response = client.post("/api/case/1/edit", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test edit Case admin"}
                        )
    assert response.status_code == 200 and b"Case 1 edited" in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Test edit Case admin" in response.data

def test_create_edit_empty_title(client):
    test_create_case(client)
    response = client.post("/api/case/1/edit", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": ""}
                        )
    assert response.status_code == 200 and b"Case 1 edited" in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["title"] == "Test Case admin"

def test_create_edit_no_data(client):
    test_create_case(client)
    response = client.post("/api/case/1/edit", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={}
                        )
    assert response.status_code == 400 and b"Please give data" in response.data

    response = client.get("/api/case/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["title"] == "Test Case admin"

def test_edit_case_exist_title(client):
    test_create_case(client)
    response = client.post("/api/case/create", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test Case 2 admin"}
                        )
    response = client.post("/api/case/1/edit", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test Case 2 admin"}
                        )
    assert response.status_code == 400 and b"Title already exist" in response.data

def test_add_org_case(client):
    test_create_case(client)
    response = client.post("/api/case/1/add_org", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"oid": "2"}
                        )
    assert response.status_code == 200 and b"Org added to case 1" in response.data

def test_add_org_case_wrong_org(client):
    test_create_case(client)
    response = client.post("/api/case/1/add_org", 
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"oid": "6"}
                        )
    assert response.status_code == 404


def test_remove_org_case(client):
    test_add_org_case(client)
    response = client.get("/api/case/1/remove_org/2", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Org deleted from case 1" in response.data

def test_get_all_users(client):
    test_create_case(client)
    response = client.get("/api/case/1/get_all_users", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200


def test_delete_case(client):
    test_create_case(client)
    response = client.get("/api/case/1/delete", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Case deleted" in response.data



##########
## TASK ##
##########

def test_create_task(client, flag=True):
    if flag:
        test_create_case(client)
    response = client.post("/api/case/1/create_task",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test task admin"}
                        )
    assert response.status_code == 201 and b"Task created for case id: 1" in response.data

def test_create_task_deadline(client, flag=True):
    if flag:
        test_create_case(client)
    response = client.post("/api/case/1/create_task",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test task admin", "description": "Test", "url": "test", "deadline_date": "2023-09-30"}
                        )
    assert response.status_code == 201 and b"Task created for case id: 1" in response.data

def test_create_task_wrong_deadline(client, flag=True):
    if flag:
        test_create_case(client)
    response = client.post("/api/case/1/create_task",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test task admin", "description": "Test", "url": "test", "deadline_date": "2023/09/30"}
                        )
    assert response.status_code == 400 and b"deadline_date bad format" in response.data

def test_get_all_tasks(client):
    test_create_task(client)
    response = client.get("/api/case/1/tasks", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200

def test_get_task(client):
    test_create_task(client)
    response = client.get("/api/case/1/task/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200


def test_edit_task(client):
    test_create_task(client)
    response = client.post("/api/case/1/task/1/edit",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"title": "Test edit task admin"}
                        )

    assert response.status_code == 200 and b"Task 1 edited" in response.data

    response = client.get("/api/case/1/task/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Test edit task admin" in response.data


def test_complete_task(client):
    test_create_task(client)
    response = client.get("/api/case/1/task/1/complete", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Task 1 completed" in response.data


def test_create_note_task(client):
    test_create_task(client)
    response = client.post("/api/case/1/task/1/modif_note",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"note": "Test super note", "note_id": "-1"}
                        )
    assert response.status_code == 200 and b"Note for task 1 edited" in response.data

def test_modif_note(client):
    test_create_note_task(client)
    response = client.post("/api/case/1/task/1/modif_note",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"note": "Test super note", "note_id": "1"}
                        )
    assert response.status_code == 200 and b"Note for task 1 edited" in response.data

def test_get_all_notes_task(client):
    test_create_task(client)
    response = client.get("/api/case/1/task/1/get_all_notes", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200

def test_get_note_task(client):
    test_create_note_task(client)
    response = client.get("/api/case/1/task/1/get_note?note_id=1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Test super note" in response.data


def test_take_task(client):
    test_create_task(client)
    response = client.get("/api/case/1/take_task/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Task Take" in response.data

def test_remove_assign_task(client):
    test_take_task(client)
    response = client.get("/api/case/1/remove_assignment/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Removed from assignment" in response.data

def test_assign_user_task(client):
    test_add_org_case(client)
    test_create_task(client, False)
    response = client.post("/api/case/1/task/1/assign_users",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"users_id": [2]}
                        )
    assert response.status_code == 200 and b"Users Assigned" in response.data

def test_remove_assign_user_task(client):
    test_assign_user_task(client)
    response = client.post("/api/case/1/task/1/remove_assign_user",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"user_id": "2"}
                        )
    assert response.status_code == 200 and b"User Removed from assignment" in response.data

def test_change_status(client):
    test_create_task(client)
    response = client.post("/api/case/1/task/1/change_status",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"status_id": "2"}
                        )
    assert response.status_code == 200 and b"Status changed" in response.data

def test_list_status(client):
    response = client.get("/api/case/list_status", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and len(response.json) == 6

def test_delete_task(client):
    test_create_task(client)
    response = client.get("/api/case/1/task/1/delete", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Task deleted" in response.data

def test_move_task_up(client):
    test_create_task(client)
    test_create_task(client, flag=False)
    response = client.get("/api/case/1/move_task_up/2", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Order changed" in response.data

    response = client.get("/api/case/1/task/2", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["task"]["case_order_id"] == 1

def test_move_task_down(client):
    test_create_task(client)
    test_create_task(client, flag=False)
    response = client.get("/api/case/1/move_task_down/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Order changed" in response.data

    response = client.get("/api/case/1/task/1", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["task"]["case_order_id"] == 2


def test_get_all_notes(client):
    test_modif_note(client)
    response = client.get("/api/case/1/all_notes", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Test super note" in response.data

def test_modif_case_note(client):
    test_create_case(client)
    response = client.post("/api/case/1/modif_case_note",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"note": "Test super note"}
                        )
    assert response.status_code == 200 and b"Note for Case 1 edited" in response.data

def test_get_case_note(client):
    test_modif_case_note(client)
    response = client.get("/api/case/1/get_note", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and b"Test super note" in response.data

def test_fork_case(client):
    test_create_case(client)
    response = client.post("/api/case/1/fork",
                           content_type='application/json',
                           headers={"X-API-KEY": API_KEY},
                           json={"case_title_fork": "Test fork case"}
                        )
    assert response.status_code == 201

    response = client.get("/api/case/2", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200 and response.json["title"] == "Test fork case"