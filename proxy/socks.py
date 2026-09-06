import requests

def get_proxy_list():
    #url = "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    #url = "https://github.com/Argh94/Proxy-List/blob/main/SOCKS5.txt"
    url = "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/socks5.txt"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        res_ls = response.text.strip().split('\n')
        res_ls = [item.replace('socks5://', '') for item in res_ls]

        return res_ls
                
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке файла: {e}")

if __name__ == "__main__":
    print(get_proxy_list())
