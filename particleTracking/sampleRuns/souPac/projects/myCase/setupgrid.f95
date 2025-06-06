SUBROUTINE setupgrid
  
   USE mod_precdef
   USE netcdf
   USE mod_param
   USE mod_vel
   
   USE mod_time
   USE mod_grid
   USE mod_name
   USE mod_vel
   USE mod_getfile
   
   IMPLICIT none
   ! =============================================================
   !    ===  Set up the grid for ORCA0083 configuration ===
   ! =============================================================
   ! Subroutine for defining the grid of the ORCA0083 config. 
   ! Run once before the loop starts.
   ! -------------------------------------------------------------
   ! The following arrays will be populated:
   !
   !  dxdy - Horizontal area of cells (T points)
   !  dz   - Thickness of standard level (T point) 
   !  dzt  - Time-invariant thickness of level (T point)
   !  dzu  - Time-invariant thickness of level (U point)
   !  dzv  - Time-invariant thickness of level (V point)
   !  kmt  - Number of levels from surface to seafloor (T point)
   !  kmu  - Number of levels from surface to seafloor (U point)
   !  kmv  - Number of levels from surface to seafloor (V point)
   !
   !NOTE - THIS VERSION OF SETUPGRID USES A COMBINED E3T FILE
   !    please email willlush@gmail.com with any questions
   !
   ! -------------------------------------------------------------
    
   ! === Init local variables for the subroutine ===
   INTEGER                                      :: i ,j ,k, n, kk, ii, &
        &                                               ip, jp, im, jm !! Loop indices
   INTEGER                                      :: kc1, kc2, kc3
   REAL(DP), SAVE, ALLOCATABLE, DIMENSION(:,:)  :: e1t,e2t,dztb0        !! dx, dy [m]
   !cwgl
   INTEGER, ALLOCATABLE, DIMENSION(:,:,:)       :: tmask,umask,vmask
   !cwgl end
   REAL(DP), ALLOCATABLE, DIMENSION(:,:,:,:)    :: tmp4D
   CHARACTER (len=200)                          :: gridFile, maskFile, zgrFile
   
   
   map2D    = [3, 4,  1, 1 ]
   map3D    = [2, 3,  4, 1 ]
   ncTpos   = 1

   !
   ! --- Read dx, dy at T points --- 
   !
   allocate ( e1t(imt,jmt) , e2t(imt,jmt) )
   gridFile = trim(inDataDir)//'fullMesh.nc'
   e1t  = get2DfieldNC(gridFile, 'e1t')
   e2t  = get2DfieldNC(gridFile, 'e2t')
   dxdy(1:imt,1:jmt) = e1t(1:imt,1:jmt) * e2t(1:imt,1:jmt)
   deallocate ( e1t, e2t )
  
   !
   ! --- Read dy at U points and dx at V points --- 
   !
   dyu  = get2DfieldNC(gridFile, 'e2u')
   dxv  = get2DfieldNC(gridFile, 'e1v')
   
   dx   = dxv(imt/2, jmt/2)
   dy   = dyu(imt/2, jmt/2)
     
   !
   ! Read number of valid levels at U, V, T points
   ! as 2D array

   allocate ( kmu(imt,jmt), kmv(imt,jmt) )

   !
   ! Read layer thickness at U, V, T points 
   ! without considering variable volume.
   !
   ! km:1:-1 deals flips data so lowest level input is surface
   ! *first row (0 in python, 1 in fortran) is surface, so this fixes that
   !
   allocate ( dzu(imt,jmt,km,2),dzv(imt,jmt,km,2), dzt0(imt,jmt,km) )
   allocate (dzt(imt,jmt,km,2))

   !new shits - cwgl - for varbottombox
   zgrFile = trim(inDataDir)//'mesh_zgr.nc'
   allocate(dztb0(imt,jmt))
   dztb0 = get2DfieldNC(zgrFile, 'e3t_ps')
   kmt = get2DfieldNC(zgrFile, 'mbathy')
   kmt = kmt+1
   dz(km:1:-1) = get1dfieldNC(zgrFile, 'e3t_0')

   !create dzt0
   do i=1,imt
      do j=1,jmt
         dzt0(i,j,:)=dz(:)
      end do
   end do

   !sets deepest grid box for t, u, v points
   kmu=0 ; kmv=0
   select case (subgrid)
   case(0)! use the full grid - where periodicity is necessary
      do j=1,jmt
         jp=j+1
         if(jp == jmt+1) jp=jmt
         do i=1,imt
            ip=i+1
            if(ip == imt+1) ip=1 !periodicity
            kmu(i,j)=min(kmt(i,j), kmt(ip,j),KM)
            kmv(i,j)=min(kmt(i,j), kmt(i,jp),KM)
         enddo
      enddo
   case(1)! use subgrid
      do j=1,jmt
         jp=j+1
         if(jp == jmt+1) jp=jmt
         do i=1,imt
            ip=i+1
            if(ip == imt+1) ip=imt !periodicity off
            kmu(i,j)=min(kmt(i,j), kmt(ip,j),KM)
            kmv(i,j)=min(kmt(i,j), kmt(i,jp),KM)
         enddo
      enddo
   end select

   !new map3D for velocity fields... cwgl
   !cGrid velocity fieds are (t,z,y,x)
   !map to (x,y,z)
   map3D  =  [2, 3, 4, 1]


   !cwgl edit - z partial step grid - see Madec 2016 - p. 66

   dztb(:,:,1) = dztb0(:,:)
   dztb(:,:,2) = dztb0(:,:)
   
   dzt(:,:,:,1) = dzt0(:,:,:) 
   dzt(:,:,:,2) = dzt0(:,:,:)
   
   dzu = dzt
   dzv = dzt
   
   !quick note on implementation: dzu and dzt are set according to dzt.
   !they are changed into their correct dimensions below when invalid points
   !are set to 0
   !scale factors are applied when making fullMesh.nc
   maskFile = trim(inDataDir)//'Mask.nc'
   allocate(tmask(imt,jmt,km),umask(imt,jmt,km),vmask(imt,jmt,km))
   tmask(:,:,km:1:-1) = get3DfieldNC(maskFile, 'tmask')
   mask = tmask(:,:,km)
   umask(:,:,km:1:-1) = get3DfieldNC(maskFile, 'umask')
   vmask(:,:,km:1:-1) = get3DfieldNC(maskFile, 'vmask')

   
   !
   !Ensure thickness is zero in invalid points
   do n=1,2
      do k=0,km-1
         kc1 = km-k
         !print *, kc1 #do not uncomment, this print statement is evil
         where (km-k < km-kmt(1:imt,1:jmt)) !slight change to implementation in
            dzt(:,:,kc1,n) = 0              !Orca12 setupgrid cwgl - changed to 
         end where
         where (km-k < km-kmu(1:imt,1:jmt))
            dzu(:,:,kc1,n) = 0
         end where
         where (km-k < km-kmv(1:imt,1:jmt))
            dzv(:,:,kc1,n) = 0
         end where
      enddo 
   end do
   
end SUBROUTINE setupgrid
