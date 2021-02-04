#!/usr/bin/env python3
import requests
import re
import random
import os.path
import os
import zipfile
from fake_useragent import UserAgent
from pymongo import MongoClient
from selenium import webdriver

donwload_path = "/Volumes/Share/"
ua = UserAgent(verify_ssl=False)
urlA = "https://ebanyun.net/?page=1"
base_url = "https://ebanyun.net"

headers = {
	'user-agent':ua.random
}

def get_comic_url_name(url):
	cli = MongoClient("0202") #数据库入口
	db = cli['e搬运']
	col = db[url.split('/')[-1]]
	response = requests.get(url, headers=headers)
	comic_name_url_list = re.findall("<div class=\"gallary-title\">(.*?)</div>", response.text)
	comic_url_list = re.findall("<a href=\"(.*?)\" target=\"_blank\">", response.text)

	new_comic_url_list = []

	for each_comic_url in comic_url_list:
		each_comic_url = base_url + each_comic_url
		new_comic_url_list.append(each_comic_url)
	
	data_list = []
	for i in range(0, len(comic_url_list)):
		data_list.append(comic_name_url_list[i])
		data_list.append(new_comic_url_list[i])
	
	new_data_list = []
	
	for i in range(2, len(data_list), 2):
		each_data_dict = dict(zip(["漫画名", "链接"], data_list[i-2:i]))
		col.insert_one(each_data_dict)
		new_data_list.append(each_data_dict)
		
	return new_data_list

def db_insert():
	cli = MongoClient("192.168.123.201")
	db = cli["e搬运"]
	list1 = [x for x in range(66, 1977)]
	for s in list1:
		urldb = base_url + "/?page=" + str(s)
		col = db[urldb.split('/')[-1]]
		get_comic_url_name(url=urldb)
		print(urldb)
		
def read_db():
	cli = MongoClient("192.168.123.201")
	db = cli["e搬运"]
	col = db['?page='+str(random.randint(2, 70))]
	random_data_dict = dict(col.find_one())
	return random_data_dict
	
random_data_dict = read_db()
def mk_Work_dir():
	os.chdir(donwload_path)
	if not os.path.lexists(os.getcwd() + "/" + random_data_dict["漫画名"]):
		print(os.getcwd() + "/" + random_data_dict["漫画名"])
		os.mkdir(random_data_dict["漫画名"])
	else:
		print("文件夹已创建")
	
def get_comic_image():
	print("爬取的链接为 %s" % random_data_dict["链接"])
	print("爬取的本子名为 %s" % random_data_dict["漫画名"])
	os.chdir(donwload_path + random_data_dict["漫画名"])
	page_url = random_data_dict["链接"] + "?&start=1&count=2000"
	response = requests.get(page_url, headers=headers)
	image_url_list = re.findall("index=\"(.*?)\" src=\"(.*?)\"", response.text)
	for i in range(0, len(image_url_list)):
		image_response = requests.get(image_url_list[i][1], headers=headers)
		print("正在接图 %s" % str(image_url_list[i][1]))
		with open(image_url_list[i][0] + ".jpg", 'wb') as f:
			f.write(image_response.content)
	print("爬取%d张图片" % len(image_url_list))

def compress_dir():
	os.chdir(donwload_path)
	z = zipfile.ZipFile(random_data_dict["漫画名"]+".zip", "w", zipfile.ZIP_DEFLATED)
	file_list = os.listdir(os.getcwd() + "/" +random_data_dict["漫画名"])
	for files in file_list:
		os.chdir(donwload_path + "/" + random_data_dict["漫画名"])
		z.write(files)
	z.close()
	os.chdir(donwload_path)
	print("压缩完成")

def rename_zip_cbz():
	osName = os.name
	if osName == "nt": 
		os.chdir(donwload_path)
		os.system("ren "+"*.zip " + "*.cbz")
	elif osName == "posix":
		os.chdir(donwload_path)
		
	else:
		print("未知系统！")

def get_one_page(pageUrl):
	random_data_dict["链接"] = pageUrl
	response = requests.get(pageUrl, headers=headers)
	random_data_dict["漫画名"] = re.findall("<span property=\"name\">(.*?)</span>",response.text)[0]
	mk_Work_dir()
	get_comic_image()
	compress_dir()
	
'''get_one_page(pageUrl="https://ebanyun.net/comic/1822602-7f9a2a1715/")'''

def getimagesthedouji(pageUrl):
	response = requests.get(pageUrl, headers=headers)
	base_url = "/index.php/categories/"
	base_2_url = "https://thedoujin.com/"
	a_url = base_url + pageUrl.split('/')[-1]
	random_data_dict["漫画名"] = re.findall(" <a href=\"%s\">(.*?)</a> " % a_url, response.text)[0]
	print(random_data_dict["漫画名"])
	page_number_list = [page_number for page_number in range(1, 28)]
	for each_page in page_number_list:
		each_page_url = base_2_url + "index.php/"+ "pages/" + pageUrl.split("/")[-1] + "?Pages_page=" + str(each_page)
		print(each_page_url)
		headers["referer"] = each_page_url
		response = requests.get(each_page_url, headers=headers)
		print(response.text)

def webchrome():
	drive = webdriver.Chrome()
	drive.get("http://mikupi.shenzhuo.vip:11569")
		

webchrome()