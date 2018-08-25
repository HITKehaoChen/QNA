from qna import *
from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort
import threading
import sys

qna = QNA()

app = Flask(__name__)


@app.route("/")
def api_root():
    return "Welcome"


@app.route("/listqa")
def listqa():
    return str(qna.list_qa())


@app.route("/additem", methods=["POST"])
def add_item():
    if not request.json or (not "question" in request.json) or (not "answer" in request.json):
        abort(400)
    ret = qna.add_content(request.json["question"], request.json["answer"])
    if ret == 0:
        return jsonify({"status": 201}), 201
    else:
        return jsonify({"status": 400}), 400


@app.route("/deleteitem", methods=["POST"])
def delete_item():
    if not request.json or (not "question" in request.json):
        abort(400)
    ret = qna.delete_content(request.json["question"])
    if ret == 0:
        return jsonify({"status": 201}), 201
    else:
        return jsonify({"status": 400}), 400


@app.route("/query", methods=["POST"])
def query():
    if not request.json or (not "question" in request.json):
        abort(400)
    ret = qna.query(request.json["question"])
    if ret != "ERROR: NOT FOUND":
        return jsonify({"answer": ret}), 201
    else:
        return jsonify({"answer": ret}), 400


@app.route("/update")
def update():
    ret = qna.update()
    if ret == 0:
        return jsonify({"status": 201}), 201
    else:
        return jsonify({"status": 400}), 400


@app.route("/backup", methods=["POST"])
def backup():
    if "path" in request.json:
        ret = qna.backup(request.json["path"])
    else:
        ret = qna.backup()
    if ret == 0:
        return jsonify({"status": 201}), 201
    else:
        return jsonify({"status": 400}), 400


@app.route("/restore", methods=["POST"])
def restore():
    if "path" in request.json:
        ret = qna.restore(request.json["path"])
    else:
        ret = qna.restore()
    if ret == 0:
        return jsonify({"status": 201}), 201
    else:
        return jsonify({"status": 400}), 400


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    api_thread = threading.Thread(target=app.run)
    api_thread.start()
    # app.run()
    while True:
        commands = str(input())
        commands = list(commands.split())
        if commands[0] == "add":
            if len(commands) == 3:
                ret = qna.add_content(commands[1], commands[2])
                if ret == 0:
                    print("ADD COMPLETE")
                else:
                    print("FAILED, ERROR CODE: %d" % ret)
            else:
                print("ERROR: TOO MUCH OR LESS PARAMETERS")
        elif commands[0] == "list":
            print(qna.list_qa())
        elif commands[0] == "del":
            if len(commands) == 2:
                ret = qna.delete_content(commands[1])
                if ret == 0:
                    print("DELETE COMPLETE")
                else:
                    print("FAILED, ERROR CODE: %d" % ret)
            else:
                print("ERROR: TOO MUCH OR LESS PARAMETERS")
        elif commands[0] == "import":
            if len(commands) == 2:
                ret = qna.import_from_path(commands[1])
                if ret == 0:
                    print("IMPORT COMPLETE")
                else:
                    print("FAILED, ERROR CODE: %d" % ret)
            else:
                print("ERROR: TOO MUCH OR LESS PARAMETERS")
        elif commands[0] == "query":
            if len(commands) == 2:
                ret = qna.query(commands[1])
                if ret != "ERROR: NOT FOUND":
                    print("QUERY COMPLETE")
                    print(ret)
                else:
                    print("FAILED, CAN NOT ANSWER THIS QUESTION")
            else:
                print("ERROR: TOO MUCH OR LESS PARAMETERS")
        elif commands[0] == "update":
            ret = qna.update()
            if ret == 0:
                print("UPDATE COMPLETE")
            else:
                print("FAILED, ERROR CODE: %d" % ret)
        elif commands[0] == "quit":
            api_thread.join(1)
            sys.exit(0)
        elif commands[0] == "backup":
            if len(commands) == 1 or len(commands) == 2:
                if len(commands) == 2:
                    ret = qna.backup(commands[1])
                else:
                    ret = qna.backup()
                if ret == 0:
                    print("BACKUP COMPLETE")
                else:
                    print("FAILED, ERROR CODE: %d" % ret)
            else:
                print("ERROR: TOO MUCH OR LESS PARAMETERS")
        elif commands[0] == "restore":
            if len(commands) == 1 or len(commands) == 2:
                if len(commands) == 2:
                    ret = qna.restore(commands[1])
                else:
                    ret = qna.restore()
                if ret == 0:
                    print("RESTORE COMPLETE")
                else:
                    print("FAILED, ERROR CODE: %d" % ret)
            else:
                print("ERROR: TOO MUCH OR LESS PARAMETERS")
        else:
            print("ERROR: NO COMMANDS LIKE " + commands[0])



