#encoding:utf-8
import re
import os
import pathlib

PATH = "./cnsoftbei/"
test_path = "./cnsoftbei/support.huaweicloud.com_devcloud_faq_devcloud_faq_0090.html"
output_path = "qa.tsv"

def parser(PATH):
    f_out = open(output_path, "w", encoding = "UTF-8")
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
            with open(f_path, "r", encoding = "UTF-8") as f:
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
    
if __name__ == "__main__":
    parser(PATH)
    # f = open(test_path, "r", encoding="UTF-8")
    # content = "".join(f.read().split())
    # print(content)
    # a = re.findall('help-detailswebhelp.+?</div>', content)
    # print(a)
    # # b = re.findall(title, "<title>软件开发云中各个区域的数据是否共通？-华为云帮助中心</title>")
    # b = re.findall(title, content)
    # print(b)
    # ans = re.findall(chi_pattern, a[0])
    # print(ans)
    
