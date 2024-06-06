# joern install

* [reference](https://www.anquanke.com/post/id/236184): Make sure to update the JDK version to 17, `sudo apt-get install openjdk-17-jdk`
* install java17

```bash
sudo apt-get update
sudo apt-get install openjdk-17-jdk
```

* install joern

```bash
git clone https://github.com/ShiftLeftSecurity/joern
cd joern
sudo ./joern-install.sh
```

# How to use?
- Install Python 3.10 and OpenJDK from the Debian packages in Ubuntu (just download the latest version, you can see it by typing 'jdk' in the command line).
- Ensure that **joern** is installed, and that the environment variables for **joern** and **joern-parse** are set up correctly
- Dependencies
    - `pip3 install cpgqls-client`
    - `pip3 install igraph`
    - `pip3 install alive-progress`
- Copy the code files or project folders that need to be parsed into the **testcase** directory
- Note that each folder under the **testcase** directory is a separate project, each project contains only one folder, the folder contains only one file, and the file contains only one function
- Note that all files under the **testcase** directory belong to the project **tmpdir**
- Run `python3 main.py` for slicing processing
- Run `python3 clean` to clear the results obtained under `data_module/database` and `slice_module/slice_result` without deleting files in the `testcase`
- Since the progress bar customizes the output, there should be no print functions in the multiprocessing, otherwise it will get stuck
- Once all the environment configurations are set up, put a small number of projects into the testcase folder, and run from main.py

# Features not well implemented
- Exiting the joern server: Currently, it is killed directly using command line instructions, and requires an official way to exit provided by joern
- joern does not directly generate ddg after importCode, which does not match the official documentation, so it needs to run `run.ossdataflow` again, which needs to be resolved by the official team (already reported to the official team)
- The **success** item in the information returned by the joern server is always **False**, this needs to be resolved by the official team
- The **map** syntax of joern is not powerful enough to achieve everything in one step, so the output json file still needs to be corrected
- Parsing multiple projects multiple times with joern is too inefficient, currently, multiple projects can only be parsed at once
- joern can recognize functions in structs but cannot recognize the definitions of struct variables, and calls to internal functions of struct variables will be pointed to External, which is equivalent to a null pointer
- Function pointers inside a function are recognized as a function, resulting in another function in the AST of the function, the impact of which is currently unknown
- For variable definition statements without assignments, there is no edge connecting the statement natively. The current patch can only add definition statements in backward slicing, but cannot add them in forward slicing
    - Need to assess its importance
    - One feasible solution is to record the local nodes corresponding to each identifier node and add definition statements at each first reference position after slicing is complete
- There is currently no way to directly filter out the attributes we want when generating node attributes
- joern **ref** can only recognize across one **block**, the definition part inside the **for** loop statement is a separate **block**, and the definitions inside cannot be ref-related to the loop control statement, loop variable assignment statement, or identifier nodes in the loop body. joern should not make the definition part inside the **for** loop statement a separate **block**
- The current sorting criteria for DAG are:
    1. Depth
    2. Code order
    - The code order may cause the output order to not be optimal, but there is currently no suitable order (algorithm) that comes to mind
