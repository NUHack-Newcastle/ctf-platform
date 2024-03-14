import json
import os
import shutil
import subprocess
import sys
import threading
import uuid

from azure.core.utils import parse_connection_string
from flask import Blueprint, abort, request, current_app as app, Response

from app import CTFPlatformApp
from db import db
from models.orchestration_static import OrchestrationStatic, OrchestrationStaticState
from models.team import Team
from sqlalchemy.orm import scoped_session, sessionmaker

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, BlobSasPermissions, PublicAccess

app: CTFPlatformApp

orchestrator_blueprint = Blueprint('orchestrator', __name__)


@orchestrator_blueprint.route('/')
def orchestrate_index():
    return 'CTF Orchestrator'


@orchestrator_blueprint.route('/orchestrate/static', methods=['POST'])
def orchestrate_static():
    if os.environ.get('CTF_IS_ORCHESTRATOR', 'false') != 'true':
        abort(404)
    team = Team.query.get(request.json.get('team'))
    challenge = app.event.get_challenge(request.json.get('challenge'))
    if not team:
        abort(404)

    print(f"Starting orchestrate for team {team.slug} on challenge {challenge.slug}", file=sys.stderr)

    db_session = db.session
    state = OrchestrationStatic.query.get((team.slug, challenge.slug))
    if not state:
        state.state = OrchestrationStaticState.NOT_STARTED
        db_session.add(state)
        db_session.commit()
    if state.state == OrchestrationStaticState.NOT_STARTED or state.state == OrchestrationStaticState.FAILED:
        state.state = OrchestrationStaticState.STARTED
        db_session.commit()

        script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'orchestrate_static.sh')
        challenge_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'event', 'challenges',
                                      challenge.category.slug, challenge.slug)

        state.state = OrchestrationStaticState.BUILDING
        db_session.commit()

        process = subprocess.Popen([script_path, challenge_path], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env={'FLAG': app.event.flag_manager.generate_flag(challenge, team)})
        stdout, stderr = process.communicate()

        # Check the exit code
        if process.returncode == 0:  # If it succeeded
            # Capture the last line of stdout
            last_line = stdout.decode().splitlines()[-1]
            state.state = OrchestrationStaticState.UPLOADING
            db_session.commit()
            # check if is dir
            if not os.path.isdir(last_line):
                print(f"Error: Script succeeded but {last_line} is not dir", file=sys.stderr)
                print("STDOUT:", stdout.decode(), file=sys.stderr)
                print("STDERR:", stderr.decode(), file=sys.stderr)
                state.state = OrchestrationStaticState.FAILED
                db_session.commit()
                return Response('Build failed', status=500, mimetype='text/plain')
            # check if dir empty
            empty = True
            for root, dirs, files in os.walk(last_line):
                if files:
                    empty = False
            if not empty:
                # upload
                container_name = None
                while True:
                    container_name = str(uuid.uuid4())
                    container_client = app.blob_service_client.get_container_client(container_name)
                    exists = container_client.exists()
                    if not exists:
                        container_client.create_container(public_access=PublicAccess.Container)
                        break
                for root, dirs, files in os.walk(last_line):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        blob_client = app.blob_service_client.get_blob_client(container=container_name,
                                                                              blob=file_path[len(last_line) + 1:])
                        with open(file_path, "rb") as data:
                            blob_client.upload_blob(data)
                state.state = OrchestrationStaticState.COMPLETE
                connstr = parse_connection_string(os.environ.get('AZURE_BLOB_CONNECTION_STRING'))
                state.resources = json.dumps({
                    'type': 'azure_blob_container',
                    'container_name': container_name,
                    'default_endpoints_protocol': connstr['defaultendpointsprotocol'],
                    'account_name': connstr['accountname'],
                    'endpoint_suffix': connstr['endpointsuffix'],
                })
                db_session.commit()
            else:
                state.state = OrchestrationStaticState.COMPLETE
                state.resources = json.dumps({'type': None})
                db_session.commit()
            # delete temp folder
            shutil.rmtree(last_line)
        else:  # If it failed
            # Print stderr and stdout onto the stderr of your program
            print("Error: Script failed with exit code", process.returncode, file=sys.stderr)
            print("STDOUT:", stdout.decode(), file=sys.stderr)
            print("STDERR:", stderr.decode(), file=sys.stderr)
            state.state = OrchestrationStaticState.FAILED
            db_session.commit()
            return Response('Build script failed', status=500, mimetype='text/plain')

    return "Challenge built"
