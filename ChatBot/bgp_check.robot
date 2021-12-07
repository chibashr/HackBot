# Execute a Test Case from Robot
# ================================================

*** Settings ***
Library        ats.robot.pyATSRobot

#*** TestCases ***
# Creating test cases from available keywords.


Initialize
    # select the testbed to use
    use testbed "testbed/routers.yml"
    run testcase "BGP_Neighbors_Established.common_setup"


Verify all BGP Neighbors are established
    run testcase "BGP_Neighbors_Established.BGP_Neighbors_Established"