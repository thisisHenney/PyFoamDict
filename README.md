## PyFoamDict Usage

> test file: ./system/fvSolution


       solvers
       {
           p_rgh
           {
               solver          PCG;
               preconditioner  DIC;
               tolerance       1e-08;
               relTol          0.01;
           }
       
           "(U|T|k|epsilon)"
           {
               solver          PBiCGStab;
               preconditioner  DILU;
               tolerance       1e-07;
               relTol          0.1;
           }
       
           cellDisplacement
           {
               $p_rgh;
               relTol          1;
           }
       }

> Example
       
    case_path = '/home/test/Desktop/TestCase'

    foam = FoamCase()
    foam.set_case_path(case_path)
    foam.update()

    fvSolution = foam.foam_file['fvSolution']
    result = fvSolution.get_dict_list(['solvers'])
    print(result)

    result = fvSolution.get(['solvers', 'cellDisplacement', 'relTol'])
    print(result)

    fvSolution.set(['solvers', 'cellDisplacement', 'relTol'], '2')
    fvSolution.save()


> Result

    >> ['p_rgh', '"(U|T|k|epsilon)"', 'cellDisplacement']
    >> 1


> Result: fvSolution file


       solvers
       {
           p_rgh
           {
               solver          PCG;
               preconditioner  DIC;
               tolerance       1e-08;
               relTol          0.01;
           }
       
           "(U|T|k|epsilon)"
           {
               solver          PBiCGStab;
               preconditioner  DILU;
               tolerance       1e-07;
               relTol          0.1;
           }
       
           cellDisplacement
           {
               $p_rgh;
               relTol          2;   // changed from 1 to 2
           }
       }
