#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动服务器（无自动重载）
"""

import uvicorn
import sys
sys.path.append('.')
from main_official_simple_memory_test import app

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8787, reload=False)
