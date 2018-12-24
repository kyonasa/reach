# -*- coding: utf-8 -*-
"""
Created on 2018/9/4 18:24
@author: mengph
reach
"""
import git
from git import Repo
repo=git.Repo("/root")
repo.clone('http://cicd.thinkcloud.lenovo.com/gerrit/nfv/VIMOps/')