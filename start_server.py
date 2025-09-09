#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动服务器（无自动重载）
"""

import uvicorn
import sys
import os
sys.path.append('.')
from main_official_simple_memory_test import app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8787))
    uvicorn.run(app, host='0.0.0.0', port=port, reload=False)
