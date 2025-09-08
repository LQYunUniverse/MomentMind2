#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单API测试
"""

import requests
import json

def test_simple():
    url = "http://localhost:8787/api/health"
    try:
        response = requests.get(url, timeout=5)
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 测试存储灵感
        url2 = "http://localhost:8787/api/summarize_inspiration"
        data = {"text": "我很喜欢牛油果，在集市上看到的新鲜牛油果"}
        response2 = requests.post(url2, json=data, timeout=10)
        print(f"Store inspiration: {response2.status_code}")
        if response2.status_code == 200:
            print(f"Result: {response2.json()}")
        else:
            print(f"Error: {response2.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()
