SUBROUTINE readfields
  
   USE mod_precdef
   USE mod_param
   USE mod_vel
   
   USE mod_time
   USE mod_grid
   USE mod_name
   USE mod_vel
   USE mod_traj
   USE mod_getfile
   use mod_seed
   use mod_tempsalt
   
   IMPLICIT none
   ! ==========================================================================
   ! === Read velocity, temperature and salinity for ORCA0083 configuration ===
   ! ==========================================================================
   ! Subroutine to read the ocean state from ORCA0083 config
   ! Run each time step
   ! --------------------------------------------------------------------------
   ! The following arrays will be populated:
   !
   ! uflux    - Zonal volume flux (U point)
   ! vflux    - Meridional volume flux (V point)
   !
   ! If run with tempsalt option, the following are also set
   ! tem      - Temperature (T point) 
   ! sal      - Salinity (T point)
   ! rho      - Potential density (T point)
   !
   ! --------------------------------------------------------------------------


   !MODIFIED BY WGL 7/2/2018 - CHANGE A-GRID TO C-GRID DATA
   !MODIFIED BY WGL 7/5/2018 - FIXING i-1/i+1 errors
   !MODIFIED BY WGL 10/17/2018 - Removing old hacks; adapting to c-grid
   
   ! = Loop variables
   INTEGER                                       :: i, j, k ,kk, im, ip
   INTEGER                                       :: jm, jp, imm, ii
   INTEGER                                       :: jmm, jpp, l
   INTEGER                                       :: kbot,ktop
   INTEGER, SAVE                                 :: ntempus=0,ntempusb=0,nread
   ! = Variables used for getfield procedures
   CHARACTER (len=200)                           :: ufilename, udataprefix
   CHARACTER (len=200)                           :: vfilename, vdataprefix
   CHARACTER (len=200)                           :: wfilename, wdataprefix
   REAL(DP), ALLOCATABLE, DIMENSION(:,:)         :: zstot,zstou,zstov,abyst,abysu,abysv
   !REAL(DP), ALLOCATABLE, DIMENSION(:)           :: wdep !cwgl
   REAL(DP), ALLOCATABLE, DIMENSION(:,:,:)       :: xxx
   REAL*4                                      :: dd,hu,hv,uint,vint,zint,hh,h0
  
   LOGICAL                                       :: around
 
!---------------------------------------------------------------   
   !
   ! Allocate variables 
   !
   !alloCondUVW: if(.not. allocated (zstot)) then
   !   allocate ( zstot(imt,jmt),zstou(imt,jmt),zstov(imt,jmt) )
   !   allocate ( xxx(imt,jmt,km))
   !endif alloCondUVW
 
   call datasetswap ! Swap between current and previous step
   call updateClock

   ! Create filename for the current timestep
   udataprefix='umerc_phy_XXXXXX.nc' !u velocities
   write(udataprefix(11:16),'(I6)') int(loopJD)
   ufilename = trim(indatadir)//trim(udataprefix)

   vdataprefix='vmerc_phy_XXXXXX.nc' !v velocities
   write(vdataprefix(11:16),'(I6)') int(loopJD)
   vfilename = trim(indatadir)//trim(vdataprefix)

   wdataprefix='wmerc_phy_XXXXXX.nc' !w velocities
   write(wdataprefix(11:16),'(I6)') int(loopJD)
   wfilename = trim(indatadir)//trim(wdataprefix)
   
   ! Read horizontal velocity fields
   uvel(:,:,km:1:-1) = get3DfieldNC(trim(ufilename), 'vozocrtx')
   vvel(:,:,km:1:-1) = get3DfieldNC(trim(vfilename), 'vomecrty')

   ! Read in vertical velocity fields
   wvel(:,:,km:1:-1) = get3DfieldNC(trim(wfilename), 'vovecrtz')

   !Read in vertical depth fields - debugging
   !allocate (wdep(km))
   !wdep(km:1:-1) = get1DfieldNC(trim(wfilename),'depthw')
   
   ! Change masked values to zero velocity
   where (uvel > 1000000)
      uvel = 0
   end where
   where (vvel > 1000000)
      vvel = 0
   end where
   where (wvel > 1000000)
      wvel = 0
   end where

   !print *,'w @ 31', wvel(310,603,31)
   !print *,'w @ 30', wvel(310,603,30)
   !print *,'w @ 29', wvel(310,603,29)
   
   
   !Debugging... cwgl
   !print *, 'dyu', dyu(ist2,jst2)
   !print *, 'dxv', dxv(ist2,jst2)
   !print *, 'dzu', dzu(ist2,jst2,kst2,:)
   !print *, 'dzv', dzv(ist2,jst2,kst2,:)
   !STOP
   !end cwgl
   
   ! Calculate volume fluxes
   do k = 1, km
      uflux(:,:,k,nsp)  = uvel(:imt,:,k) * dyu(:imt,:) * dzu(:,:,k,nsp)
      vflux(:,:,k,nsp) = vvel(:imt,:,k) * dxv(:imt,:) * dzv(:,:,k,nsp)
      wflux(:,:,k,nsp) = wvel(:imt,:,k)*dxdy(:imt,:jmt)
      
   enddo

   !print *, imt, jmt, km, 'CWGL'
   
   ! Check that volume fluxes are zero below sea floor
   !do i=1,IMT
   !do j=1,JMT
   !do k=1,KM
   !   if(k > kmv(i,j) .and. vflux(i,j,km+1-k,nsp) /= 0.) then
   !      print *,'vflux=',vflux(i,j,km+1-k,nsp),vvel(i,j,k),i,j,k,kmv(i,j),nsp
   !      stop 4966
   !   endif
   !   if(k > kmu(i,j) .and. uflux(i,j,km+1-k,nsp) /= 0.) then
   !      print *,'uflux=',uflux(i,j,km+1-k,nsp),uvel(i,j,k),i,j,k,kmu(i,j),nsp
   !      stop 4967
   !   endif
   !enddo
   !enddo
   !enddo
   

   return
   
end subroutine readfields



