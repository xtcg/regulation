#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/9/2 11:23
# @File    : file.py
# @Software: PyCharm
from pydantic import BaseModel, HttpUrl


class File(BaseModel):
    url: HttpUrl
    filename: str

