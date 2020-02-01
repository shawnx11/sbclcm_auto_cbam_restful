# Pre-Steps
1. create one user on CBAM for rest api calls
2. setup orchvm, http server, backup server

# v1
1. minimal prototype                    - done

# v2
1. Upload VNF Package                   - done
2. Create, Instantiate                  - done
3. Disable auto_backup, auto_scale      - done
4. Connection                           - done
5. Disconnection                        - done
6. backup                               - done
7. DB restore                           - done
8. Single VM Heal                       - done
9. Multple VM Heal                      - done
10. Scale                               - done
11. Scale Out and In                    - done
12. Terminate                           - done
13. Delete                              - done
14. Change Package Version              - done
15. SU                                  - done
16. Upgrade archive                     - done
17. CSSU                                - done

# v3
1. class re-design                      - done
2. add LcmTestDriver class              - done
3. re-org globals                       - done
4. add TS                               - done

# v4
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

# v5
1. add more TS scenarios                - done
2. 6 DRs scenarios                      - done

# v6
1. media plane support
    - instantiation                     - done
    - backup                            - done
    - dr                                - done
    - scale                             - done
    - restore                           - done
    - heal                              - done
    - issu                              - done
    - nssu                              - done
    - backout                           - done
    - rollback                          - done
2. change to pl043                      - done
3. class re-org                         - done
    - SBCVnf
        - SigVnf
        - MediaVnf
    - SBCVnfLcmTestDriver
        - SigVnfLcmTestDriver
        - MediaVnfLcmTestDriver
4. add class LcmUtils                   - done

# v7
1. add cancel
2. media plane su->cancel->backout
3. media artifact generator
4. use yaml file for configuration      - done
5. load shipping, upload
6. re-org globals                       - done
7. change README to MD format
8. add sbc test suites
9. Sig DB restore from local oam

# TODO
1. data visualization
2. containerlization
3. sig plane support api v3
4. Should it support TS resume?

