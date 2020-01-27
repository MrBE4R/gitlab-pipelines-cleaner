#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gitlab
import sys
import json
import logging

if __name__ == "__main__":
    print('Initializing gitlab-pipelines-cleaner.')
    config = None
    with open('config.json') as f:
        config = json.load(f)
    if config is not None:
        print('Done.')
        print('Updating logger configuration')
        log_option = {'format': '[%(asctime)s] [%(levelname)s] %(message)s'}
        if config['log']:
            log_option['filename'] = config['log']
        if config['log_level']:
            log_option['level'] = getattr(logging, str(config['log_level']).upper())
        logging.basicConfig(**log_option)
        print('Done.')
        logging.info('Connecting to GitLab')
        if config['gitlab']['api']:
            if len(config['gitlab']['groups']) > 0 and len(config['gitlab']['projects']) > 0:
                logging.error('You should set groups or project in config.json but not both, aborting.')
                sys.exit(1)
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
            try:
                gl.auth()
            except:
                logging.error('Cannot connect to gitlab, aborting.')
                sys.exit(1)
            logging.info('Done.')
            if len(config['gitlab']['groups']) == 0 and len(config['gitlab']['projects']) == 0:
                logging.info('Going through all groups and projects')
                projects = gl.projects.list(all=True)
                for project in projects:
                    logging.info(' Working on project %s' % str(project.name))
                    pipelines_to_delete = {'running': [], 'pending': [], 'success': [], 'failed': [], 'canceled': [], 'skipped': []}
                    pipelines = project.pipelines.list(all=True)
                    if len(config['gitlab']['status_autodelete']) > 0:
                        logging.info('  Auto cleaning pipeline in status : %s' % ', '.join(config['gitlab']['status_autodelete']))
                        for pipeline in pipelines:
                            if pipeline.status in config['gitlab']['status_autodelete']:
                                pipelines_to_delete[pipeline.status].append(pipeline)
                    else:
                        logging.info('  Auto cleaning all pipeline')
                        for pipeline in pipelines:
                            pipelines_to_delete[pipeline.status].append(pipeline)
                    for pipe_status in pipelines_to_delete:
                        while len(pipelines_to_delete[pipe_status]) > config['gitlab']['to_keep']:
                            pr_pid = pipelines_to_delete[pipe_status][len(pipelines_to_delete[pipe_status]) - 1]._parent_attrs['project_id']
                            pp_pid = pipelines_to_delete[pipe_status][len(pipelines_to_delete[pipe_status]) - 1].id
                            logging.info('    Deleting pipeline %s for project %s' % (pp_pid, gl.projects.get(pr_pid).name))
                            path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], pr_pid, pp_pid)
                            if config['gitlab']['private_token']:
                                gl.http_delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                            elif config['gitlab']['oauth_token']:
                                gl.http_delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                            logging.info('      Deleted pipeline %s for project %s' % (pp_pid, gl.projects.get(pr_pid).name))
                            pipelines_to_delete[pipe_status].pop()
            else:
                if len(config['gitlab']['groups']) > 0:
                    logging.info('Going through user defined groups list.')
                    for group in config['gitlab']['groups']:
                        pipelines_to_delete = {'running': [], 'pending': [], 'success': [], 'failed': [], 'canceled': [], 'skipped': []}
                        for g in gl.groups.list(search=group, all=True):
                            if g.name == group:
                                logging.info('  Working on group %s' % group)
                                pipelines_to_delete = {'running': [], 'pending': [], 'success': [], 'failed': [], 'canceled': [], 'skipped': []}
                                for project in group.projects.list(all=True):
                                    logging.info('  Working on project %s.' % project.name)
                                    logging.info('    Project %s found.' % project.name)
                                    pipelines = project.pipelines.list()
                                    if len(config['gitlab']['status_autodelete']) > 0:
                                        logging.info('      Auto cleaning pipeline in status : %s' % ', '.join(config['gitlab']['status_autodelete']))
                                        for pipeline in pipelines:
                                            if pipeline.status in config['gitlab']['status_autodelete']:
                                                pipelines_to_delete[pipeline.status].append(pipeline)
                                    else:
                                        logging.info('  Auto cleaning all pipeline')
                                        for pipeline in pipelines:
                                            pipelines_to_delete[pipeline.status].append(pipeline)
                                    for pipe_status in pipelines_to_delete:
                                        while len(pipelines_to_delete[pipe_status]) > config['gitlab']['to_keep']:
                                            pp_pid = pipelines_to_delete[pipe_status][len(pipelines_to_delete[pipe_status]) - 1].id
                                            logging.info('        Deleting pipeline %s for project %s' % (pp_pid, project.name))
                                            path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], project.id, pp_pid)
                                            if config['gitlab']['private_token']:
                                                gl.http_delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                                            elif config['gitlab']['oauth_token']:
                                                gl.http_delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                                            logging.info('          Deleted pipeline %s for project %s' % (pp_pid, project.name))
                                            pipelines_to_delete[pipe_status].pop()
                                    logging.info('  Done project %s.' % project)
                if len(config['gitlab']['projects']) > 0:
                    logging.info('Going through user defined projects list.')
                    for project in config['gitlab']['projects']:
                        pipelines_to_delete = {'running': [], 'pending': [], 'success': [], 'failed': [], 'canceled': [], 'skipped': []}
                        logging.info('  Working on project %s.' % project)
                        for p in gl.projects.list(search=project, all=True):
                            if p.name == project:
                                logging.info('    Project %s found.' % project)
                                pipelines = p.pipelines.list()
                                if len(config['gitlab']['status_autodelete']) > 0:
                                    logging.info('      Auto cleaning pipeline in status : %s' % ', '.join(config['gitlab']['status_autodelete']))
                                    for pipeline in pipelines:
                                        if pipeline.status in config['gitlab']['status_autodelete']:
                                            pipelines_to_delete[pipeline.status].append(pipeline)
                                else:
                                    logging.info('      Auto cleaning all pipeline')
                                    for pipeline in pipelines:
                                        pipelines_to_delete[pipeline.status].append(pipeline)
                                for pipe_status in pipelines_to_delete:
                                    while len(pipelines_to_delete[pipe_status]) > config['gitlab']['to_keep']:
                                        pp_pid = pipelines_to_delete[pipe_status][len(pipelines_to_delete[pipe_status]) - 1].id
                                        logging.info('        Deleting pipeline %s for project %s' % (pp_pid, p.name))
                                        path = "%s/api/v4/projects/%s/pipelines/%s" % (config['gitlab']['api'], p.id, pp_pid)
                                        if config['gitlab']['private_token']:
                                            gl.http_delete(path, headers={'PRIVATE-TOKEN': config['gitlab']['private_token']})
                                        elif config['gitlab']['oauth_token']:
                                            gl.http_delete(path, headers={'OAUTH-TOKEN': config['gitlab']['oauth_token']})
                                        logging.info('          Deleted pipeline %s for project %s' % (pp_pid, p.name))
                                        pipelines_to_delete[pipe_status].pop()
                        logging.info('  Done project %s.' % project)
        else:
            logging.error('GitLab API is empty, aborting.')
            sys.exit(1)
    else:
        print('Could not load config.json, check if the file is present.')
        print('Aborting.')
        sys.exit(1)
