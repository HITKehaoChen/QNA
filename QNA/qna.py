import http.client, urllib.parse, json, time, requests

PATH = "./cnsoftbei/"
test_path = "./cnsoftbei/support.huaweicloud.com_devcloud_faq_devcloud_faq_0090.html"
output_path = "qa.tsv"


def parser(PATH):
    f_out = open(output_path, "w", encoding="UTF-8")
    title = "<title>.+?</title>"
    chi = u"([\u4e00-\u9fa5|，。；？、：！][\u4e00-\u9fa5|，。；？、：！|a-z|A-Z|0-9]+)"
    chi_pattern = re.compile(chi)
    faq_qa_re = re.compile('<divclass="help-details.+?</div>')
    file_list = os.listdir(PATH)
    # print(file_list)
    cnt = 0
    qa_ret = {}
    for name in file_list:
        if len(name.split("faq")) >= 2:
            f_path = PATH + name
            with open(f_path, "r", encoding="UTF-8") as f:
                # content = f.read()
                # print(f_path)
                content = "".join(f.read().split())
                # print(content)
                a = re.findall('help-detailswebhelp.+?</div>', content)
                # print(a)
                # b = re.findall(title, "<title>软件开发云中各个区域的数据是否共通？-华为云帮助中心</title>")
                b = re.findall(title, content)
                # print(b)
                if len(a) > 0:
                    # print(f_path)
                    ans = list(re.findall(chi_pattern, a[0]))
                    pos = len(ans) - 1
                    for i in range(pos, 0, -1):
                        if ans[i].endswith("?"):
                            pos = i + 1
                            break

                    tit = b[0].split("<title>")[1].split("</title>")[0]
                    pos = 1
                    # print(tit.split("-")[0])
                    # print("".join(ans[pos:]))
                    if "".join(ans[pos:]) != "":
                        f_out.write(tit.split("-")[0] + "\t" + "".join(ans[pos:]) + "\n")
                        qa_ret[tit.split("-")[0]] = "".join(ans[pos:])
                        cnt += 1
                f.close()
    print(cnt)
    f_out.close()
    return qa_ret


class QNA(object):
    def __init__(self):
        self._qa_ = {}
        self.cnt_server = 0
        self._key_ = ""
        self.kb = ""
        with open("config.json", "r") as f:
            content = eval(f.read())
            self._key_ = content["subscriptionKey"]
            self.kb = content["kb"]
            f.close()
        self.host = "https://softbei.azurewebsites.net"
        self.service = "/qnamaker"
        self.method = "/knowledgebases/"

    def list_qa(self):
        try:
            a = sorted(self._qa_, key=lambda d: d[0], reverse=False)
            return a
        except:
            print("list_qa failed")
            return []
            # i = 1
            # for aa in a:
            #     print(str(i)+". "+aa[0]+": "+aa[1])
            #     i += 1

    def add_content(self, question, answer):
        try:
            self._qa_[question] = answer
            return 0
        except:
            print("add item failed")
            return -1

    def delete_content(self, question):
        try:
            self._qa_.pop("question")
            return 0
        except:
            return -2

    def query(self, question):
        try:
            # print(question)
            query_host = "https://softbei.azurewebsites.net/qnamaker/knowledgebases/97ba1f9a-34bf-4b08-8a29-7f76082aeacb/generateAnswer"
            data = json.dumps({
                "question": question,
                "top": 1
            })
            headers = {
                'Authorization': 'EndpointKey ' + self._key_,
                'Content-Type': 'application/json',
                'Content-Length': str(len(data))
            }
            request1 = requests.post(query_host, data=data, headers=headers)
            data = request1.content.decode("utf-8")
            js_dict = json.loads(data)
            # print(js_dict['answers'][0]["answer"])
            return js_dict['answers'][0]["answer"]
        except:
            return "ERROR: NOT FOUND"

    def query_local(self, question):
        try:
            return self._qa_[question]
        except:
            return "ERROR: NOT FOUND"

    def update_kb(self, path, content):
        content = json.dumps(content)
        headers = {
            'Authorization': 'EndpointKey ' + self._key_,
            'Content-Type': 'application/json',
            'Content-Length': str(len(content))
        }
        request1 = requests.post(path, data=content, headers=headers)
        # PATCH /knowledgebases returns an HTTP header named Location that contains a URL
        # to check the status of the operation to create the knowledgebase.
        return request1.content.decode("utf-8")

    def update(self):
        cnt_temp_val = self.cnt_server
        delete_req = {
            'delete': {
                'ids': [i for i in range(cnt_temp_val)]
            }
        }
        content = json.dumps(delete_req)
        result = self.update_kb(self.host + self.service + self.method + self.kb, content)
        time.sleep(3)
        add_req = {
            'add': {
                'qnaList': []
            }

        }
        qnalist = []
        cnt = 0
        for i in self._qa_.keys():
            item = {}
            item["id"] = cnt
            item["answer"] = self._qa_[i]
            item["source"] = "Custom Editorial"
            item["questions"] = [i]
            item["metadata"] = []
            cnt += 1
            qnalist.append(item)
        add_req["add"]["qnaList"] = qnalist
        content = json.dumps(add_req)
        result = self.update_kb(self.host + self.service + self.method + self.kb, content)
        time.sleep(3)
        self.cnt_server = len(self._qa_.keys())
        if result:
            return 0
        else:
            return -6

    def backup(self, backup_file_path="./backup.json"):
        try:
            back = {}
            back["remote_num"] = self.cnt_server
            back["qa"] = self._qa_
            with open(backup_file_path, "w") as f:
                f.write(str(back))
                f.close()
            return 0
        except:
            return -4

    def restore(self, backup_file_path="./backup.json"):
        try:
            with open(backup_file_path, "r") as f:
                content = f.read()
                back = eval(content)
                self._qa_ = back["qa"]
                self.cnt_server = back["remote_num"]
                f.close()
            return 0
        except:
            return -5

    def import_from_path(self, path):
        try:
            qa_ret = parser(path)
            print(qa_ret)
            for i in qa_ret.keys():
                self.add_content(i, qa_ret[i])
            return 0
        except:
            return -8

