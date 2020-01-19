##############################################
Pre-steps:
1. create one user on CBAM for rest api calls
2.

##############################################
v1:
# minimal prototype

##############################################
v2:
# - Upload VNF Package                  - done
# - Create, Instantiate                 - done
# - Disable auto_backup, auto_scale     - done
# - Connection                          - done
# - Disconnection                       - done
# - backup                              - done
# - DB restore                          - done
# - Single VM Heal                      - done
# - Multple VM Heal                     - done
# - Scale                               - done
# - Scale Out and In                    - done
# - Terminate                           - done
# - Delete                              - done
# - Change Package Version              - done
# - SU                                  - done
# - Upgrade archive                     - done
# - CSSU                                - done

##############################################
v3:
To-do:
1. class re-design                      - done
2. add LcmTestDriver class              - done
3. re-org globals                       - done
4. add TS                               - done

##############################################
v4:
To-do:
1. uniform request sender               - done
2. timeout and retries of requests      - done
3. SU To load artifact generation       - done
4. logging, timing                      - done
5. sig artifact generation class        - done
6. add DR                               - done
7. add ScaleOutToMax, ScaleInToInit     - done
8. setup pubkey for backup              - done
9. get initial sc count before scale    - done
10. gen artifacts after sc scale        - done

##############################################
v5:
To-do:
1. add more TS scenarios                - done
2. 6 DRs scenarios                      - done

##############################################
v6:
To-do:
1. media plane support
    - instantiation                     - done
    - backup                            - done
    - dr                                - done
    - scale                             - done
    - restore                           - done
    - heal                              - done
    - issu                              - done
    - nssu                              - done
    - backout
    - rollback                          - done
2. change to pl043                      - done
3. class re-org                         - done
    SBCVnf
        --> SigVnf
        --> MediaVnf
    SBCVnfLcmTestDriver
        --> SigVnfLcmTestDriver
        --> MediaVnfLcmTestDriver
4. media artifact generator
5. use yaml file for configuration
6. load shipping, upload
7. add class LcmUtils

##############################################
v7:
To-do:
1. add cancel
2. data visualization