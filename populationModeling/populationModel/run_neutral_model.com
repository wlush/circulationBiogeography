#!/bin/bash
	      #this code runs multiple runs of the neutral model
	      #runs shorter runs first to check for problems

	      
	      mpiexec -n 16 python neutralModel_MPI_3_excludePoints_bashInput.py indPac win 3 1
	      wait
	      mpiexec -n 16 python neutralModel_MPI_3_excludePoints_bashInput.py indPac win 15 6
	      wait
	      mpiexec -n 16 python neutralModel_MPI_3_excludePoints_bashInput.py indPac win 45 20
	      wait
	      mpiexec -n 16 python neutralModel_MPI_3_excludePoints_bashInput.py indPac sum 3 1
	      wait
	      mpiexec -n 16 python neutralModel_MPI_3_excludePoints_bashInput.py indPac sum 15 6
	      wait
	      mpiexec -n 16 python neutralModel_MPI_3_excludePoints_bashInput.py indPac sum 45 20
	      wait
