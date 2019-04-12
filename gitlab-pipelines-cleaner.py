#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gitlab
import sys
import json
import logging
import requests

if __name__ == "__main__":
    print('Initializing gitlab-pipelines-cleaner.')
    config = None
    with open('config.json') as f:
        config = json.load(f)
    if config is not None:
        print('Done.')
        print('Updating logger configuration')
        log_option = {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s'
        }
        if config['log']:
            log_option['filename'] = config['log']
        if config['log_level']:
            log_option['level'] = getattr(logging, str(config['log_level']).upper())
        logging.basicConfig(**log_option)
        print('Done.')
        logging.info('Connecting to GitLab')
        if config['gitlab']['api']:
            gl = None
            if not config['gitlab']['private_token'] and not config['gitlab']['oauth_token']:
                logging.error('You should set at least one auth information in config.json, aborting.')
            elif config['gitlab']['private_token'] and config['gitlab']['oauth_token']:
                logging.error('You should set at most one auth information in config.json, aborting.')
            else:
                if config['gitlab']['private_token']:
                    gl = gitlab.Gitlab(url=config['gitlab']['api'], private_token=config['gitlab']['private_token'])
                elif config['gitlab']['oauth_token']:
                    gl = gitlab.Gitlab(url=config['gitlab']['api'], oauth_token=config['gitlab']['oauth_token'])
                else:
                    gl = None
                if gl is None:
                    logging.error('Cannot create gitlab object, aborting.')
                    sys.exit(1)
            gl.auth()
            logging.info('Done.')
            if len(config['gitlab']['groups']) == 0 and len(config['gitlab']['projects']) == 0:
                logging.info('Going through all groups and projects')
                projects = gl.projects.list()
                for project in projects:
                    pipelines = project.pipelines.list()
                    if len(config['gitlab']['status_autodelete'])>0:
                        pipe = []
                        for pipeline in pipelines:
                            if pipeline.status in config['gitlab']['status_autodelete']:
                                pipe.append(pipeline)
                        pipelines = pipe
                    while len(pipelines) > config['gitlab']['to_keep']:
                        pr_pid = pipelines[len(pipelines)-1]._parent_attrs['project_id']
                        pp_pid = pipelines[len(pipelines)-1].id
                        logging.info('Deleting pipeline %s for project %s' % (pp_pid, gl.projects.get(pr_pid).name))
                        path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], pr_pid, pp_pid)
                        if config['gitlab']['private_token']:
                            r = requests.delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                        elif config['gitlab']['oauth_token']:
                            r = requests.delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                        pipelines.pop(len(pipelines)-1)
            else:
                if len(config['gitlab']['groups'])>0:
                    groups = gl.groups.list()
                    logging.info('Going through user defined group list')
                    for group in groups:
                        if group.name in config['gitlab']['groups']:
                            projects = group.projects.list()
                            pipelines = []
                            if len(config['gitlab']['projects']):
                                logging.info('Going through user defined project list')
                                for project in projects:
                                    if project.name in config['gitlab']['projects']:
                                        pipelines = project.pipelines.list()
                                        if len(config['gitlab']['status_autodelete'])>0:
                                            pipe = []
                                            for pipeline in pipelines:
                                                if pipeline.status in config['gitlab']['status_autodelete']:
                                                    pipe.append(pipeline)
                                            pipelines = pipe
                                        while len(pipelines) > config['gitlab']['to_keep']:
                                            pr_pid = pipelines[len(pipelines)-1]._parent_attrs['project_id']
                                            pp_pid = pipelines[len(pipelines)-1].id
                                            logging.info('Deleting pipeline %s for project %s' % (pp_pid, gl.projects.get(pr_pid).name))
                                            path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], pr_pid, pp_pid)
                                            if config['gitlab']['private_token']:
                                                r = requests.delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                                            elif config['gitlab']['oauth_token']:
                                                r = requests.delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                                            pipelines.pop(len(pipelines)-1)
                            else:
                                logging.info('Going through all the project for the specified group')
                                for project in projects:
                                    pipelines = project.pipelines.list()
                                    if len(config['gitlab']['status_autodelete'])>0:
                                        pipe = []
                                        for pipeline in pipelines:
                                            if pipeline.status in config['gitlab']['status_autodelete']:
                                                pipe.append(pipeline)
                                        pipelines = pipe
                                    while len(pipelines) > config['gitlab']['to_keep']:
                                        pr_pid = pipelines[len(pipelines)-1]._parent_attrs['project_id']
                                        pp_pid = pipelines[len(pipelines)-1].id
                                        logging.info('Deleting pipeline %s for project %s' % (pp_pid, gl.projects.get(pr_pid).name))
                                        path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], pr_pid, pp_pid)
                                        if config['gitlab']['private_token']:
                                            r = requests.delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                                        elif config['gitlab']['oauth_token']:
                                            r = requests.delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                                        pipelines.pop(len(pipelines)-1)
                if len(config['gitlab']['projects'])>0:
                    logging.info('Going through user defined group list')
                    for project in gl.projects.list():
                        if project.name in config['gitlab']['projects']:
                            pipelines = project.pipelines.list()
                            if len(config['gitlab']['status_autodelete'])>0:
                                pipe = []
                                for pipeline in pipelines:
                                    if pipeline.status in config['gitlab']['status_autodelete']:
                                        pipe.append(pipeline)
                                pipelines = pipe
                            while len(pipelines) > config['gitlab']['to_keep']:
                                pr_pid = pipelines[len(pipelines)-1]._parent_attrs['project_id']
                                pp_pid = pipelines[len(pipelines)-1].id
                                logging.info('Deleting pipeline %s for project %s' % (pp_pid, gl.projects.get(pr_pid).name))
                                path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], pr_pid, pp_pid)
                                if config['gitlab']['private_token']:
                                    r = requests.delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                                elif config['gitlab']['oauth_token']:
                                    r = requests.delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                                pipelines.pop(len(pipelines)-1)
        else:
            logging.error('GitLab API is empty, aborting.')
            sys.exit(1)
    else:
        print('Could not load config.json, check if the file is present.')
        print('Aborting.')
        sys.exit(1)
