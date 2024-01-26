import requests

def get_wikipedia_content(title):
    # 设置MediaWiki API的URL
    api_url = "https://en.wikipedia.org/w/api.php"

    # 设置API请求参数
    params = {
        'action': 'query',
        'format': 'json',
        'titles': title,
        'prop': 'extracts',
        'exintro': True  # 获取页面的简介部分
    }

    # 发送GET请求
    response = requests.get(api_url, params=params)
    
    # 检查请求是否成功
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()

        # 提取页面内容
        pages = data['query']['pages']
        for page_id, page_info in pages.items():
            content = page_info['extract']
            if len(content) > 50:
                return content
            else:
                return " "
    else:
        print(f"Error: {response.status_code}")


# wiki_title = "Python_(programming_language)"
# wiki_title = "Apple_Inc."
# content = get_wikipedia_content(wiki_title)

# print(content)
