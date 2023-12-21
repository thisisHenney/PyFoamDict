## PyFoamDict Usage

- Example
       
    case_path = '/home/test/Desktop/TestCase'

    foam = FoamCase()
    foam.set_case_path(case_path)
    foam.update()

    // Read
    fvSolution = foam.foam_file['fvSolution']
    result = fvSolution.get_dict_list(['solvers'])
    print(result)

    result = fvSolution.get(['solvers', 'cellDisplacement', 'relTol'])
    print(result)

     // Write
    fvSolution.set(['solvers', 'cellDisplacement', 'relTol'], '2')
    fvSolution.save()


- Result

    >> ['p_rgh', '"(U|T|k|epsilon)"', 'cellDisplacement']
    >> 1
