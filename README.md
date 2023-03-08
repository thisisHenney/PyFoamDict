## Notice 
  - 2023.03.08 (001) : changing var/func name
  

## Update    
  - 2022.04.19 (001) : bug fixed

  - 2022.03.18 (001) : files name changed
 
 

## PyFoamDict
- This code is for reading and writing all OpenFOAM dictionary files with Python language

  pip install PyFoamDict (making...not yet)


- Code Structure

  ./NextLib/PyFoamDict

  ./NextLib/cmn.py


## How to use (in Terminal) - Checking Completed!!

1. $> mkdir Test && cd Test

2. Test$> git clone https://github.com/thisisHenney/NextLib.git

3. Test$> git clone https://github.com/thisisHenney/PyFoamDict.git ./NextLib/PyFoamDict

4. Test$> export PYTHONPATH=${PYTHONPATH}:${PWD}
   
      (depends on your system) Add parent path of "NextLib" folder to PYTHONPATH

5. Test$> python

6. Write the code below in python editor

    from NextLib.PyFoamDict.file import *
  
    path ="/home/test/Desktop/ExampleCase" # OpenFOAM Case file structure
  
  
  
    foam = FOAM_CLASS()
    
    foam.New(path)
  
  
  
    getData = foam.name["control"].Get(["startTime"])
  
    print(getData)
  
  
  
    foam.name["control"].Set(["startTime"], 100)
    
    foam.name["control"].Del(["endTime"])
  
  
    
    foam.name["control"].Save()



## Extended usage
  
  - Get second value
    
    foam.name["fvSolution"].Get(["solvers", "h", "smoother"], 1)
  
  
  - Insert dictionary
    
    foam.name["fvSolution"].Set2(["solvers", "U"])
  
  
  - Delete only data except "{,}"
    
    foam.name["fvSolution"].Reset(["solvers", "U"])
   
  
  - Delete all dictionary except foam header
    
    foam.name["fvSolution"].Clear()
    
    
  
  
  

