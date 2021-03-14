from distutils.core import setup
from setuptools import find_packages
#这是一个和根目录相关的安装文件的列表，列表中setup.py更具体)
 
files = ["things/*"]

_package_name = "myQueue"

setup(name = "myQueue",
    version = "1.0.0",
    description = "Queue Server Simulator",
    author = "tcyhost",
    author_email = "tcyhost@buaa.edu.cn",
    url = "",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found recursively.)
    packages=find_packages(
        include=(_package_name, "%s.*" % _package_name)
    ),
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    #package_data = {'package' : files },
    #'runner' is in the root.
    #scripts = ["runner"],
    #long_description = """Really long text here.""" 
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
)